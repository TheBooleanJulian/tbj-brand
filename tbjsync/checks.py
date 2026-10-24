"""Conformance checks. Each check inspects a repo and either passes, fixes the
drift (fix mode), or reports something a human must decide.

Rules of thumb baked in here:
  * Only managed blocks and fully-managed files are ever rewritten.
  * Anything with legal or deployment consequences (relicensing, renaming the
    default branch, Zeabur cut-over) is reported, never auto-applied.
"""
from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import blocks, render
from .config import RepoContext

PASS, FIXED, FIXABLE, MANUAL, INFO = "pass", "fixed", "fixable", "manual", "info"


@dataclass
class Finding:
    check: str
    level: str          # error | warn | info
    status: str         # pass | fixed | fixable | manual | info
    message: str = ""
    files: list[str] = field(default_factory=list)


class Workspace:
    """Reads/writes against the repo; in dry mode writes are recorded, not applied."""

    def __init__(self, ctx: RepoContext, apply: bool):
        self.ctx, self.apply = ctx, apply
        self.writes: dict[str, str] = {}
        rp = ctx.readme_path
        self.readme_rel = rp.name if rp else "README.md"
        self.readme = rp.read_text(encoding="utf-8", errors="replace") if rp else None
        self._readme_orig = self.readme

    def exists(self, rel: str) -> bool:
        return rel in self.writes or (self.ctx.path / rel).exists()

    def read(self, rel: str) -> str | None:
        if rel in self.writes:
            return self.writes[rel]
        p = self.ctx.path / rel
        return p.read_text(encoding="utf-8", errors="replace") if p.exists() else None

    def write(self, rel: str, content: str) -> None:
        self.writes[rel] = content

    def flush(self) -> list[str]:
        if self.readme is not None and self.readme != self._readme_orig:
            self.writes[self.readme_rel] = self.readme
        changed = []
        for rel, content in self.writes.items():
            p = self.ctx.path / rel
            old = p.read_text(encoding="utf-8", errors="replace") if p.exists() else None
            if old == content:
                continue
            changed.append(rel)
            if self.apply:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
        return changed


CheckFn = Callable[[RepoContext, Workspace], Finding]
REGISTRY: dict[str, tuple[str, CheckFn]] = {}


def check(cid: str, title: str):
    def deco(fn: CheckFn) -> CheckFn:
        REGISTRY[cid] = (title, fn)
        return fn
    return deco


def _fixed(cid, level, ws, msg, files=()):
    return Finding(cid, level, FIXED if ws.apply else FIXABLE, msg, list(files))


# ── Repo identity ───────────────────────────────────────────────────────────
@check("marker", "Standards stamp (.tbj.toml)")
def c_marker(ctx, ws):
    want = render.marker(ctx)
    have = ws.read(".tbj.toml")
    if have == want:
        return Finding("marker", "info", PASS)
    ws.write(".tbj.toml", want)
    m = re.search(r'standards\s*=\s*"([^"]+)"', have or "")
    msg = f"stamp {m.group(1)} → {ctx.brand.version}" if m else f"add stamp v{ctx.brand.version}"
    return _fixed("marker", "info", ws, msg, [".tbj.toml"])


# ── README ──────────────────────────────────────────────────────────────────
@check("readme", "README exists")
def c_readme(ctx, ws):
    if ws.readme is not None and ws.readme.strip():
        return Finding("readme", "error", PASS)
    ws.readme = render.readme_skeleton(ctx)
    ws.readme_rel = "README.md"
    return _fixed("readme", "error", ws, "no README — skeleton created (needs your content)", ["README.md"])


@check("badges", "Brand badge row (managed block)")
def c_badges(ctx, ws):
    if ws.readme is None:
        return Finding("badges", "warn", MANUAL, "no README")
    body = render.badges(ctx)
    text = ws.readme
    if blocks.has(text, "badges"):
        if blocks.get(text, "badges") == body:
            cleaned = blocks.remove_license_badges(text)
            if cleaned == text:
                return Finding("badges", "warn", PASS)
            ws.readme = cleaned
            return _fixed("badges", "warn", ws, "removed duplicate hand-written licence badge")
        ws.readme = blocks.replace(text, "badges", body)
        return _fixed("badges", "warn", ws, "badge row updated")
    text = blocks.remove_license_badges(text)
    at = blocks.header_insert_point(text)
    block = "\n" + blocks.wrap("badges", body) + "\n"
    ws.readme = text[:at] + block + ("\n" if not text[at:].startswith("\n") else "") + text[at:]
    return _fixed("badges", "warn", ws, "badge row added under the title")


@check("footer", "Standard footer (managed block)")
def c_footer(ctx, ws):
    if ws.readme is None:
        return Finding("footer", "error", MANUAL, "no README")
    body = render.footer(ctx)
    text = ws.readme
    if blocks.has(text, "footer"):
        if blocks.get(text, "footer") == body:
            return Finding("footer", "error", PASS)
        ws.readme = blocks.replace(text, "footer", body)
        return _fixed("footer", "error", ws, "footer updated to current wording")
    text, migrated = blocks.strip_legacy_footer(text)
    ws.readme = text.rstrip() + "\n\n" + blocks.wrap("footer", body) + "\n"
    return _fixed("footer", "error", ws, "legacy footer converted" if migrated else "footer added")


@check("license_section", "License section (managed block)")
def c_license_section(ctx, ws):
    if ws.readme is None:
        return Finding("license_section", "warn", MANUAL, "no README")
    body = render.license_section(ctx)
    if body is None:
        return Finding("license_section", "info", PASS, "licence policy is 'keep'")
    text = ws.readme
    if blocks.has(text, "license"):
        if blocks.get(text, "license") == body:
            return Finding("license_section", "warn", PASS)
        ws.readme = blocks.replace(text, "license", body)
        return _fixed("license_section", "warn", ws, "licence section updated")
    span = blocks.find_section(text, r"licen[cs]e")
    block = blocks.wrap("license", body)
    if span:
        a, b = span
        ws.readme = text[:a] + block + "\n\n" + text[b:].lstrip("\n")
        return _fixed("license_section", "warn", ws, "licence section converted to managed block")
    m = re.search(r"<!--\s*tbj:footer:start", text)
    if m:
        ws.readme = text[: m.start()].rstrip() + "\n\n" + block + "\n\n" + text[m.start():]
    else:
        ws.readme = text.rstrip() + "\n\n" + block + "\n"
    return _fixed("license_section", "warn", ws, "licence section added")


ALIASES = {
    "quick start": ["quick start", "quickstart", "setup and quick start", "getting started", "setup", "installation", "install", "run", "usage", "local development"],
    "status and roadmap": ["status and roadmap", "roadmap", "future roadmap", "status"],
    "deployment": ["deployment", "deploy", "deploy to zeabur", "deploying", "hosting"],
    "tech stack": ["tech stack", "stack", "built with", "architecture"],
    "what it does": ["what it does", "overview", "about", "how it works"],
    "configuration": ["configuration", "config", "environment variables", "env"],
    "changelog": ["changelog", "versioning", "release notes", "version history"],
}


@check("sections", "Canonical README sections")
def c_sections(ctx, ws):
    if ws.readme is None:
        return Finding("sections", "warn", MANUAL, "no README")
    present = {blocks.normalise_heading(h) for h in blocks.headings(ws.readme)}
    lic = blocks.get(ws.readme, "license")
    if lic:
        present |= {blocks.normalise_heading(h) for h in blocks.headings(lic)}
    optional = set(ctx.brand.raw["readme"].get("optional", {}).get(ctx.entry.tier, []))
    missing = []
    for s in ctx.brand.raw["readme"]["sections"]:
        if s in optional:
            continue
        key = blocks.normalise_heading(s)
        names = ALIASES.get(key, [key])
        if not any(n in present for n in names):
            missing.append(s)
    if not missing:
        return Finding("sections", "warn", PASS)
    return Finding("sections", "warn", MANUAL, "missing: " + ", ".join(missing))


@check("archived_banner", "Archived banner (managed block)")
def c_archived(ctx, ws):
    if ws.readme is None:
        ws.readme = render.readme_skeleton(ctx)
        ws.readme_rel = "README.md"
    body = render.archived_banner(ctx)
    text = ws.readme
    if blocks.has(text, "archived"):
        if blocks.get(text, "archived") == body:
            return Finding("archived_banner", "warn", PASS)
        ws.readme = blocks.replace(text, "archived", body)
        return _fixed("archived_banner", "warn", ws, "banner updated")
    at = blocks.header_insert_point(text)
    lead = "\n" if at else ""
    ws.readme = text[:at] + lead + blocks.wrap("archived", body) + "\n\n" + text[at:].lstrip("\n")
    return _fixed("archived_banner", "warn", ws, "archived banner added — then archive the repo on GitHub")


# ── Licence files ───────────────────────────────────────────────────────────
def _license_kind(text: str | None) -> str:
    if not text:
        return "none"
    head = text[:600]
    if "GNU AFFERO" in head:
        return "agpl"
    if "GNU Affero General Public License" in text[:1500]:
        return "agpl-notice"  # short notice only — same licence, but the full text must ship
    if "MIT License" in head or "Permission is hereby granted, free of charge" in text[:1500]:
        return "mit"
    if "Apache License" in head:
        return "apache"
    if "GNU GENERAL PUBLIC" in head:
        return "gpl"
    return "other"


@check("license_files", "Licence files match policy")
def c_license_files(ctx, ws):
    policy = ctx.license_policy
    if policy == "keep":
        return Finding("license_files", "error", PASS, "policy 'keep'")
    want = {"dual-agpl": "agpl", "mit": "mit"}[policy]
    have = _license_kind(ws.read("LICENSE") or ws.read("LICENSE.md") or ws.read("LICENSE.txt"))
    if have == "agpl-notice" and want == "agpl":
        have = "none"  # upgrade notice → full text; not a relicense
    changed = []
    if have not in ("none", want) and not ctx.entry.relicense:
        return Finding("license_files", "error", MANUAL,
                       f"LICENSE is {have.upper()} but policy is {policy}. Relicensing is your call: "
                       f"set license = \"{ 'mit' if have == 'mit' else 'keep'}\" in repos.toml to accept it, "
                       f"or relicense = true to let sync replace it.")
    if have != want:
        if want == "agpl":
            ws.write("LICENSE", render.agpl_text())
        else:
            ws.write("LICENSE", render.mit_text(ctx, _dt.date.today().year))
        changed.append("LICENSE")
    if policy == "dual-agpl" and not ws.exists("COMMERCIAL-LICENSE.md"):
        ws.write("COMMERCIAL-LICENSE.md", render.commercial_license(ctx))
        changed.append("COMMERCIAL-LICENSE.md")
    if not changed:
        return Finding("license_files", "error", PASS)
    return _fixed("license_files", "error", ws, "added " + ", ".join(changed), changed)


@check("fork_license", "Fork licence integrity")
def c_fork_license(ctx, ws):
    lic = _license_kind(ws.read("LICENSE"))
    has_commercial = ws.exists("COMMERCIAL-LICENSE.md")
    if lic == "agpl" and has_commercial:
        return Finding("fork_license", "error", MANUAL,
                       "fork carries AGPLv3 + commercial terms, but you can only dual-license code you own "
                       "outright. Restore the upstream licence and credit the original author, or mark it as "
                       "a rewrite in repos.toml (tier = \"tool\") if no upstream code remains.")
    return Finding("fork_license", "info", PASS, "untouched (external)")


# ── Hygiene files ───────────────────────────────────────────────────────────
@check("editorconfig", ".editorconfig")
def c_editorconfig(ctx, ws):
    want = render.editorconfig()
    if ws.read(".editorconfig") == want:
        return Finding("editorconfig", "info", PASS)
    ws.write(".editorconfig", want)
    return _fixed("editorconfig", "info", ws, "written", [".editorconfig"])


@check("gitignore", ".gitignore")
def c_gitignore(ctx, ws):
    if ws.exists(".gitignore"):
        return Finding("gitignore", "warn", PASS)
    ws.write(".gitignore", render.gitignore(ctx.stack))
    return _fixed("gitignore", "warn", ws, "seeded for " + (", ".join(ctx.stack) or "base"), [".gitignore"])


@check("ci", "TBJ workflow (conformance + stack CI)")
def c_ci(ctx, ws):
    want = render.workflow(ctx)
    rel = ".github/workflows/tbj.yml"
    if ws.read(rel) == want:
        return Finding("ci", "warn", PASS)
    ws.write(rel, want)
    return _fixed("ci", "warn", ws, "workflow written", [rel])


# ── Git / hosting — reported, never auto-changed ────────────────────────────
@check("branch_main", "Default branch is main")
def c_branch_main(ctx, ws):
    if ctx.default_branch in ("main", ""):
        return Finding("branch_main", "warn", PASS)
    return Finding("branch_main", "warn", MANUAL,
                   f"default branch is '{ctx.default_branch}'. Rename when convenient: "
                   f"gh api -X POST repos/{ctx.brand.identity['owner']}/{ctx.name}/branches/{ctx.default_branch}/rename "
                   f"-f new_name=main (re-point any deploy hooks first)")


@check("branch_dev", "dev branch exists (feature → dev → main)")
def c_branch_dev(ctx, ws):
    if ctx.has_dev:
        return Finding("branch_dev", "info", PASS)
    return Finding("branch_dev", "info", MANUAL, "no dev branch")


@check("zeabur", "Zeabur references (migration tracker)")
def c_zeabur(ctx, ws):
    hits = []
    for p in ctx.files:
        if p.suffix.lower() in (".md", ".py", ".js", ".ts", ".json", ".toml", ".yml", ".yaml", ".env", ".example") or p.name.lower().startswith("zbpack"):
            try:
                if p.stat().st_size < 300_000 and "zeabur" in p.read_text(errors="ignore").lower():
                    hits.append(ctx.rel(p))
            except OSError:
                pass
    if not hits:
        return Finding("zeabur", "info", PASS)
    return Finding("zeabur", "warn", MANUAL, f"{len(hits)} file(s) still reference Zeabur", hits[:8])


# ── UI tokens ───────────────────────────────────────────────────────────────
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
FONT = re.compile(r"font-family\s*:\s*['\"]?([A-Za-z][\w \-]+)|family=([A-Za-z+]+)")


@check("ui_tokens", "Brand tokens in UI")
def c_ui_tokens(ctx, ws):
    if "web" not in ctx.stack:
        return Finding("ui_tokens", "info", PASS, "no web UI")
    import json
    tok = json.loads(ctx.brand.tokens_path().read_text())
    brand_hex = set()
    for t in tok["color"]["tokens"]:
        v = t["value"]
        if isinstance(v, dict):
            brand_hex |= {x.upper() for x in v.values() if isinstance(x, str) and x.startswith("#")}
    fams = " ".join(tok.get("type", {}).get("families", {}).values())
    brand_fonts = {f.strip().strip('"') for f in re.findall(r'"([^"]+)"', fams)}
    off_hex, off_fonts, uses_tokens = set(), set(), False
    for p in ctx.files:
        if p.suffix.lower() not in (".css", ".html", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte"):
            continue
        try:
            if p.stat().st_size > 400_000:
                continue
            s = p.read_text(errors="ignore")
        except OSError:
            continue
        if "tbj-brand" in s or "brand/tokens.css" in s:
            uses_tokens = True
        off_hex |= {h.upper() for h in HEX.findall(s)} - brand_hex - {"#FFFFFF", "#000000"}
        for a, b in FONT.findall(s):
            f = (a or b).replace("+", " ").strip()
            if f and f not in brand_fonts and f.lower() not in {"inherit", "monospace", "sans serif", "sans-serif", "system-ui", "serif", "var"}:
                off_fonts.add(f)
    # Keep a vendored copy current so adoption is one <link> away.
    want = render.tokens_css(ctx.brand)
    vend = "brand/tokens.css"
    vendored_ok = ws.read(vend) == want
    if not vendored_ok:
        ws.write(vend, want)
    detail = []
    if not uses_tokens:
        detail.append("UI doesn't load brand/tokens.css yet")
    if off_hex:
        detail.append(f"{len(off_hex)} off-palette colours")
    if off_fonts:
        detail.append("off-brand fonts: " + ", ".join(sorted(off_fonts)[:5]))
    if not detail:
        return Finding("ui_tokens", "warn", PASS if vendored_ok else (FIXED if ws.apply else FIXABLE),
                       "" if vendored_ok else "tokens.css refreshed", [] if vendored_ok else [vend])
    msg = "; ".join(detail) + ("" if vendored_ok else " (tokens.css vendored so you can switch)")
    return Finding("ui_tokens", "warn", MANUAL, msg, [] if vendored_ok else [vend])


# ── Runner ──────────────────────────────────────────────────────────────────
def git_has_commits(ctx: RepoContext) -> bool:
    from .config import git
    if not (ctx.path / ".git").exists():
        return True  # plain folder (e.g. CI artifact) — assume real content
    return bool(git(ctx.path, "rev-parse", "--verify", "-q", "HEAD"))


def run(ctx: RepoContext, apply: bool = False, only: list[str] | None = None) -> tuple[list[Finding], list[str]]:
    if not ctx.files or not git_has_commits(ctx):
        return [Finding("empty", "warn", MANUAL, "empty repository — push a first commit or delete it")], []
    tier = ctx.brand.tier(ctx.entry.tier)
    ids = [c for c in tier["checks"] if c not in ctx.entry.skip and (not only or c in only)]
    # README must exist before block checks; footer before licence so the licence lands above it.
    order = ["marker", "readme", "archived_banner", "badges", "footer", "license_section", "sections"]
    ids.sort(key=lambda c: order.index(c) if c in order else len(order))
    ws = Workspace(ctx, apply)
    findings = []
    for cid in ids:
        title, fn = REGISTRY[cid]
        try:
            findings.append(fn(ctx, ws))
        except Exception as exc:  # a broken check must never take the whole fleet down
            findings.append(Finding(cid, "warn", MANUAL, f"check crashed: {exc!r}"))
    changed = ws.flush()
    return findings, changed


def score(findings: list[Finding], after_fix: bool = False) -> int:
    """0–100 conformance. after_fix=True projects the score once auto-fixes merge."""
    weights = {"error": 3, "warn": 2, "info": 1}
    ok = {PASS, FIXED, INFO} | ({FIXABLE} if after_fix else set())
    total = sum(weights[f.level] for f in findings) or 1
    good = sum(weights[f.level] for f in findings if f.status in ok)
    return round(100 * good / total)
