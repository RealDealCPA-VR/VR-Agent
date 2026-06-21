<div align="center">

# RealDeal CPA

### The AI accounting **employee** — not another tool you babysit.

**It arrives like a 15-year hire.** It learns your firm, follows your SOPs, leaves workpapers, self-checks, escalates what's material, and gets better every time you review it.

**It runs QuickBooks. It runs Windows. It runs the browser. From the terminal.**

`Black · White · Green` &nbsp;•&nbsp; `Windows` &nbsp;•&nbsp; `102 skills` &nbsp;•&nbsp; `16 SOP runbooks` &nbsp;•&nbsp; `4 MCP servers · 204 tools` &nbsp;•&nbsp; `CLI · TUI · Dashboard · Slack`

[Install](#install) · [Quickstart](#quickstart) · [Commands](#command-reference) · [Skill Catalog](#the-skill-catalog) · [Safety Model](#the-authority-model--trustworthy-by-design) · [Architecture](#architecture) · [FAQ](#troubleshooting--faq)

</div>

---

## The résumé

| | |
|---|---|
| **Role** | Staff accountant / CPA — bookkeeping, tax prep, advisory, practice ops |
| **Experience** | 15+ years of firm practice, encoded as 16 professional SOP runbooks |
| **Knows how a firm runs** | Yes — and onboards to learn *yours* on day one |
| **Operates** | QuickBooks Desktop · the Windows desktop (any app) · the web browser |
| **Leaves a paper trail** | A reviewable workpaper for every task |
| **Default posture** | Prepares everything; stops at money & filings for your sign-off |
| **Gets better** | Learns from your corrections; consolidates skills between sessions |

You're not installing software. You're staffing a seat.

---

## Why this is different

Most "AI for accounting" is a chatbot bolted onto a feature. RealDeal CPA is an **employee**: it onboards, holds context per client, works to a standard, and knows when to stop and ask. It's built as a customized, hardened overlay on the open-source [`NousResearch/hermes-agent`](https://github.com/NousResearch/hermes-agent) engine.

| | A tool / chatbot | **RealDeal CPA** |
|---|---|---|
| **Onboarding** | None — starts cold every time | First-day interview; learns *your* firm + clients |
| **Method** | Ad-hoc answers | 16 professional **SOP runbooks** it actually follows |
| **Evidence** | A chat log | A reviewable **workpaper** for every task |
| **Judgment** | Guesses on ambiguity | Routes material/ambiguous items to an **exceptions queue** |
| **Authority** | Acts freely, or not at all | Tiered **Green / Yellow / Red** gates — it prepares filings, *you* submit |
| **Reach** | API calls | Controls **QuickBooks Desktop, the Windows desktop, and the browser** |
| **Memory** | Forgets | Persistent `USER.md` / `MEMORY.md` + per-client profiles |

---

## What it does

- **Accounting & bookkeeping** — categorize, reconcile, close.
- **Tax** — research and prep; **sales-tax** nexus, prep & filing; **payroll-tax** prep (Forms 941/940, EFTPS).
- **Advisory & consulting** — client-facing analysis and recommendations.
- **Marketing & brand** — assets and campaigns for your firm or your clients.
- **Practice management** — email triage, comms cadence, proactive routines.
- **It operates the machine** — **QuickBooks Desktop**, the **Windows desktop (any app)**, and a **headless browser** — all from the terminal.

---

## Capabilities at a glance

| Surface | What's wired | Count |
|---|---|---|
| **Skills** | Enabled skills loaded on the agent | **102** |
| **SOP runbooks** | Professional, step-by-step procedures | **16** |
| **MCP tool servers** | desktop · quickbooks · karboncopy · vr-ledger | **4** |
| **Tools across servers** | 14 + 150 + 33 + 7 | **204** |
| **Web** | `web_search` + full headless-Chromium automation | navigate / click / type / screenshot / run JS |
| **Interfaces** | CLI · TUI · branded web dashboard · Slack | **4** |

### The 4 MCP tool servers

| Server | Tools | What it controls |
|---|---|---|
| **desktop** | 14 | Windows GUI automation — drive any desktop app |
| **quickbooks** | 150 | QuickBooks Desktop. **Safe SIMULATION by default**; live mode talks to QB Desktop |
| **karboncopy** | 33 | Practice management |
| **vr-ledger** | 7 | Plain-text double-entry ledger |

### Capability packs

- **Image generation** (fal) · **Premium web research** (exa / firecrawl)
- **Google Workspace** — Gmail, Calendar, Drive, Sheets · **YouTube transcripts** · **TTS**
- **Finance models** — 3-statement, DCF, plus **Excel & PowerPoint authoring**

### Self-improving by design

- **Persistent memory** — `USER.md` / `MEMORY.md` + per-client profiles, with a **local
  semantic-recall provider** (holographic — zero key, zero cost) layered on top.
- **Skill-creation loop** — a background review after each turn captures corrections and
  techniques into the right skill/memory; the `self-improvement` skill drives it for your firm.
- **Background curator** — consolidates overlapping skills into umbrellas and archives stale ones.
- **Promote what it learns** — `scripts/promote-skills.ps1` version-controls new agent skills.
- **Parallel subagents** — delegates work to run concurrently.
- **Multi-provider brain** — OpenRouter / Anthropic / others, switchable on the fly.

### Optimize for your model

Switching LLMs? `RealDeal CPA` tunes itself to the model you choose — reasoning effort,
autonomy budget, and how skills are delivered (lean for frontier models, explicit for small/
local ones). It's an **offer** — nothing changes without `-Apply`, and `-Revert` undoes it.

```powershell
.\scripts\optimize-skills.ps1                 # show what tuning the current model would get
.\scripts\optimize-skills.ps1 -Model haiku    # preview tuning for a model before you switch
.\scripts\optimize-skills.ps1 -Apply          # apply it (config + skill-style) and re-sync
```

---

## Install

> **Prereqs (on PATH):** Windows · git · uv · Node 20 · npm · pnpm. **QuickBooks Desktop** for live books (the MCP also runs in safe simulation without it). Paths are templated and portable across machines — see [`SETUP-NEW-MACHINE.md`](SETUP-NEW-MACHINE.md).

```powershell
git clone https://github.com/RealDealCPA-VR/VR-Agent.git VRAGENT
cd VRAGENT
.\scripts\install.ps1
```

`install.ps1` clones the engine, installs it, seeds the skills, and **builds + brands the dashboard**.

### Add an LLM key (required)

Edit `home\.env`:

```env
OPENROUTER_API_KEY=...        # one key → 200+ models (recommended), or:
ANTHROPIC_API_KEY=...
```

### Verify

```powershell
.\scripts\vragent.ps1 doctor      # expect green
.\scripts\vragent.ps1 mcp list    # desktop / quickbooks / karboncopy / vr-ledger enabled
```

---

## Quickstart

```powershell
# 1) Start the agent (CLI)
.\scripts\vragent.ps1

# 2) First day on the job — let it learn your firm + clients
#    run the firm-onboarding flow before any production work

# 3) Open the branded web dashboard
.\scripts\vragent.ps1 dashboard   # -> http://127.0.0.1:9119
```

> **First day:** run **`firm-onboarding`** before production work. It comes with 15 years of expertise but no knowledge of *your* firm until onboarded. Then load/seed client profiles with **`client-context`**.

---

## Command reference

> All commands run from the repo root. The launcher pins state (config, persona, skills, sessions, memory) inside the project via an in-repo `HERMES_HOME`.

| Command | What it does |
|---|---|
| `.\scripts\install.ps1` | Clone the engine, install, seed skills, build + brand the dashboard |
| `.\scripts\vragent.ps1` | Run the agent (interactive **CLI**) |
| `.\scripts\vragent.ps1 --tui` | Run the **terminal UI** |
| `.\scripts\vragent.ps1 doctor` | Health check |
| `.\scripts\vragent.ps1 dashboard` | Start the **web dashboard** → http://127.0.0.1:9119 |
| `.\scripts\vragent.ps1 model` | Switch provider / model |
| `.\scripts\vragent.ps1 mcp list` | List wired MCP tool servers |
| `.\scripts\vragent.ps1 gateway run` | Start the **Slack** (messaging) gateway |
| `.\scripts\sync-overlay.ps1` | Re-render config/persona/launchers into `home\` after edits |

### Configure (optional integrations)

| Setting | Where | Keys / steps |
|---|---|---|
| **Slack** | `home\.env` | `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN` |
| **Pixio** (media) | `home\.env` | `PIXIO_API_KEY` |
| **KarbonCopy** | its own `.env.local` | `KARBONCOPY_API_KEY`, `APP_ENCRYPTION_KEY`, `DATABASE_URL` |
| **QuickBooks live** | `vr-overlay\mcp\launchers\quickbooks.cmd.tmpl` | set `QB_LIVE=1` + `QB_COMPANY_FILE=...`, re-run `sync-overlay.ps1`, open QB Desktop with that file (first connection prompts a one-time QB authorization) |

---

## The skill catalog

**102 enabled skills.** The professional core is 16 SOP runbooks the agent actually follows:

| Bookkeeping & close | Tax | Specialized & systems |
|---|---|---|
| month-end-close | sales-tax-prep-filing | fixed-assets-depreciation |
| bank-reconciliation | sales-tax-nexus-determination | debt-loan-amortization |
| transaction-categorization | payroll-tax-prep-filing (941/940, EFTPS) | inventory-cogs-cycle |
| accounts-payable | year-end-close-1099 | deferred-revenue-recognition (ASC 606) |
| accounts-receivable | | new-client-onboarding |
| financial-statement-prep | | quickbooks-operating-guide |

### Firm / employee skills

| Skill | Role |
|---|---|
| `firm-onboarding` | First-day interview — learns your firm |
| `client-context` | Loads a client's profile before any work |
| `authority-and-escalation` | Trust tiers (Green / Yellow / Red) |
| `workpaper-standard` | Every task leaves a reviewable workpaper |
| `self-review-qc` | Self-checks its own output before handoff |
| `communication-cadence` | Keeps a professional comms rhythm |
| `proactive-routines` | Runs recurring work on its own |

Plus the wider library of **102** skills — image generation, web research, Google Workspace, finance modeling, document authoring, and more.

---

## The authority model — trustworthy by design

The gates aren't a caveat. They're the feature. **A good firm doesn't let a first-week hire wire money. Neither does this.** Every task is classified, and **every task leaves a reviewable workpaper**. Ambiguous or material items go to an **exceptions queue** — never guessed.

| Tier | Behavior | Examples |
|:---:|---|---|
| 🟢 **GREEN** | **Does it autonomously** | Read, categorize, reconcile, draft, prepare, analyze, write workpapers |
| 🟡 **YELLOW** | **Does it + tells you** | Routine, immaterial standard entries |
| 🔴 **RED** | **Prepares — you authorize** | Posting material/unusual journal entries · sending client emails · moving money · **submitting any tax or payroll filing** |

> On **RED**, the agent pre-fills the portal and assembles the workpaper. A human reviews and clicks **submit**. Keep these gates on in production.

---

## Architecture

```
VRAGENT/                         your overlay repo (path-portable)
├─ scripts/
│  ├─ install.ps1                clone engine · install · seed skills · build+brand dashboard
│  ├─ sync-overlay.ps1           render config/persona/launchers into home/
│  └─ vragent.ps1                launcher (pins an in-repo HERMES_HOME)
├─ home/                         state: config, persona, skills, sessions, memory, .env  (gitignored)
├─ hermes-agent/                 the open-source engine (NousResearch/hermes-agent)
└─ vr-overlay/                   persona · skills · config templates · MCP launchers (path-templated)

MCP servers (sibling projects under the same parent folder):
  Quickbooks MCP Desktop/   ·   KarbonCopy/   ·   RPA/ (desktop control)   ·   VR-Ledger/
```

- **Path-portable.** `install.ps1` and `sync-overlay.ps1` resolve every path at deploy time (`__VRAGENT_ROOT__`, `__PROJECTS_ROOT__`). The `C:\Users\…` paths don't need to match.
- **Self-contained state.** The launcher sets `HERMES_HOME` to the repo's `home\`, so config, persona, skills, sessions, and memory all live inside the project.
- **Sibling MCPs.** Place the four integration projects under the **same parent folder** as `VRAGENT`. If one is absent, that MCP simply won't start — comment it out of `vr-overlay/config/config.yaml.tmpl` and re-run `sync-overlay.ps1`.
- **Upstream stays updatable.** Your customization lives in `vr-overlay/`; the engine in `hermes-agent/` can be updated independently.

---

## Troubleshooting & FAQ

**`Hermes is not installed yet. Run: .\scripts\install.ps1`**
The venv/binary isn't built. Run `.\scripts\install.ps1` from the repo root.

**`doctor` isn't green.**
Confirm prereqs are on PATH (git · uv · Node 20 · npm · pnpm) and that `home\.env` has a valid `OPENROUTER_API_KEY` or `ANTHROPIC_API_KEY`.

**An MCP server is missing from `mcp list`.**
The matching sibling project isn't present under the parent folder. Add it, or comment it out of `vr-overlay/config/config.yaml.tmpl` and re-run `sync-overlay.ps1`.

**Will it touch my real books?**
No — the QuickBooks MCP runs in **safe simulation by default**. Live mode requires you to set `QB_LIVE=1` + `QB_COMPANY_FILE`, re-sync, open QB Desktop, and approve a one-time authorization.

**Will it file my taxes or move money without me?**
No. Those are **RED** actions: it prepares and pre-fills, then a human reviews and submits.

**Can I move it to another machine?**
Yes — paths are templated. See [`SETUP-NEW-MACHINE.md`](SETUP-NEW-MACHINE.md).

**The honest line.** The only two things it can't do out of the box: **(1)** run without an LLM key, and **(2)** act on real systems without that one-time connection and your sign-off on filings and money. By design.

---

<div align="center">

## Hire it today

It already has 15 years of experience. Give it one onboarding interview and it learns *your* firm.

```powershell
git clone https://github.com/RealDealCPA-VR/VR-Agent.git VRAGENT
cd VRAGENT
.\scripts\install.ps1
.\scripts\vragent.ps1            # then run firm-onboarding
```

**Onboard it this afternoon. Put it on the books by Monday.**

*The employee that reads, reconciles, prepares, and leaves the workpaper — you review and sign.*

</div>
