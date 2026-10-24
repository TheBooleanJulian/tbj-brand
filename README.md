<div align="center">

# tbj-brand

**One source of truth for every TheBooleanJulian repo — and a bot that keeps them all in line.**

![Python](https://img.shields.io/badge/-Python%203.11+-3776AB?logo=python&logoColor=white)
![Stdlib only](https://img.shields.io/badge/dependencies-none-05060D)
![GitHub Actions](https://img.shields.io/badge/-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)

</div>

---

## What it does

Every repo gets the same README chrome, licence files, footer, hygiene files, CI and design tokens — without anyone editing 69 repos by hand. You change wording, colours or policy **here**; the sync workflow opens one pull request per drifting repo. Nothing merges without you.

It only ever rewrites two things:

- **Managed blocks** in READMEs, fenced by `<!-- tbj:NAME:start -->` … `<!-- tbj:NAME:end -->` (badges, licence section, footer, archived banner). Everything outside them is the repo's own.
- **Managed files**: `.tbj.toml`, `.editorconfig`, `.github/workflows/tbj.yml`, `brand/tokens.css`, and `LICENSE` / `COMMERCIAL-LICENSE.md` when they're missing.

Anything with legal or deployment consequences — relicensing, renaming `master` → `main`, Zeabur cut-over, fork licences — is **reported in the PR as a checklist, never auto-applied**.

## How it fits together

```
tbj-brand (this repo)                         every other repo
├── brand.toml   identity, palette, policy    ├── README.md   ← managed blocks inside
├── repos.toml   tier/venture/wave per repo   ├── .tbj.toml   ← "conforms to v1.0.0"
├── tokens/      design tokens (2 palettes)   ├── brand/tokens.css
├── templates/   footer, licences, CI …       └── .github/workflows/tbj.yml
├── tbjsync/     the engine (stdlib Python)          │ calls
└── .github/workflows/                               ▼
    ├── sync.yml ──── opens PRs ─────────▶   conformance.yml@v1  (job summary per push)
    ├── conformance.yml  (reusable)          python-ci.yml@v1 / node-ci.yml@v1
    ├── python-ci.yml / node-ci.yml (reusable)
    └── kit-ci.yml
TheBooleanJulian/.github  → CONTRIBUTING, SECURITY, issue + PR templates inherited by all repos
TheBooleanJulian/TheBooleanJulian → profile README generated from repos.toml
```

**Tiers** decide how much applies: `product` (everything, incl. UI tokens) · `tool` (repo chrome, UI advisory) · `themed` (games and fan projects — chrome only, UI exempt) · `archive` (banner + footer, then archive) · `external` (forks — never touched, licence flagged).

**Ventures** decide the footer and brand badge: `tbj`, `accurova`, `upteach`, `fan`.

**Waves** stage the rollout: `0` canary → `1` maintained products → `2` everything.

## Quick Start

```bash
git clone https://github.com/TheBooleanJulian/tbj-brand && cd tbj-brand
python -m tbjsync audit --repos-dir ~/code          # score local clones, change nothing
python -m tbjsync fix   --repo ~/code/qr-forge      # see exactly what a PR would contain
git -C ~/code/qr-forge diff
```

## Setup (one time)

1. **Create this repo** as `TheBooleanJulian/tbj-brand` (public — other repos' workflows read it) and push.
2. **Tag it** so reusable workflows resolve: `git tag v1 && git push origin v1`.
3. **Create `TheBooleanJulian/.github`** (public) from the `dotgithub/` folder.
4. **Add a token**: a fine-grained PAT with access to all repositories and *Contents*, *Pull requests* and *Workflows* set to read/write. Save it here as the Actions secret `TBJ_SYNC_TOKEN`.
5. **Canary**: Actions → *Sync standards* → Run workflow with wave `0`, dry run **on**. Read the log. Run again with dry run **off**. Review and merge the three canary PRs.
6. **Roll out**: run wave `1`, merge, then wave `2`.
7. **Automate**: set `auto_sync = true` in `brand.toml`. From then on, every change to the kit and every Monday re-syncs.
8. **Tighten**: once repos are green, set `enforce = "error"` so drift fails CI.

## Day to day

| You want to… | Do this |
|---|---|
| Change footer wording, badge colour, licence text | Edit `brand.toml` or `templates/`, bump `standards.version`, push. PRs follow. |
| Switch palette (legacy teal ↔ Unified UI) | `palette.active` in `brand.toml`, then `python -m tbjsync tokens`. |
| Start a new repo | Add it to `repos.toml` (tier, venture, wave 2). The next sync onboards it. |
| Exempt one repo from one check | `skip = ["ui_tokens"]` on its `repos.toml` entry. |
| Keep a repo's own licence | `license = "keep"` (or `"mit"`) on its entry. |
| Retire a repo | `tier = "archive"`, `successor = "new-repo"`; merge the PR, then archive on GitHub. |
| Update the GitHub profile | `python -m tbjsync profile` → copy `dist/profile-README.md`. The sync job also refreshes it. |

## Configuration

| File | What lives there |
|---|---|
| `brand.toml` | Standards version, enforcement, `auto_sync`, identity and domain, active palette, licence policy, branch policy, venture footers, tier → checks, README section order |
| `repos.toml` | One entry per repo: `tier`, `venture`, `license`, `relicense`, `description`, `homepage`, `successor`, `wave`, `skip`, `notes` |
| `tokens/*.json` | `unified` (Julian Unified UI) and `legacy` (teal/gold) — same token names, so apps switch by swapping one file |

## Checks

| id | Level | Auto-fix | What it checks |
|---|---|---|---|
| `marker` | info | ✓ | `.tbj.toml` stamp matches the current standard |
| `readme` | error | ✓ skeleton | README exists |
| `badges` | warn | ✓ | Licence + domain (+ venture) badges, no duplicates |
| `license_section` | warn | ✓ | Licence section matches policy |
| `footer` | error | ✓ | Venture footer; migrates the Sept 2026 hand-written footers |
| `sections` | warn | — | Canonical sections present (aliases allowed) |
| `archived_banner` | warn | ✓ | Archive notice with successor link |
| `license_files` | error | ✓ if missing | LICENSE / COMMERCIAL-LICENSE.md; **never relicenses without `relicense = true`** |
| `fork_license` | error | — | Forks claiming dual licensing |
| `editorconfig` | info | ✓ | Shared `.editorconfig` |
| `gitignore` | warn | ✓ if missing | Stack-aware seed |
| `ci` | warn | ✓ | `tbj.yml` calling the reusable workflows |
| `branch_main` | warn | — | Default branch is `main` (prints the rename command) |
| `branch_dev` | info | — | `dev` branch exists |
| `zeabur` | warn | — | Files still referencing Zeabur (migration tracker) |
| `ui_tokens` | warn | vendors tokens | Off-palette colours / fonts; keeps `brand/tokens.css` current |

## Project Structure

```
brand.toml  repos.toml  pyproject.toml
tokens/      unified.json, legacy.json
templates/   files/ (licences, editorconfig, gitignore/, tbj-workflow.yml), readme/skeleton.md
tbjsync/     config.py, blocks.py, render.py, checks.py, __main__.py
dist/        generated tokens.css|py|ts, profile-README.md, projects.json
dotgithub/   contents for TheBooleanJulian/.github
tests/       pytest suite
```

## Changelog

- **v1.0.0** — *2026-10-25* — Initial release: 16 checks, managed blocks with legacy migration, wave-based PR sync, reusable conformance/Python/Node CI, two token palettes, profile generator, `.github` community files.

<!-- tbj:license:start · managed by tbj-brand — edits inside are overwritten -->
## License

This project is dual licensed.

- **Community Edition** — [GNU Affero General Public License v3 (AGPLv3)](LICENSE). Free to use, modify, and self-host. If you distribute a modified version or run it as a network service, you must make the corresponding source available.
- **Commercial License** — for organisations that want to embed, modify, or distribute this software without AGPLv3's obligations. See [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md).
<!-- tbj:license:end -->

<!-- tbj:footer:start · managed by tbj-brand — edits inside are overwritten -->
---

<div align="center">
<sub>Built by <a href="https://github.com/TheBooleanJulian">@TheBooleanJulian</a> · <a href="https://thebooleanjulian.dev">thebooleanjulian.dev</a></sub>
</div>
<!-- tbj:footer:end -->
