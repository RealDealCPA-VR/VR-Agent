# Inventory & Port Map — Hermes build → Claude Code build

A precise account of **what exists today** and **where each piece lands** on Claude Code.
Source of truth for "what the agent does" is the current `vr-overlay/` in the parent project.

Legend: ✅ ports clean · 🟡 re-expressed (same intent, new mechanism) · 🔴 rebuilt · ⛔ dropped

---

## A. Current build inventory (as of 2026-06-23)

**MCP tool servers — 9** (223 tools total)
| Server | Tools | Kind | Notes |
|---|---|---|---|
| desktop (desktop-control) | 14 | in-repo FastMCP (Python) | Windows GUI control (wraps RPA) |
| quickbooks | 150 | external (launcher) | QuickBooks Desktop; sim + live |
| karboncopy | 33 | external (launcher) | practice management |
| vr-ledger | 7 | in-repo FastMCP | plain-text double-entry |
| vr-verify | 6 | in-repo FastMCP | deterministic re-derivation (no LLM) |
| vr-provenance | 4 | in-repo FastMCP | SHA-256 evidence + hash-chained ledger + dossier |
| vr-cohort | 3 | in-repo FastMCP | private cross-client benchmark |
| vr-risk | 3 | in-repo FastMCP | liability/exposure ledger |
| vr-capacity | 3 | in-repo FastMCP | realization + surge triage |

**Skills — 47 custom** (the framework reports 117 enabled = 47 custom + ~70 Hermes built-ins)
- sop: 17 · firm: 12 · quality: 7 · accounting: 2 · advisory: 2 · practice: 2 ·
  creative: 1 · desktop: 1 · email: 1 · marketing: 1 · tax: 1

**Persona / behavior**
- `SOUL.md` — the "Remy" persona (hot-reloaded each message in Hermes).
- Authority tiers GREEN/YELLOW/RED (in `firm/authority-and-escalation`).
- Workpaper standard, adversarial review, deliverable verification, provenance (quality skills).

**Memory**
- `home/memories/MEMORY.md` + `USER.md`; holographic semantic provider (local SQLite).

**Interfaces**
- CLI/TUI (skin-branded), web dashboard (:9119) + the **Command Center** tab, Slack gateway.

**The Command Center** (`vr-overlay/command-center/`)
- `fleet.py` (data layer), `fleet.seed.json`, `web_routes.py` (FastAPI), `web/CommandCenterPage.tsx`
  (React Flow node canvas). Embedded in the Hermes dashboard.

**Scripts — 11** (install, sync-overlay, brand-web, install-command-center, snapshot-state,
glassbox, optimize-skills, promote-skills, vragent, …) — PowerShell + Python.

**Config** — `config.yaml.tmpl`: model claude-opus-4.5, reasoning_effort high, holographic
memory, curator, delegation, platform toolsets, the 9 MCP servers, display skin + dashboard theme.

---

## B. Port map

### MCP servers → `.mcp.json` ✅ (the cleanest win)
Claude Code speaks **standard MCP**. The 7 in-repo FastMCP stdio servers run **unchanged**;
only the registration moves from `config.yaml`'s `mcp_servers:` (YAML) to `.mcp.json`
(`mcpServers`, JSON, `"type":"stdio"`, command/args/env, `timeout` in ms). The 2 external
servers (quickbooks, karboncopy) register the same way (their launcher commands).
- **Effort:** low. Mechanical YAML→JSON translation of 9 entries. Test with `claude mcp list`.
- **Gotcha:** Claude Code defers tool definitions via tool-search by default; set
  `ENABLE_TOOL_SEARCH=false` if the agent needs all ~223 tools visible upfront (and note Haiku
  doesn't support tool search). The vr-* path fix (use `HERMES_HOME`/env, not a path relative to
  `__file__`) already landed — keep servers writing runtime data under an env-provided dir.

### Skills (47) → `.claude/skills/<name>/SKILL.md` ✅ / 🟡
SKILL.md format is shared. Each ports with **frontmatter edits**:
- Keep: `name`, `description` (Claude Code merges `description`+`when_to_use` ≤ ~1536 chars).
- Map: Hermes `metadata.hermes.tags` / `related_skills` → drop (Claude Code ignores; optionally
  fold "related" into the description prose). Add Claude Code fields as useful:
  `allowed-tools`, `disable-model-invocation` (for human-only runbooks), `model`, `context: fork`.
- Keep bodies under ~500 lines (already true); supporting files (templates/examples) allowed.
- **Effort:** medium but highly mechanical — a one-time conversion script over the 47 dirs.
- **Decision:** ship them as **plugin skills** (namespaced `/realdealcpa:<skill>`) for clean packaging.

### Persona (SOUL.md) → `CLAUDE.md` + `--append-system-prompt` ✅ / 🟡
- Put the "Remy" persona in the project `CLAUDE.md` (always in context).
- For the **hard rules** (never deceive a client/regulator; never self-authorize RED), also pass
  `--append-system-prompt` (or `--system-prompt`) so they're system-level, not just context.
- **Note:** CLAUDE.md is *context, not enforced*. Enforcement lives in hooks (below).

### Authority tiers (GREEN/YELLOW/RED) → `PreToolUse` hooks 🟡 (an UPGRADE)
- Today RED is a prompt instruction (soft). On Claude Code, a `PreToolUse` hook in
  `settings.json` matches money/posting/filing tools and returns
  `{"permissionDecision":"deny"}` (or `"ask"`) — **deterministic**, can't be prompted away.
- Match patterns: any `qb_*_create`/post/void, any payment/transfer, any filing submit, period
  locks, sending client comms. Block → route to an exceptions queue note; require explicit human ok.
- **Effort:** medium. This is the highest-value improvement in the whole migration — do it well.

### Specialized agents (the fleet) → `.claude/agents/<name>.md` ✅
- bookkeeping, payroll, tax, sentinel (portal watch), review (adversarial) → subagents with
  `name`, `description`, `tools`, `model`, `skills:`, `mcpServers:`. Isolated context by default.
- The **adversarial review** subagent is a natural fit (different model via `model:`, blind to prep).
- **Effort:** low-medium.

### Proactive routines (Hermes cron) → OS scheduler + `claude -p` 🟡
- Replace Hermes cron with Windows Task Scheduler / cron calling headless:
  `claude -p "run the daily AM standup" --allowedTools "Read,Bash,mcp__*" --permission-mode default --output-format json`.
- Keep them GREEN-only (read/draft/deliver; never post/file/move money — enforced by the hook).
- **Effort:** medium (rebuild the schedule + the prompts as headless commands).
- **Watch:** headless runs count against subscription usage limits — keep them lean.

### Memory (MEMORY.md/USER.md + holographic) → `CLAUDE.md` + notes 🟡 / ⛔
- Durable facts → `CLAUDE.md` / `CLAUDE.local.md` (gitignored) + per-client `.claude/` notes.
- Holographic semantic recall → **dropped** by default (Claude Code has no equivalent). If
  semantic recall matters, add a small **memory MCP server** later (optional, non-blocking).
- **Effort:** low (simplification).

### Command Center → standalone web app 🔴 (largest item; ~70% reusable)
- The React Flow canvas (`web/CommandCenterPage.tsx`) is **reusable as-is**.
- Rebuild the **backend**: a thin FastAPI app whose "fleet" maps **Claude Code subagents +
  running sessions** to nodes (instead of Hermes `fleet.json`). Subagents can write their
  state to a JSON file (via a `PostToolUse`/`Stop` hook or a tiny MCP) that the backend reads.
- It runs as its own process (`python server.py` → its own port), independent of Claude Code.
- **Effort:** high-ish, but bounded — frontend done, backend is a small read-model + a state hook.

### Branding (skin engine + dashboard theme) → status line + output 🟡
- CLI branding → `/statusline` config (limited, predefined fields) + persona tone in CLAUDE.md.
- No skin-engine equivalent; the rich CLI banner/colors don't fully carry. Accept a lighter touch.
- **Effort:** low (and lower fidelity than today).

### Multi-provider brain ⛔
- Dropped intentionally — Claude Code is Claude-only, which is the whole point.

### Curator / skill-tuner / self-improvement loop 🟡
- Hermes' background curator/nudges have no direct equivalent. Approximate with a scheduled
  `claude -p` "maintenance" run that reviews recent corrections and proposes skill edits (human
  approves). **Effort:** medium; can be a later phase.

### Slack gateway 🔴 / ⛔
- No built-in equivalent. Defer; if needed later, a separate Slack→`claude -p` bridge.

### Packaging → one Claude Code **plugin** ✅
- Bundle `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `CLAUDE.md`, `bin/` scripts, and
  `.claude-plugin/plugin.json` into one installable plugin. Distribute via a (private) git repo.
- **Effort:** low once the parts exist; gives a clean one-command install.

---

## C. Effort roll-up (rough)
| Bucket | Items | Relative effort |
|---|---|---|
| Mechanical ports | MCP config, skills conversion, subagents, persona, plugin packaging | **Small–Medium** |
| Real engineering | Authority-gate hooks, headless routines, Command Center backend | **Medium–High** |
| Dropped/deferred | multi-provider, holographic memory, skin engine, curator, Slack | n/a |

**Critical path:** MCP config → persona/CLAUDE.md → authority hooks → skills → subagents →
headless routines → Command Center → plugin packaging. (Detailed phases in BUILD-SPEC.)
