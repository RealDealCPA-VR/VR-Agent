# RealDeal CPA — New-Machine / Production Setup

This project is path-portable: `install.ps1` and `sync-overlay.ps1` resolve all paths at
deploy time (`__VRAGENT_ROOT__` = this folder, `__PROJECTS_ROOT__` = its parent). You do
**not** need the `C:\Users\VR\...` paths to match.

## 1. Prerequisites (on PATH)
- **git**, **uv**, **Node 20.x** (required for the QuickBooks live COM binding), **npm**, **pnpm**
- **QuickBooks Desktop** installed, for live bookkeeping (the MCP also runs in safe simulation without it)
- *(optional)* **dotnet SDK** for Lacerte (LacertMCP); **Python 3.11** is provisioned by `uv`

## 2. Expected layout
Place this project and its sibling integration projects under the **same parent folder**:
```
<ProjectsRoot>\
  VRAGENT\                  <- this repo
  Quickbooks MCP Desktop\   <- QuickBooks MCP (built: dist/index.js)
  KarbonCopy\               <- practice-mgmt MCP (with its .env.local + data/)
  RPA\                      <- desktop-control engine (ai_rpa_system)
  VR-Ledger\                <- plain-text ledger engine
```
If a sibling project is absent, that MCP server simply won't start — comment it out of
`vr-overlay/config/config.yaml.tmpl` (`mcp_servers`) and re-run `sync-overlay.ps1`.

## 3. Install
```powershell
git clone https://github.com/RealDealCPA-VR/VR-Agent.git VRAGENT
cd VRAGENT
.\scripts\install.ps1            # clones Hermes, installs, seeds skills, builds + rebrands the dashboard
```

## 4. Configure
1. **LLM key** — edit `home\.env`: `OPENROUTER_API_KEY=...` (or `ANTHROPIC_API_KEY=...`). Required.
2. **KarbonCopy** — its own `.env.local` (`KARBONCOPY_API_KEY`, `APP_ENCRYPTION_KEY`, `DATABASE_URL`).
3. **QuickBooks live** — in `vr-overlay\mcp\launchers\quickbooks.cmd.tmpl` set `QB_LIVE=1` and
   `QB_COMPANY_FILE=...`, re-run `sync-overlay.ps1`, and have QB Desktop open with that file.
   First connection prompts a one-time QB authorization.
4. *(optional)* **Slack** — `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` in `home\.env`; **Pixio** — `PIXIO_API_KEY`.

## 5. Verify
```powershell
.\scripts\vragent.ps1 doctor        # green
.\scripts\vragent.ps1 mcp list       # desktop / quickbooks / karboncopy / vr-ledger enabled
.\scripts\vragent.ps1                # start the agent (run firm onboarding first — see below)
```

## 6. First day on the job
Before production work, run the **`firm-onboarding`** flow so the agent learns your firm and
clients, and load/seed client profiles (`client-context`). It comes with 15 years of expertise
but no knowledge of *your* firm until onboarded.

## 7. Authority gates (do NOT skip)
The agent operates in tiers (see the `authority-and-escalation` skill):
- **Autonomous:** read, categorize, reconcile, draft, prepare, analyze, write workpapers.
- **Requires your sign-off:** posting material/unusual journal entries, sending client emails,
  moving money / cutting payments, and **submitting any tax or payroll filing**. It prepares and
  pre-fills; you review and authorize the submit. Keep these gates on in production.
