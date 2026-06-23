# Build Spec — RealDeal CPA on Claude Code

Technical architecture + phased plan. Config formats verified against Claude Code docs as of
2026-06-23 (links at the end). **Re-verify against live docs at build time** — a few details were
in flux (plugin versioning, tool-search defaults).

---

## 1. Architecture overview
Claude Code is the agent runtime. The agent = **CLAUDE.md (persona/context) + skills (knowledge)
+ subagents (the fleet) + MCP servers (tools) + hooks (deterministic guardrails)**, packaged as a
**plugin**, authenticated to the **Max subscription** via `claude login`. A separate small web app
provides the **Command Center**.

```
realdealcpa-cc/                      # the new build (a git repo / Claude Code plugin)
├── .claude-plugin/plugin.json       # plugin manifest
├── CLAUDE.md                        # "Remy" persona + firm context (always in context)
├── .mcp.json                        # the 9 MCP servers (standard MCP)
├── settings.json                    # hooks (authority gates), statusline, defaults
├── skills/                          # 47 skills -> <name>/SKILL.md
│   ├── month-end-close/SKILL.md
│   ├── deliverable-verification/SKILL.md
│   └── ...
├── agents/                          # the fleet -> <name>.md
│   ├── bookkeeping.md  payroll.md  tax.md  sentinel.md  review.md
├── hooks/
│   └── authority-gate.py            # PreToolUse: deny/ask on RED actions
├── mcp/                             # the 7 in-repo FastMCP servers (unchanged Python)
│   ├── vr-verify/server.py  vr-provenance/server.py  ... desktop-control/server.py
├── bin/                             # launchers for external servers (quickbooks, karboncopy)
├── routines/                        # headless schedules (claude -p prompts + cron/Task Scheduler)
└── command-center/                  # standalone web app (reused canvas + new backend)
    ├── server.py   fleet_state.py   web/CommandCenterPage.tsx
```

---

## 2. Subsystem specs

### 2.1 MCP servers — `.mcp.json`
Project-scope file at repo root. Standard MCP; the existing FastMCP Python servers run unchanged.
```json
{
  "mcpServers": {
    "vr-verify":     { "type": "stdio", "command": "${CLAUDE_PROJECT_DIR}/.venv/Scripts/python.exe",
                       "args": ["${CLAUDE_PROJECT_DIR}/mcp/vr-verify/server.py"], "timeout": 120000 },
    "vr-provenance": { "type": "stdio", "command": "${CLAUDE_PROJECT_DIR}/.venv/Scripts/python.exe",
                       "args": ["${CLAUDE_PROJECT_DIR}/mcp/vr-provenance/server.py"], "timeout": 120000 },
    "vr-ledger":     { "type": "stdio", "command": "...python", "args": ["...vr-ledger/server.py"] },
    "vr-cohort":     { "type": "stdio", "command": "...python", "args": ["...vr-cohort/server.py"] },
    "vr-risk":       { "type": "stdio", "command": "...python", "args": ["...vr-risk/server.py"] },
    "vr-capacity":   { "type": "stdio", "command": "...python", "args": ["...vr-capacity/server.py"] },
    "desktop":       { "type": "stdio", "command": "...python", "args": ["...desktop-control/server.py"] },
    "quickbooks":    { "type": "stdio", "command": "cmd", "args": ["/c", "${CLAUDE_PROJECT_DIR}/bin/quickbooks.cmd"] },
    "karboncopy":    { "type": "stdio", "command": "cmd", "args": ["/c", "${CLAUDE_PROJECT_DIR}/bin/karboncopy.cmd"] }
  }
}
```
- `timeout` is **milliseconds** (Hermes used seconds — convert).
- `${CLAUDE_PROJECT_DIR}` is provided to stdio servers/hooks; use it for portability instead of
  absolute paths. Runtime data dirs come from an env var the servers read (carry the
  `HERMES_HOME`-style pattern; rename the env var if desired).
- Verify: `claude mcp list` and exercise one tool from each server.
- If the agent needs all tools visible at once: `ENABLE_TOOL_SEARCH=false` (note: not on Haiku).

### 2.2 Persona & context — `CLAUDE.md` (+ system prompt for hard rules)
- Project `CLAUDE.md` holds the "Remy" persona, firm context, the authority-tier *policy* (human
  reading), and pointers (`@skills/...`) — concatenated into context automatically.
- Hard, non-negotiable rules also go to the **system prompt** at launch:
  `claude --append-system-prompt "You never imply to a client or regulator that you are a licensed
  human CPA. You never self-authorize a RED action."` (Context alone is advisory; this is firmer.)
- Enforcement of RED is in hooks (next), not prose.

### 2.3 Authority gates — `PreToolUse` hooks (the safety upgrade)
`settings.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "mcp__quickbooks__.*|mcp__vr-ledger__.*|Bash",
        "hooks": [ { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/hooks/authority-gate.py" } ] }
    ]
  }
}
```
`hooks/authority-gate.py` reads the tool call on stdin and returns a decision:
```python
# stdin: {"tool_name": "...", "tool_input": {...}, ...}
# RED triggers: posting JEs, paying/transferring money, submitting any filing, voids/locks,
#               sending client comms. -> deny (or "ask") with a reason.
import sys, json
data = json.load(sys.stdin)
name, ti = data["tool_name"], data.get("tool_input", {})
RED = is_posting_or_filing_or_money(name, ti)   # implement against the real tool names
if RED:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",   # force human approval; "deny" to hard-block
        "permissionDecisionReason": "RED action — requires partner sign-off (authority policy)."}}))
sys.exit(0)
```
- Exit code 2 also blocks (reason on stderr); JSON `permissionDecision` is the structured path.
- This makes GREEN/YELLOW/RED **deterministic** — the core win over the current prompt-only gate.

### 2.4 Skills — `skills/<name>/SKILL.md`
- Convert the 47 skills with a one-time script: keep `name`/`description`, drop
  `metadata.hermes.*` and `related_skills`, optionally add `allowed-tools`,
  `disable-model-invocation: true` for human-only runbooks, `context: fork` for heavy ones.
- Bodies stay < 500 lines (already true). Bundle templates/examples in the skill dir.
- Discovery is automatic (model-invoked by `description`) + `/realdealcpa:<skill>` when packaged.

### 2.5 Subagents — `agents/<name>.md`
Example (the adversarial reviewer — note the different model for true independence):
```markdown
---
name: review
description: Independent adversarial reviewer. Use before any RED sign-off. Tries to BREAK the deliverable.
tools: Read, Bash, mcp__vr-verify__*, mcp__vr-provenance__*
model: sonnet            # different model than the preparer; blind to prep reasoning
skills: [adversarial-review, deliverable-verification]
maxTurns: 20
---
You are an independent reviewer. You receive ONLY the deliverable + evidence, never the
preparer's reasoning. Try to disprove every number and conclusion. Surface dissent as exceptions.
```
- Build: bookkeeping, payroll, tax, sentinel (portal/rule watch), review. Each isolated context.

### 2.6 Headless routines — `routines/` + OS scheduler
- Each routine is a `claude -p` invocation, scheduled by Windows Task Scheduler / cron:
```
claude -p "Daily AM standup: deadlines at risk, AP/AR aging deltas, overnight bank activity.
           Deliver a digest. Do not post, file, or move money." \
  --allowedTools "Read,Bash,mcp__quickbooks__*,mcp__karboncopy__*,mcp__vr-ledger__*" \
  --permission-mode default --output-format json --max-turns 30
```
- The authority hook still applies (RED stays blocked even headless). Keep routines lean —
  they consume subscription usage.

### 2.7 Command Center — standalone web app (reuse the canvas)
- **Frontend:** reuse `web/CommandCenterPage.tsx` (React Flow node canvas) nearly as-is; point its
  API base at the new backend.
- **Backend:** `command-center/server.py` (FastAPI) + `fleet_state.py`. The "fleet" = your defined
  subagents (static from `agents/`) + live work state. Live state is written by a small
  `Stop`/`PostToolUse` hook (or a tiny MCP) into a JSON file the backend reads and serves at
  `/api/command-center/state` (same shape the canvas already consumes: agents/edges/work).
- Runs as its own process/port; independent of Claude Code. Add/inspect agents = edit `agents/`.

### 2.8 Packaging — one plugin
`.claude-plugin/plugin.json`:
```json
{ "name": "realdealcpa", "description": "RealDeal CPA internal accounting agent",
  "version": "1.0.0", "author": { "name": "RealDeal CPA" }, "license": "MIT" }
```
- Plugin auto-loads `skills/`, `agents/`, `hooks/`, `.mcp.json` when enabled. Distribute via a
  **private** git repo; install with `/plugin marketplace add <repo>` then `/plugin install realdealcpa`.
- Set an explicit `version` (omit → every commit SHA is a new version).

### 2.9 Auth & setup
- `claude login` (OAuth) → uses the **Max subscription**. No API key, no `.env` secret for the model.
- External tool secrets (QuickBooks/Karbon) live in their launchers' own env, gitignored — never committed.

---

## 3. Phased build plan
Each phase has a deliverable + an acceptance test. Build in order (it's the critical path).

| Phase | Deliverable | Acceptance |
|---|---|---|
| **0. Scaffold + auth** | repo skeleton, `.venv`, `claude login` on Max | `claude -p "hello"` runs on the subscription |
| **1. MCP** | `.mcp.json` with all 9 servers; copy the 7 Python servers + 2 launchers | `claude mcp list` green; one tool from each callable |
| **2. Persona** | `CLAUDE.md` (Remy) + `--append-system-prompt` hard rules | agent answers in the Remy register; states the no-deception rule |
| **3. Authority hooks** | `hooks/authority-gate.py` + `settings.json` | a posting/filing/money tool call is blocked/asked; GREEN flows free |
| **4. Skills** | 47 skills converted to `skills/<name>/SKILL.md` | skills discoverable; a tax + a close skill trigger correctly |
| **5. Subagents** | the 5 fleet agents | adversarial `review` runs blind on a sample deliverable |
| **6. Routines** | 3–4 headless schedules (standup, weekly digest, close kickoff, sentinel) | a scheduled `claude -p` runs and delivers; RED stays blocked |
| **7. Command Center** | standalone app (reused canvas + state hook backend) | canvas shows the fleet + live work; add-agent reflects `agents/` |
| **8. Package** | the plugin | clean-machine install via `/plugin install`; end-to-end task works |

**End-to-end acceptance (the whole build):** "Reconcile the operating account for last month and
produce a workpaper" — uses QuickBooks + vr-verify (numbers re-derived) + vr-provenance (evidence
+ hash-chained log), the RED gate blocks the final post until you approve, and the Command Center
shows the work — **all running on the Max subscription.**

---

## 4. Open decisions (resolve before/while building)
1. **Rename the runtime env var?** (`HERMES_HOME` → e.g. `REALDEALCPA_HOME`) — cosmetic; the servers
   just need *an* env-provided runtime dir. Decide and apply consistently.
2. **Holographic memory** — drop (default) or rebuild as a memory MCP? (Non-blocking; start without.)
3. **Command Center state transport** — `Stop` hook writing JSON vs a tiny `vr-fleet` MCP. (Hook is simpler.)
4. **How aggressive are the headless routines?** — scope to fit subscription usage limits.
5. **Plugin distribution** — private git repo (recommended) vs local `--plugin-dir`.

## 5. References (verify at build time — current as of 2026-06-23)
- MCP: https://code.claude.com/docs/en/mcp
- Skills: https://code.claude.com/docs/en/skills
- Subagents: https://code.claude.com/docs/en/sub-agents
- Hooks: https://code.claude.com/docs/en/hooks-guide
- Memory: https://code.claude.com/docs/en/memory
- Headless: https://code.claude.com/docs/en/headless
- Plugins: https://code.claude.com/docs/en/plugins
