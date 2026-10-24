"""Render managed block bodies and whole managed files from brand.toml."""
from __future__ import annotations

import json
from pathlib import Path
from string import Template
from urllib.parse import quote

from .config import Brand, RepoContext

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

LICENSE_LABEL = {
    "dual-agpl": "AGPLv3 / Commercial",
    "mit": "MIT",
}


def shield(label: str, message: str, color: str) -> str:
    def esc(s: str) -> str:
        return quote(s.replace("-", "--").replace("_", "__"), safe="")
    return f"https://img.shields.io/badge/{esc(label)}-{esc(message)}-{color}"


def badges(ctx: RepoContext) -> str:
    b = ctx.brand
    color = b.badge_hex
    venture = b.venture(ctx.entry.venture)
    lines = []
    lic = LICENSE_LABEL.get(ctx.license_policy)
    if lic:
        lines.append(f"[![License]({shield('license', lic, color)})](LICENSE)")
    lines.append(f"[![{b.identity['domain']}]({shield('by', b.identity['domain'], '05060D')})]({b.identity['site']})")
    if ctx.entry.venture not in ("tbj", "fan"):
        lines.append(f"[![{venture['label']}]({shield('part of', venture['label'], color)})]({venture['url']})")
    if ctx.entry.tier == "archive":
        lines.append(f"![Status]({shield('status', 'archived', '6370B6')})")
    return "\n".join(lines)


def footer(ctx: RepoContext) -> str:
    line = ctx.brand.fmt(ctx.brand.venture(ctx.entry.venture)["footer"])
    return f"---\n\n<div align=\"center\">\n<sub>{line}</sub>\n</div>"


def license_section(ctx: RepoContext) -> str | None:
    policy = ctx.license_policy
    if policy == "dual-agpl":
        return (
            "## License\n\n"
            "This project is dual licensed.\n\n"
            "- **Community Edition** — [GNU Affero General Public License v3 (AGPLv3)](LICENSE). "
            "Free to use, modify, and self-host. If you distribute a modified version or run it as a "
            "network service, you must make the corresponding source available.\n"
            "- **Commercial License** — for organisations that want to embed, modify, or distribute this "
            "software without AGPLv3's obligations. See [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)."
        )
    if policy == "mit":
        return "## License\n\nMIT — see [LICENSE](LICENSE)."
    return None


def archived_banner(ctx: RepoContext) -> str:
    succ = ctx.entry.successor
    tail = f" Its successor is **[{succ}](https://github.com/{ctx.brand.identity['owner']}/{succ})**." if succ else ""
    return (
        "> [!NOTE]\n"
        f"> **Archived.** This project is kept for reference and is no longer maintained.{tail}"
    )


def commercial_license(ctx: RepoContext) -> str:
    t = Template((TEMPLATES / "files" / "COMMERCIAL-LICENSE.md").read_text())
    return t.substitute(repo=ctx.name, owner=ctx.brand.identity["owner"],
                        holder=ctx.brand.raw["license"]["copyright_holder"],
                        site=ctx.brand.identity["site"])


def agpl_text() -> str:
    return (TEMPLATES / "files" / "LICENSE-AGPL-3.0").read_text()


def mit_text(ctx: RepoContext, year: int) -> str:
    t = Template((TEMPLATES / "files" / "LICENSE-MIT").read_text())
    return t.substitute(year=year, holder=ctx.brand.raw["license"]["copyright_holder"])


def editorconfig() -> str:
    return (TEMPLATES / "files" / "editorconfig").read_text()


def gitignore(stack: list[str]) -> str:
    parts = [(TEMPLATES / "files" / "gitignore" / "base").read_text()]
    for s in stack:
        p = TEMPLATES / "files" / "gitignore" / s
        if p.exists():
            parts.append(p.read_text())
    return "\n".join(parts)


def workflow(ctx: RepoContext) -> str:
    t = Template((TEMPLATES / "files" / "tbj-workflow.yml").read_text())
    stack_jobs = []
    if "python" in ctx.stack and any(p.name.startswith("test_") or p.parent.name == "tests" for p in ctx.files):
        stack_jobs.append(
            "  python:\n"
            f"    uses: {ctx.brand.identity['owner']}/tbj-brand/.github/workflows/python-ci.yml@v1\n"
        )
    if "node" in ctx.stack:
        stack_jobs.append(
            "  node:\n"
            f"    uses: {ctx.brand.identity['owner']}/tbj-brand/.github/workflows/node-ci.yml@v1\n"
        )
    return t.substitute(owner=ctx.brand.identity["owner"], stack_jobs="\n".join(stack_jobs).rstrip())


def marker(ctx: RepoContext) -> str:
    e = ctx.entry
    return (
        "# Written by tbj-brand. Tier and venture are set centrally in tbj-brand/repos.toml;\n"
        "# this stamp records which version of the standard this repo was last synced to.\n"
        f'standards = "{ctx.brand.version}"\n'
        f'tier = "{e.tier}"\n'
        f'venture = "{e.venture}"\n'
    )


def readme_skeleton(ctx: RepoContext) -> str:
    t = Template((TEMPLATES / "readme" / "skeleton.md").read_text())
    desc = ctx.entry.description or "<!-- TODO: one-sentence description -->"
    sections = []
    for s in ctx.brand.raw["readme"]["sections"]:
        if s == "License":
            continue
        sections.append(f"## {s}\n\n<!-- TODO -->\n")
    return t.substitute(title=ctx.name, description=desc, sections="\n".join(sections))


# ── Design tokens → platform files ──────────────────────────────────────────
def _tokens(brand: Brand) -> dict:
    return json.loads(brand.tokens_path().read_text())


def tokens_css(brand: Brand) -> str:
    tok = _tokens(brand)
    dark, light = [], []
    for t in tok["color"]["tokens"]:
        v = t["value"]
        if isinstance(v, dict):
            dark.append(f"  --{t['name']}: {v['dark']};")
            light.append(f"  --{t['name']}: {v['light']};")
        elif isinstance(v, str) and v.startswith("{"):
            ref = v.strip("{}")
            dark.append(f"  --{t['name']}: var(--{ref});")
    static = []
    fam = tok.get("type", {}).get("families", {})
    for k, v in fam.items():
        static.append(f"  --font-{k}: {v};")
    for group in ("spacing", "radius", "size", "duration"):
        for t in tok.get(group, {}).get("tokens", []):
            static.append(f"  --{t['name']}: {t['value']};")
    shadows_d, shadows_l = [], []
    for t in tok.get("shadow", {}).get("tokens", []):
        shadows_d.append(f"  --{t['name']}: {t['value']['dark']};")
        shadows_l.append(f"  --{t['name']}: {t['value']['light']};")
    head = (f"/* {tok['name']} — generated by tbj-brand {brand.version}. Do not edit; change tbj-brand/tokens and re-sync. */\n")
    dark_block = "\n".join(dark + shadows_d)
    light_block = "\n".join(light + shadows_l)
    return (
        head
        + ":root {\n  color-scheme: dark light;\n" + "\n".join(static) + "\n" + dark_block + "\n}\n"
        + "@media (prefers-color-scheme: light) {\n  :root:not([data-theme=\"dark\"]) {\n"
        + "\n".join("  " + l for l in light_block.splitlines()) + "\n  }\n}\n"
        + ":root[data-theme=\"light\"] {\n" + light_block + "\n}\n"
        + ":root[data-theme=\"dark\"] {\n" + dark_block + "\n}\n"
    )


def tokens_py(brand: Brand) -> str:
    tok = _tokens(brand)
    dark, light = {}, {}
    for t in tok["color"]["tokens"]:
        v = t["value"]
        if isinstance(v, dict):
            dark[t["name"]] = v["dark"]
            light[t["name"]] = v["light"]
    fam = tok.get("type", {}).get("families", {})
    return (
        f'"""{tok["name"]} — generated by tbj-brand {brand.version}. Do not edit."""\n\n'
        f"DARK = {json.dumps(dark, indent=4)}\n\n"
        f"LIGHT = {json.dumps(light, indent=4)}\n\n"
        f"FONTS = {json.dumps(fam, indent=4)}\n\n"
        "def theme(mode: str = \"dark\") -> dict:\n"
        "    return DARK if mode == \"dark\" else LIGHT\n"
    )


def tokens_ts(brand: Brand) -> str:
    tok = _tokens(brand)
    dark, light = {}, {}
    for t in tok["color"]["tokens"]:
        v = t["value"]
        if isinstance(v, dict):
            dark[t["name"]] = v["dark"]
            light[t["name"]] = v["light"]
    return (
        f"// {tok['name']} — generated by tbj-brand {brand.version}. Do not edit.\n"
        f"export const dark = {json.dumps(dark, indent=2)} as const;\n"
        f"export const light = {json.dumps(light, indent=2)} as const;\n"
        "export type Token = keyof typeof dark;\n"
    )
