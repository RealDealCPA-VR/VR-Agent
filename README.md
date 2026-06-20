# VRAGENT

A personal, ultra-capable agent for Valentino — a **customized overlay on
[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)**, tuned for
**accounting, bookkeeping, tax research, marketing, consulting, practice management, and
email**, with full creative range — and the ability to **control the Windows desktop and
browse the web from the terminal**.

Upstream Hermes stays untouched and updatable; everything that makes it *yours* lives in
`vr-overlay/`, and all runtime state lives in a repo-local `HERMES_HOME` (`home/`).

## Layout
```
hermes-agent/            upstream clone (pinned in HERMES_PIN.txt), editable-installed
home/                    HERMES_HOME — config.yaml, SOUL.md, skills/, sessions, memory (runtime)
vr-overlay/              tracked source of truth for all customization
  SOUL.md                the persona (CPA-grade advisor + creative range)
  config/config.yaml     model (multi-provider), toolsets, mcp_servers
  config/env.example     secrets template
  skills/                8 domain skills (accounting, tax, marketing, ...)
  mcp/desktop-control/   net-new Windows GUI-control MCP server (wraps your RPA project)
  mcp/launchers/         .cmd shims that run the QuickBooks/KarbonCopy MCPs from their dirs
scripts/
  install.ps1            reproducible one-shot setup
  sync-overlay.ps1       copy config.yaml + SOUL.md into home/ after editing
  vragent.ps1            launcher (sets HERMES_HOME=./home, runs `hermes …`)
```

## Setup
```powershell
.\scripts\install.ps1
# then add an LLM key to home\.env:  OPENROUTER_API_KEY=...  (or ANTHROPIC_API_KEY=...)
.\scripts\vragent.ps1 doctor
```

## Run (interfaces)
```powershell
.\scripts\vragent.ps1                 # interactive CLI
.\scripts\vragent.ps1 --tui           # terminal UI
.\scripts\vragent.ps1 dashboard       # web dashboard -> http://127.0.0.1:9119
.\scripts\vragent.ps1 model           # switch provider/model (multi-provider)
.\scripts\vragent.ps1 mcp list        # see wired MCP servers
.\scripts\vragent.ps1 gateway run     # messaging gateway (Slack, etc.)
```

## What's wired and working
- **Brain:** multi-provider (OpenRouter gateway by default; Anthropic/Nous/OpenAI/etc.
  switchable with `hermes model`). Default model `anthropic/claude-opus-4.6`.
- **Persona:** `vr-overlay/SOUL.md` (hot-reloaded every message).
- **Skills:** 8 domain skills + ~60 Hermes built-ins, all enabled. Domain skills live in
  `vr-overlay/skills` (read live via `skills.external_dirs`).
- **MCP tools (validated):**
  - `desktop` — 14 Windows GUI tools (screenshot/click/type/hotkey/scroll/launch/run_workflow).
  - `quickbooks` — 150 tools (currently **simulation mode**; safe mock books).
  - `karboncopy` — 33 practice-management tools (uses its own `.env.local` + SQLite).
  - `vr-ledger` — 7 plain-text double-entry tools (validate, balances, balance sheet, income statement, cash flow).
- **Web:** `web_search` + full `browser_*` toolset (local Chromium via agent-browser).
- **Capability packs:** image-gen (fal), premium web intel (exa, firecrawl), Google Workspace
  (Gmail/Calendar/Drive/Sheets), YouTube transcripts, TTS (edge-tts); finance skills
  (3-statement, DCF, comps, LBO, merger, Excel/PPTX authoring). CLI toolset includes
  browser, code execution, parallel **delegation** (subagents), session recall, and mixture-of-agents.
- **Self-improvement:** faster skill/memory nudges, background **curator** (consolidates
  learned skills), seeded `USER.md`/`MEMORY.md` so it starts knowing you. Promote learned
  skills into the tracked overlay with `.\scripts\promote-skills.ps1`.
- **Branding:** crimson/black VR-Ai theme — CLI skin `vragent` + dashboard theme `vragent`
  (config-only, no upstream fork). Tweak in `vr-overlay/skins/` and `vr-overlay/dashboard-themes/`.

## To finish wiring (needs your input / prereqs)
| Item | What it needs |
|------|----------------|
| **LLM key** | `OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY` in `home\.env` (required to run). |
| **QuickBooks live** | Edit `vr-overlay/mcp/launchers/quickbooks.cmd`: set `QB_LIVE=1` + `QB_COMPANY_FILE`, open QB Desktop. |
| **Lacerte (tax)** | Fix the `dotnet` SDK, build LacertMCP, add `launchers/lacerte.cmd`, uncomment `lacerte:` in config. |
| **tax-rag / vr-ledger** | Expose each FastAPI app as an http MCP (or adapter); uncomment in config. |
| **Slack** | Create a Slack app (Socket Mode), put `SLACK_BOT_TOKEN`+`SLACK_APP_TOKEN` in `.env`, `vragent.ps1 gateway run`. |
| **Email** | Configure the Email gateway / a Gmail MCP for valentinohelp@gmail.com. |
| **Pixio** | `PIXIO_API_KEY` in `.env` for the marketing/creative media skills. |

## Editing
- Change behavior/persona/models → edit files in `vr-overlay/`, then `.\scripts\sync-overlay.ps1`.
- Add a skill → drop `vr-overlay/skills/<category>/<name>/SKILL.md` (no sync needed).
- Add an MCP → add an entry under `mcp_servers:` in `vr-overlay/config/config.yaml`, sync, `vragent.ps1 mcp test <name>`.

Updating upstream: `git -C hermes-agent pull` then re-run `install.ps1` (your overlay is untouched).
