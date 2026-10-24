"""Tests for tbjsync. Run: pytest -q"""
import subprocess
from pathlib import Path

import pytest

from tbjsync import blocks, checks, render
from tbjsync.config import Brand, RepoEntry, build_context

BRAND = Brand.load()

LEGACY = """<div align="center">

# Demo

**Does a thing.**

![Python](https://img.shields.io/badge/-Python-3776AB)
![License](https://img.shields.io/badge/license-AGPLv3%20%2F%20Commercial-00D4C8.svg)

</div>

---

## What it does

Stuff.

## License

This project is dual licensed.

- Community Edition — AGPL.

---

<div align="center">
<sub>Built by <a href="https://github.com/TheBooleanJulian">@TheBooleanJulian</a></sub>
</div>"""


def make_repo(tmp_path: Path, files: dict, entry: RepoEntry | None = None, commit=True):
    root = tmp_path / (entry.name if entry else "demo")
    root.mkdir()
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    if commit:
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                        "commit", "-qm", "init", "--allow-empty"], check=True)
    manifest = {entry.name: entry} if entry else {}
    return build_context(root, BRAND, manifest, default_branch="main", has_dev=True)


def run_fix(ctx):
    return checks.run(ctx, apply=True)


def test_legacy_footer_is_migrated_once(tmp_path):
    ctx = make_repo(tmp_path, {"README.md": LEGACY, "LICENSE": render.agpl_text()})
    run_fix(ctx)
    text = (ctx.path / "README.md").read_text()
    assert text.count("Built by") == 1
    assert blocks.has(text, "footer")
    assert "thebooleanjulian.dev" in blocks.get(text, "footer")


def test_markdown_footer_variant(tmp_path):
    readme = "# X\n\nHello.\n\nBuilt by [@TheBooleanJulian](https://github.com/TheBooleanJulian).\n"
    ctx = make_repo(tmp_path, {"README.md": readme})
    run_fix(ctx)
    text = (ctx.path / "README.md").read_text()
    assert text.count("Built by") == 1 and blocks.has(text, "footer")


def test_second_run_changes_nothing(tmp_path):
    ctx = make_repo(tmp_path, {"README.md": LEGACY, "index.html": "<style>body{font-family:Arial}</style>"},
                    RepoEntry(name="demo", tier="product", venture="accurova"))
    _, first = run_fix(ctx)
    assert first
    ctx2 = build_context(ctx.path, BRAND, {"demo": ctx.entry}, default_branch="main", has_dev=True)
    _, second = run_fix(ctx2)
    assert second == []


def test_license_badge_not_duplicated(tmp_path):
    ctx = make_repo(tmp_path, {"README.md": LEGACY})
    run_fix(ctx)
    text = (ctx.path / "README.md").read_text()
    assert text.count("img.shields.io/badge/license") == 1


def test_numbered_license_heading_is_recognised(tmp_path):
    readme = "# X\n\nIntro.\n\n## 9 · Changelog\n\n- v1\n\n## 10 · License\n\nOld text.\n"
    ctx = make_repo(tmp_path, {"README.md": readme})
    run_fix(ctx)
    text = (ctx.path / "README.md").read_text()
    assert "Old text." not in text
    assert text.count("## License") == 1


def test_badges_never_split_a_heading(tmp_path):
    readme = "# Title\n\nPara one line one\nline two.\n\nPara two.\n\n## How it works\n\nText.\n"
    ctx = make_repo(tmp_path, {"README.md": readme})
    run_fix(ctx)
    text = (ctx.path / "README.md").read_text()
    assert "\n## How it works\n" in text
    assert text.index("tbj:badges:start") < text.index("Para two.")


def test_existing_mit_is_not_relicensed_without_consent(tmp_path):
    mit = "MIT License\n\nCopyright (c) 2026 X\n\nPermission is hereby granted, free of charge, ..."
    ctx = make_repo(tmp_path, {"README.md": "# X\n\nHi.\n", "LICENSE": mit})
    findings, _ = run_fix(ctx)
    lic = next(f for f in findings if f.check == "license_files")
    assert lic.status == checks.MANUAL
    assert (ctx.path / "LICENSE").read_text() == mit


def test_agpl_notice_upgraded_to_full_text(tmp_path):
    notice = ("Copyright (c) 2026 TheBooleanJulian\n\nThis program is free software: you can redistribute it "
              "and/or modify\nit under the terms of the GNU Affero General Public License as published by\n...")
    ctx = make_repo(tmp_path, {"README.md": "# X\n\nHi.\n", "LICENSE": notice})
    findings, _ = run_fix(ctx)
    assert next(f for f in findings if f.check == "license_files").status == checks.FIXED
    assert "GNU AFFERO" in (ctx.path / "LICENSE").read_text()[:200]


def test_relicense_flag_allows_replacement(tmp_path):
    mit = "MIT License\n\nPermission is hereby granted, free of charge, ..."
    ctx = make_repo(tmp_path, {"README.md": "# X\n\nHi.\n", "LICENSE": mit},
                    RepoEntry(name="demo", relicense=True))
    run_fix(ctx)
    assert "GNU AFFERO" in (ctx.path / "LICENSE").read_text()[:200]
    assert (ctx.path / "COMMERCIAL-LICENSE.md").exists()


def test_external_fork_is_flagged_and_untouched(tmp_path):
    files = {"README.md": "# Fork\n", "LICENSE": render.agpl_text(), "COMMERCIAL-LICENSE.md": "x"}
    ctx = make_repo(tmp_path, files, RepoEntry(name="demo", tier="external"))
    findings, changed = run_fix(ctx)
    assert changed == []
    assert findings[0].check == "fork_license" and findings[0].status == checks.MANUAL


def test_empty_repo_is_skipped(tmp_path):
    ctx = make_repo(tmp_path, {}, commit=False)
    findings, changed = run_fix(ctx)
    assert changed == [] and findings[0].check == "empty"


def test_archive_tier_gets_banner_only(tmp_path):
    ctx = make_repo(tmp_path, {"README.md": "# Old\n\nOld thing.\n"},
                    RepoEntry(name="demo", tier="archive", successor="new-thing"))
    _, changed = run_fix(ctx)
    text = (ctx.path / "README.md").read_text()
    assert blocks.has(text, "archived") and "new-thing" in text
    assert not text.startswith("\n")
    assert not (ctx.path / ".github/workflows/tbj.yml").exists()


def test_venture_wording(tmp_path):
    ctx = make_repo(tmp_path, {"README.md": "# X\n\nHi.\n"}, RepoEntry(name="demo", venture="accurova"))
    run_fix(ctx)
    assert "Accurova" in blocks.get((ctx.path / "README.md").read_text(), "footer")


def test_edit_inside_block_is_reverted(tmp_path):
    ctx = make_repo(tmp_path, {"README.md": LEGACY})
    run_fix(ctx)
    p = ctx.path / "README.md"
    p.write_text(p.read_text().replace("Built by", "Hacked by"))
    run_fix(build_context(ctx.path, BRAND, {}, default_branch="main", has_dev=True))
    assert "Hacked by" not in p.read_text()


def test_tokens_css_has_both_themes():
    css = render.tokens_css(BRAND)
    assert ":root[data-theme=\"light\"]" in css and "prefers-color-scheme: light" in css
    assert "--cyan:" in css and "--font-mono:" in css


@pytest.mark.parametrize("palette", ["unified", "legacy"])
def test_both_palettes_generate(palette):
    b = Brand.load()
    b.raw["palette"]["active"] = palette
    assert "--bg:" in render.tokens_css(b)
    assert "DARK" in render.tokens_py(b)
