"""tbjsync — keep every TheBooleanJulian repo aligned with tbj-brand.

  python -m tbjsync audit  --repos-dir ../clones          # score every repo, change nothing
  python -m tbjsync audit  --repo .                        # one repo (what CI runs)
  python -m tbjsync fix    --repo ../clones/miku-ocr       # apply fixes locally
  python -m tbjsync sync   --wave 0 [--dry-run]            # clone → fix → push branch → open/refresh PR
  python -m tbjsync tokens                                 # regenerate dist/tokens.{css,py,ts}
  python -m tbjsync profile                                # regenerate dist/profile-README.md + projects.json

Stdlib only. `sync` needs the GitHub CLI (gh) authenticated with a token that can
write contents, pull requests and workflows on your repos.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import checks, render
from .config import KIT_ROOT, Brand, build_context, load_manifest

ICON = {"pass": "✓", "fixed": "✎", "fixable": "↻", "manual": "!", "info": "·"}


def _report_row(ctx, findings, changed):
    return {
        "repo": ctx.name,
        "tier": ctx.entry.tier,
        "venture": ctx.entry.venture,
        "wave": ctx.entry.wave,
        "stack": ctx.stack,
        "default_branch": ctx.default_branch,
        "has_dev": ctx.has_dev,
        "score": checks.score(findings),
        "score_after": checks.score(findings, after_fix=True),
        "changed": changed,
        "findings": [f.__dict__ for f in findings],
    }


def _print(row, verbose=False):
    bad = [f for f in row["findings"] if f["status"] not in ("pass", "info")]
    print(f"{row['score']:>3}% → {row['score_after']:>3}%  {row['repo']:<32} {row['tier']:<8} {len(row['changed'])} file(s) to sync")
    for f in row["findings"]:
        if verbose or f["status"] not in ("pass", "info"):
            print(f"       {ICON[f['status']]} {f['check']:<16} {f['message']}")
    return bad


def cmd_audit(args, apply=False):
    brand, manifest = Brand.load(), load_manifest()
    paths = [Path(args.repo)] if args.repo else sorted(p for p in Path(args.repos_dir).iterdir() if (p / ".git").exists())
    rows = []
    for p in paths:
        ctx = build_context(p, brand, manifest)
        if args.repo and (ctx.path / ".tbj.toml").exists() and ctx.name not in manifest:
            # In CI the folder name is the repo name; tier comes from the stamp if the manifest lacks it.
            import tomllib
            stamp = tomllib.loads((ctx.path / ".tbj.toml").read_text())
            ctx.entry.tier = stamp.get("tier", ctx.entry.tier)
            ctx.entry.venture = stamp.get("venture", ctx.entry.venture)
        findings, changed = checks.run(ctx, apply=apply)
        row = _report_row(ctx, findings, changed)
        rows.append(row)
        _print(row, args.verbose)
    if args.json:
        Path(args.json).write_text(json.dumps({"standards": brand.version, "palette": brand.palette, "repos": rows}, indent=1))
    if os.environ.get("GITHUB_STEP_SUMMARY") and args.repo:
        _step_summary(rows[0], brand)
    errors = [f for r in rows for f in r["findings"] if f["level"] == "error" and f["status"] in ("fixable", "manual")]
    if args.fail_on == "error" and brand.enforce == "error" and errors:
        return 1
    return 0


def _step_summary(row, brand):
    lines = [f"### TBJ standards v{brand.version} — {row['score']}%\n", "| | Check | Detail |", "|---|---|---|"]
    for f in row["findings"]:
        lines.append(f"| {ICON[f['status']]} | `{f['check']}` | {f['message'] or f['status']} |")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fh:
        fh.write("\n".join(lines) + "\n")


# ── sync: the bit that updates existing repos ──────────────────────────────
def sh(*cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout.strip()


def pr_body(brand, row):
    done = [f for f in row["findings"] if f["status"] in ("fixed", "fixable")]
    todo = [f for f in row["findings"] if f["status"] == "manual"]
    out = [f"Automated sync to **TheBooleanJulian standards v{brand.version}** "
           f"([tbj-brand](https://github.com/{brand.identity['owner']}/tbj-brand)).\n",
           f"Tier `{row['tier']}` · venture `{row['venture']}` · conformance after merge ≈ {row['score_after']}%\n",
           "### Changed in this PR"]
    out += [f"- `{f['check']}` — {f['message']}" for f in done] or ["- nothing"]
    if todo:
        out += ["", "### Needs you (not automated)"]
        out += [f"- [ ] `{f['check']}` — {f['message']}" for f in todo]
    out += ["", "Only managed blocks (`<!-- tbj:… -->`) and managed files are touched. "
            "Edit the wording centrally in tbj-brand, not here — changes inside blocks are overwritten on the next sync."]
    return "\n".join(out)


def cmd_sync(args):
    brand, manifest = Brand.load(), load_manifest()
    owner = brand.identity["owner"]
    branch = brand.raw["branches"]["sync_branch"]
    targets = [e for e in manifest.values() if e.wave <= args.wave and e.tier != "external"]
    if args.only:
        targets = [e for e in targets if e.name in args.only]
    work = Path(tempfile.mkdtemp(prefix="tbjsync-"))
    rows, failures = [], []
    for e in targets:
        try:
            meta = json.loads(sh("gh", "repo", "view", f"{owner}/{e.name}", "--json", "defaultBranchRef,isArchived,isEmpty"))
            if meta.get("isArchived") or meta.get("isEmpty"):
                print(f"skip {e.name}: {'archived' if meta.get('isArchived') else 'empty'}")
                continue
            default = meta["defaultBranchRef"]["name"]
            dest = work / e.name
            sh("gh", "repo", "clone", f"{owner}/{e.name}", str(dest), "--", "--depth", "50", "--no-single-branch")
            has_dev = bool(sh("git", "ls-remote", "--heads", "origin", "dev", cwd=dest, check=False))
            base = "dev" if has_dev and brand.raw["branches"]["prefer_base"] == "dev" else default
            sh("git", "checkout", "-B", branch, f"origin/{base}", cwd=dest)
            ctx = build_context(dest, brand, manifest, default_branch=default, has_dev=has_dev)
            findings, changed = checks.run(ctx, apply=not args.dry_run)
            row = _report_row(ctx, findings, changed)
            row["base"] = base
            rows.append(row)
            _print(row)
            if args.dry_run or not changed:
                continue
            sh("git", "add", "--", *changed, cwd=dest)
            sh("git", "-c", "user.name=tbj-sync[bot]", "-c", f"user.email={os.environ.get('TBJ_BOT_EMAIL', 'tbj-sync@users.noreply.github.com')}",
               "commit", "-m", f"chore(brand): sync TBJ standards v{brand.version}", cwd=dest)
            sh("git", "push", "--force", "origin", branch, cwd=dest)
            existing = sh("gh", "pr", "list", "--repo", f"{owner}/{e.name}", "--head", branch, "--state", "open",
                          "--json", "number", "--jq", ".[0].number", check=False)
            body = pr_body(brand, row)
            if existing:
                sh("gh", "pr", "edit", existing, "--repo", f"{owner}/{e.name}", "--body", body)
                print(f"       ↻ updated PR #{existing}")
            else:
                url = sh("gh", "pr", "create", "--repo", f"{owner}/{e.name}", "--base", base, "--head", branch,
                         "--title", f"chore(brand): sync TBJ standards v{brand.version}", "--body", body)
                print(f"       ＋ {url}")
        except Exception as exc:
            failures.append((e.name, str(exc)))
            print(f"FAIL {e.name}: {exc}", file=sys.stderr)
    shutil.rmtree(work, ignore_errors=True)
    if args.json:
        Path(args.json).write_text(json.dumps({"standards": brand.version, "palette": brand.palette, "repos": rows}, indent=1))
    if failures:
        print(f"\n{len(failures)} repo(s) failed: " + ", ".join(n for n, _ in failures), file=sys.stderr)
        return 1
    return 0


# ── generated assets ────────────────────────────────────────────────────────
def cmd_tokens(args):
    brand = Brand.load()
    out = KIT_ROOT / "dist"
    out.mkdir(exist_ok=True)
    (out / "tokens.css").write_text(render.tokens_css(brand))
    (out / "tokens.py").write_text(render.tokens_py(brand))
    (out / "tokens.ts").write_text(render.tokens_ts(brand))
    print(f"wrote dist/tokens.css, tokens.py, tokens.ts from tokens/{brand.palette}.json")
    return 0


def cmd_profile(args):
    """Profile README for github.com/TheBooleanJulian + projects.json for thebooleanjulian.dev."""
    brand, manifest = Brand.load(), load_manifest()
    owner, ident = brand.identity["owner"], brand.identity
    shown = [e for e in manifest.values() if e.tier in ("product", "tool", "themed")]
    groups = {}
    for e in shown:
        key = {"accurova": "Accurova", "upteach": "Upteach", "fan": "Fan & creative"}.get(e.venture)
        if not key:
            key = {"product": "Products", "tool": "Tools & bots", "themed": "Games & experiments"}[e.tier]
        groups.setdefault(key, []).append(e)
    order = ["Products", "Accurova", "Upteach", "Tools & bots", "Games & experiments", "Fan & creative"]
    lines = [f"### {ident['name']}", "", ident["tagline"], "",
             f"[![{ident['domain']}]({render.shield('site', ident['domain'], brand.badge_hex)})]({ident['site']})", ""]
    for g in order:
        if g not in groups:
            continue
        lines += [f"#### {g}", "", "| Project | What it is |", "|---|---|"]
        for e in sorted(groups[g], key=lambda x: x.name.lower()):
            lines.append(f"| [{e.name}](https://github.com/{owner}/{e.name}) | {e.description or ''} |")
        lines.append("")
    lines += ["---", "", f"<sub>Generated by tbj-brand v{brand.version} from repos.toml</sub>"]
    out = KIT_ROOT / "dist"
    out.mkdir(exist_ok=True)
    (out / "profile-README.md").write_text("\n".join(lines) + "\n")
    projects = [{"name": e.name, "tier": e.tier, "venture": e.venture, "description": e.description,
                 "repo": f"https://github.com/{owner}/{e.name}", "homepage": e.homepage} for e in shown]
    (out / "projects.json").write_text(json.dumps(projects, indent=1))
    print(f"wrote dist/profile-README.md and dist/projects.json ({len(shown)} projects)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tbjsync", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("audit", "fix"):
        p = sub.add_parser(name)
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--repo")
        g.add_argument("--repos-dir")
        p.add_argument("--json")
        p.add_argument("--fail-on", choices=["error", "never"], default="error")
        p.add_argument("-v", "--verbose", action="store_true")
    p = sub.add_parser("sync")
    p.add_argument("--wave", type=int, default=0)
    p.add_argument("--only", nargs="*")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json")
    sub.add_parser("tokens")
    sub.add_parser("profile")
    a = ap.parse_args(argv)
    if a.cmd == "audit":
        return cmd_audit(a)
    if a.cmd == "fix":
        return cmd_audit(a, apply=True)
    return {"sync": cmd_sync, "tokens": cmd_tokens, "profile": cmd_profile}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
