# RealDeal CPA — Remarkable Roadmap (fan-out-ready)

Turning the "truly remarkable" ideas into work. **Every task is scoped so one agent finishes
it well within ~60% of its context window** — minimal reads, a single output artifact, and a
concrete acceptance test. That keeps fan-out parallel and avoids context rot.

## How to fan this out
- Give each agent **only** its task block. Do not hand it the whole repo.
- **Templates** an agent may read to match conventions (these are the *only* ambient reads):
  - Skill format → `vr-overlay/skills/firm/colleague/SKILL.md`
  - MCP server (FastMCP, stdio) → `vr-overlay/mcp/vr-ledger/server.py`
  - PowerShell script → `scripts/sync-overlay.ps1` (ASCII-only; PS 5.1 mis-parses non-ASCII)
  - Real MCP tool names (never fabricate) → `.audit/realtools.md`
- **Conventions:** skills are `vr-overlay/skills/<cat>/<name>/SKILL.md` (auto-discovered);
  MCP servers are pure-Python FastMCP over stdio (only `mcp`, `hashlib`, `decimal`, `json`,
  stdlib); scripts ASCII-only. Authority gates (GREEN/YELLOW/RED) and the no-client-deception
  guardrail are invariant — never weaken them.
- **Integration tasks** (wire an MCP into `config.yaml.tmpl`, run `sync-overlay`, `mcp test`)
  are done by the orchestrator in the main loop, not by a fan-out agent.

Legend: `[skill]` `[mcp]` `[script]` `[integration]` `[moonshot]` · context `S` (~1 file) `M` (~2-3 files).

---

## WAVE 1 — The Provable-Trust Trilogy (build first; highest leverage)

### Epic E1 — Deterministic verification spine (the math leaves the LLM)
**T1.1 `[mcp] M` — `vr-verify` server.** Build `vr-overlay/mcp/vr-verify/server.py` (FastMCP stdio).
Pure-Decimal, NO LLM. Tools: `check_balanced(je_json)` (Dr==Cr to the cent, returns variance),
`check_ties(spec_json)` (recompute each tie: expected vs actual, list pass/fail + variance),
`foot(rows_json)` (sum a column, return total), `recompute_depreciation(method, basis, life, salvage, period)`
(SL/DDB/units), `recompute_loan_payment(principal, annual_rate, term_months, payment_no)` (principal/interest split),
`reroll_retained_earnings(beginning, net_income, distributions, other_json)`. Read: vr-ledger server template.
Accept: `python -c` runs `check_balanced` on a balanced and an unbalanced JE (pass / fail+variance), and `recompute_depreciation` SL ties to hand-calc.

**T1.2 `[skill] M` — `deliverable-verification` skill.** `vr-overlay/skills/quality/deliverable-verification/SKILL.md`.
Defines the side-artifact "verification spec" the agent emits for every numeric deliverable (the JEs,
the tie-out table, the recompute params) and mandates running the `vr-verify` tools BEFORE asserting any
number; a number that the spine didn't confirm is not "done". Read: colleague skill + T1.1 tool list.
Accept: skill parses; references only real vr-verify tools; gates intact.

**T1.3 `[skill] M` — re-perform manifest.** Edit `vr-overlay/skills/quality/workpaper-standard/SKILL.md`
to embed a machine-executable manifest in each workpaper (the exact tool calls + params + source-doc
SHA-256 hashes), so a workpaper can be **re-performed and diffed** later. Add a `reperform` convention.
Read: workpaper-standard. Accept: edited skill parses; manifest template present.

### Epic E2 — Adversarial independent review
**T2.1 `[skill] M` — `adversarial-review` skill.** `vr-overlay/skills/quality/adversarial-review/SKILL.md`.
Before any RED sign-off, spawn an INDEPENDENT reviewer via the delegation toolset — **different model**
(multi-provider brain), **blind to the preparer's reasoning**, given only the deliverable + evidence
bundle — whose sole mandate is to BREAK the conclusion (re-pull sources, hunt the split-to-dodge-
materiality, the self-referential tie, the empty exceptions queue on a messy month). Disagreements →
exceptions. Read: authority-and-escalation + self-review-qc. Accept: parses; describes a genuinely blind/
independent pass (not same-model self-grading); related_skills resolve.

**T2.2 `[skill] S` — wire adversarial pass into the RED gate.** Edit
`vr-overlay/skills/firm/authority-and-escalation/SKILL.md` so RED items require an `adversarial-review`
verdict before the human sign-off request. Read: authority-and-escalation. Accept: edited skill parses.

### Epic E3 — Cryptographic provenance & defensibility
**T3.1 `[mcp] M` — `vr-provenance` server.** Build `vr-overlay/mcp/vr-provenance/server.py` (FastMCP).
stdlib only (`hashlib`, `json`, `pathlib`). Tools: `record_read(source, content)` (SHA-256, write an
evidence bundle under `home/provenance/evidence/`), `append_event(event_json)` (append to a **hash-chained**
log `home/provenance/ledger.jsonl` where each entry stores `prev_hash`+`hash`), `verify_chain()` (recompute
the chain; report first break), `build_dossier(client, period)` (assemble ledger slice + evidence index into
`home/provenance/dossiers/<client>-<period>.json`). Read: vr-ledger server template. Accept: append 3 events
→ `verify_chain` ok; hand-edit one ledger line → `verify_chain` reports the break.

**T3.2 `[skill] M` — `provenance-and-evidence` skill.** `vr-overlay/skills/quality/provenance-and-evidence/SKILL.md`.
When you read a source for a number, `record_read` it; log each consequential action via `append_event`;
on demand `build_dossier` for an audit/exam/peer-review. Frame the AI-vs-human disclosure as a FEATURE
recorded in the ledger. Read: workpaper-standard + T3.1 tools. Accept: parses; gates intact.

---

## WAVE 2 — Compounding moat & continuous operation

### Epic E4 — Cross-client private benchmark mesh (the data flywheel)
**T4.1 `[mcp] M` — `vr-cohort` server.** `vr-overlay/mcp/vr-cohort/server.py`. Local SQLite. Tools:
`add_observation(naics, metric, value, client_hash)` (store de-identified feature; never the client name),
`cohort_stats(naics, metric)` (mean/stdev/quartiles across the firm's own book), `score(naics, metric, value)`
(z-score + percentile vs cohort). All local, never pooled externally. Accept: add 5 obs, `score` returns a sane sigma.
**T4.2 `[skill] M` — `cohort-benchmarking` skill.** Per close, feed de-identified metrics to `vr-cohort` and
flag outliers ("3.2σ vs your 14 retail clients"). Privacy wall: only abstracted signal crosses clients.
**T4.3 `[skill] S` — nightly cohort routine.** Add a `hermes cron add` job to `proactive-routines` that
maintains the cohort model and runs a per-client peer-anomaly pass.

### Epic E5 — Continuous close / living financials
**T5.1 `[skill] M` — `continuous-close` skill.** A persistent per-client close-state machine (what's tied,
what's open, what's drifting) that never resets; an "audit-readiness %" that asymptotes to 100% daily.
**T5.2 `[skill] S` — event-driven incremental-close routine.** A frequent cron that does an incremental
recon+categorize+accrual pass on new QB activity so books are reconciled-through-yesterday.

### Epic E6 — Owner operating-rhythm model
**T6.1 `[skill] M` — `owner-rhythm` skill.** Build a private behavioral model of the OWNER as a decision-maker
(what he always approves vs pushes back on, revealed risk tolerance, the questions he asks each quarter),
stored at `home/memories/owner-rhythm.md`. Anticipate instead of asking what's predictable.

---

## WAVE 3 — Capacity, risk, continuity

### Epic E7 — Review-tier mode (the inversion: be REVIEW capacity, not prep)
**T7.1 `[skill] M` — `review-tier` skill.** Ingest work prepared by HUMAN staff (their close/return/workpapers
from QB/Karbon) and REVIEW it — ties, nexus triggers, missed safe-harbors, the source doc that doesn't support
the entry — multiplying the firm's scarce partner-review hours. Output a reviewer's notes packet, never a sign-off.

### Epic E8 — Liability / exposure meter
**T8.1 `[mcp] M` — `vr-risk` server.** Running exposure ledger: `log_decision(tier, area, dollars, penalty_exposure)`,
`exposure_summary(client, period)` (aggregate — catches 200 immaterial decisions becoming a restatement),
`threshold_breached()`. Local SQLite/JSON. Accept: log 3 decisions → summary aggregates dollars + flags a breach.
**T8.2 `[skill] S` — `liability-meter` skill.** Feed each GREEN/YELLOW/RED decision to `vr-risk`; surface
accumulated exposure to the partner before it compounds.

### Epic E9 — Succession / continuity proof
**T9.1 `[script] M` — `snapshot-state.ps1`.** Sign + version a snapshot of the learned "employee" (promoted
skills, client precedents, memory) so it survives a model swap and you can prove "I didn't silently change last
year": tar + SHA-256 manifest under `home/snapshots/<date>/`, ASCII-only. Accept: PS parser clean; produces a snapshot + manifest.
**T9.2 `[skill] S` — `continuity` skill.** When to snapshot (each close/quarter), how to diff two snapshots, and
how to answer "prove last year's treatment" from a snapshot.

### Epic E10 — Portal & rule sentinel
**T10.1 `[skill] M` — `portal-sentinel` skill.** Point the headless browser + desktop vision at IRS/state DOR
portals, EFTPS, the QB UI, e-file schemas, and client bank/payroll portals; daily login (within access rules) +
screenshot + diff vs yesterday; flag a changed rate/schema/threshold. Read-only; client-facing actions stay RED.
**T10.2 `[skill] S` — daily sentinel routine.** A `hermes cron add` job that runs the sentinel diff and flags changes.

---

## WAVE 4 — Client experience (bigger builds)

### Epic E11 — Client glass-box portal `[moonshot]`
Extend the web dashboard into a client-facing glass box: every statement figure hyperlinks down through
workpaper → tool calls → source doc → bank line, backed by the `vr-provenance` ledger, with a public
AI-vs-human provenance record. Decompose later into: T11.1 provenance API endpoint, T11.2 trace-graph UI,
T11.3 "ask your books" surface answering only from traced evidence. Needs a web build (edit `hermes-agent/web`,
recapture via a `brand-web`-style script).

### Epic E12 — Capacity-as-a-dial `[moonshot]`
Real-time firm-wide realization + surge-staffing engine that reallocates Remy's effort during busy season to
protect margin (Karbon budget-vs-actual + deadline proximity + completion state). Needs live Karbon time data;
decompose after E4/E5 land.

---

## Dependency / wave order
- **Wave 1 first** (E1, E2, E3) — the trust spine; E3 (provenance) underpins E11.
- **Wave 2** (E4, E5, E6) — moat + continuous ops; E4 feeds E12.
- **Wave 3** (E7, E8, E9, E10) — capacity/risk/continuity; mostly independent, parallelizable.
- **Wave 4** (E11, E12) — last; depend on E3/E4/E5 and a web build.
