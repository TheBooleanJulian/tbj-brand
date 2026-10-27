# Alignment register

The human-judgement half of tbj-brand. `tbjsync audit` finds drift it can measure; this file records
the off-cases that need a decision, and what each one should become. Started during the Zeabur
shutdown migration (Oct 2026); migration progress itself lives in `../zeabur-migration/progress.md`.

How it works:
- Measurable drift becomes a check (see `tbjsync/checks.py`). Infra drift is covered by
  `infra_host` and `data_store`, driven by `host` / `data` in repos.toml and `[infra]` in brand.toml.
- Anything needing a call (database consolidation, palette, deleting a service) stays here as a row
  until Julian decides, then becomes either a repos.toml value or a check.
- Rows are never deleted: mark them **resolved** with the date and what was done.

## Open decisions (need Julian)
| # | Decision | Context | Status |
|---|---|---|---|
| D1 | Which palette is the standard: `unified` (cyan #00E5FF / magenta #FF2BD6, Chakra Petch + IBM Plex Sans, light mode) or `legacy` (teal #00D4C8 / gold #F5C842, Space Grotesk, dark only)? | brand.toml has `palette.active = "unified"` and `julian-unified-ui-design-system.md` (desktop spec) is in progress, but global AGENTS.md / CLAUDE.md still mandate legacy teal/gold, dark only. Agents follow AGENTS.md until this is settled. | **resolved 2026-10-26**: Unified UI takes precedence. Global AGENTS.md / CLAUDE.md / design rules updated to match; legacy palette kept in tokens/legacy.json for un-migrated apps only. |
| D2 | Supabase layout: one project, one schema per app. Cross-schema access allowed by explicit grant only? | Replaces separate Postgres (mikuquest, accurova-card, srv-3dp-tycoon, second-brain, accurova-live-event), SQLite (clawsune, luxsync-v3, accurova-live-event) and Redis (food-analyst-bot, miku-monday, infinicanvas) | open, planning |
| D3 | Versioned repos: retire older versions instead of migrating them? | luxsync-v2 is `tier = "archive"` (successor luxsync-v3) but still runs on Zeabur | **resolved 2026-10-26**: retire superseded versions (luxsync-v2, and v1/v2 of anything with a later version). Suspend on Zeabur, don't migrate. |
| D4 | Where wrangler config lives during migration | Staged in zeabur-migration/sites/ so repos stay untouched; target is `wrangler.jsonc` in each repo root (infra_host checks for it) | open |
| D5 | Deploy-on-push for Workers | Zeabur redeployed on every push; Workers sites are deployed from Julian's machine today. Options: Cloudflare Workers Builds (connect repo in dashboard, needs wrangler.jsonc in repo) or a GitHub Action running `wrangler deploy` with a CLOUDFLARE_API_TOKEN secret. Workers Builds is the closer Zeabur equivalent and needs no token in GitHub. | open |
| D6 | Large media (miku-bday dl/, 6 GB of mp4) | Workers static assets cap files at 25 MiB. R2 bucket + custom domain is the Cloudflare option (free tier 10 GB). | open |
| D7 | Bot runtime (see zeabur-migration/HARD-GROUP-PLAN.md H1) | Telegram serverless has no scheduler and no runtime-secret store; 8 of 11 bots need cron, 9 need API keys | open: recommend Cloudflare Workers webhook bots |

## Baseline snapshot (2026-10-26)
| Attribute | Finding |
|---|---|
| Language | python 16, node 11, static 7, unclear 5 |
| Default branch | main 20, master 12, other/feature branch checked out 7 |
| `dev` branch exists (global workflow needs it) | only 11 of 39 |
| Dockerfile | 13 of 39 |
| Caddyfile | 1 (accurova-site) |
| Procfile | 5 (bot-core-canary, clawsune, luxsync-v3, probe-seo-analyzer, openclaw) |
| zeabur.json | 3 (chuckleclips, mikew-gcal-v3, monitoring-miku) |
| CI workflows | 8 of 39 |
| Tests | 2 of 39 |
| .env.example | 16 of 39 |
| AGENTS.md / handover.md / CHANGELOG.md | 1 / 1 / 1 |
| README, LICENSE | 39 / 35 |
| Database | none 29, redis 3, postgres 3-4, sqlite 3, supabase 1 (xymiku-site) |
| Frameworks | telegram bots 10, fastapi 5-6, express 7, vite 5, next 1, flask 1 |


## Off-case register
Format: repo | category | what's different | suggested alignment | found during
| Repo | Category | Off-case | Suggested alignment | Found during |
|---|---|---|---|---|
| accurova-site | web server | Only repo with a Caddyfile | Replace with `_headers`/`_redirects` on Workers assets | scan |
| xymiku-site | database | Only repo using Supabase; Next.js on a separate Cloudflare account | Fold into the consolidated Supabase project (own schema); account now unified via admin invite | scan |
| clawsune, luxsync-v3, accurova-live-event | database | SQLite used inside long-running Python services | Decide per app: Supabase schema or Telegram-serverless SQLite | scan |
| mikuquest, accurova-card, accurova-live-event, second-brain | database | Separate Postgres instances (some on Zeabur) | Consolidate into one Supabase project, schema per app | scan |
| food-analyst-bot, miku-monday, infinicanvas | database | Redis dependency | Replace with Supabase table or Durable Object/KV | scan |
| 12 repos | git | Default branch is `master` not `main` | Rename to `main` | scan |
| 28 of 39 repos | git | No `dev` branch | Create `dev` per global workflow | scan |
| clawsune, miku-singlish-word-of-the-day, luxsync-v3, miku-ocr, accurova-card, invoice-forge | git | Local checkout sits on a feature branch, unmerged work possible | Check for unmerged changes before touching | scan |
| chuckleclips, mikew-gcal-v3, monitoring-miku | deploy | zeabur.json present | Remove after cutover | scan |
| bot-core-canary, clawsune, luxsync-v3, probe-seo-analyzer, openclaw | deploy | Procfile and often a Dockerfile both exist | Pick one; both go once off Zeabur | scan |
| accurova-workflow-dashboard, accurova-loyalty, rothko-cal | structure | No recognizable manifest locally | Locate real source, align layout | scan |
| accurova-ai-web-search, srv-3dp-tycoon | source | Deployed on Zeabur but no local repo folder | Pull from GitHub, add to workspace | scan |
| food-analyst-bot, miku-monday | duplicate | Two Zeabur projects each (`-2` copies) | Confirm duplicates, retire extras | scan |
| openclaw | duplicate | Likely stale copy of clawsune (see memory) | Archive | scan |
| 37 of 39 repos | tests | No tests dir | Add only for core logic, per global rule | scan |
| 31 of 39 repos | ci | No GitHub Actions | Add proportionate CI where it has logic | scan |
| luxsync-v2 | lifecycle | Archived in repos.toml but still deployed on Zeabur | Retire, don't migrate (D3) | migration |
| thebooleanjulian-branding | tooling | No remote, no `dev` branch; `tbjsync` crashed printing on Windows (cp1252) | dev created; encoding fixed in v1.1.0; push + tag v1 still pending | alignment |
| miku-bday | security | `ADMIN_KEY` shared secret hardcoded in admin.html (client-side); Apps Script URL never configured | Move admin auth server-side (Worker or Apps Script check), rotate key | migration |
| miku-figures, readme-forge | uptime | Already returning 502 on Zeabur before migration (readme-forge deployment REMOVED) | Fleet has no uptime check; monitoring-miku only watches bots | migration |
| minutes-in-seconds | deploy | Zeabur deployment stuck in BUILDING; Whisper + pyannote is too heavy for Workers/Vercel | Re-plan with hard group | migration |
| accurova-bni | config | Build-time config.js generated from host env vars (zbpack.json + scripts/build.js) | Standard: public config via wrangler `vars` or committed config; secrets never in browser config | migration |
| invoice-forge | structure | Express server whose only job is serving static files + /healthz | Drop server, serve public/ as Workers assets (done for hosting) | migration |
| accurova-site, deckmate, others | routing | Zeabur served the homepage (200) for unknown paths; Caddyfile 404 page never actually applied | Workers assets: explicit `not_found_handling` per site (404-page or single-page-application) | migration |
| all repos | line endings | Drive working copies are CRLF, deployed files LF | Add `.gitattributes` (`* text=auto eol=lf`) to the standard | migration |
| food-analyst-bot, miku-monday | duplicate | Older Zeabur copies (deployment REMOVED) and live `-2` copies share one bot token | Retire originals (suspend pending Julian) | migration |
| juliancheung-landing | hygiene | `.claude/settings.local.json` committed and publicly served on juliancheung.com (permissions allowlist, no secrets) | Add `.claude/` and `.vscode/` to the standard .gitignore; deploy tooling must never serve dot-folders (stage_static.py now skips them) | migration |
| accurova-workflow-dashboard | security | `VITE_API_KEY` is baked into the browser bundle at build time | Keep keys server-side (Worker); browser gets a session, not a key | triage |
| accurova-loyalty | deploy | Zeabur service with no running deployment still claims `infinicanvas.thebooleanjulian.dev` | Release the hostname when retiring; one hostname per app | triage |
| clawsune, supercalifragilisticex, miku-ocr | runtime | OCR via Tesseract, a native binary (can't run in Workers or Telegram serverless) | One shared approach: vision-model OCR (Gemini) in the JS bot skeleton | triage |
| 8 bots | runtime | Scheduling reinvented per bot: job_queue, APScheduler, node-cron, setInterval | Cron Triggers in wrangler.jsonc + one `scheduled` handler pattern | triage |
| 5 apps | data | Redis used for small state/cache in miku-monday, food-analyst-bot, miku-singlish, supercalifragilisticex, infinicanvas | D1/KV for bot state, Durable Objects for infinicanvas real-time | triage |
| second-brain, web-search-ai-agent, accurova-loyalty, readme-forge | lifecycle | Zeabur deployments REMOVED or never configured; apps silently not running | Uptime + last-deploy check in the new monitoring-miku | triage |
| every Zeabur service | config | `PASSWORD` variable present on all 55 services (injected by Zeabur, not read by most apps) | Ignore when migrating; only carry variables the code reads | triage |
| are-you-donkey | content drift | Zeabur copy (45,827 B) differs from repo HEAD (46,882 B): last deploy was behind the repo | Confirm repo HEAD is intended; note drift | migration |

- deckmate, miku-watch, accurova-site, miku-figures, iq-aptitude-test, see-your-voice, miku-keytar, accurova-bni, invoice-forge: live on Workers 2026-10-26; configs in zeabur-migration/sites/.
