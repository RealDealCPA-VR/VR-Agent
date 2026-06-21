---
name: provenance-and-evidence
description: "The firm's tamper-evident evidence ledger: record_read every source you pull a number from, append_event for every consequential action (tool call, JE prepared, approval requested/granted, gate classification, money/filing action, exception), verify_chain to prove the record was never altered, and build_dossier(client, period) to assemble a regulator/exam/peer-review-ready package on demand. Load this whenever you touch client numbers or take a consequential action — it is the cryptographic backbone under the workpaper standard. Treats the AI-vs-human disclosure not as a footnote but as a FEATURE recorded immutably: who acted (agent) and who authorized (human) is captured in the chain, honoring the no-client-deception guardrail by construction."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Provenance, Evidence, Audit-Trail, Hash-Chain, Tamper-Evident, Dossier, Disclosure, Quality-Control]
    related_skills: [workpaper-standard, deliverable-verification, adversarial-review, authority-and-escalation]
---

# Provenance & Evidence

A workpaper says *what* you did and *why* the conclusion holds. The provenance
ledger proves it — cryptographically, in order, and unforgeably. Every number you
rely on is tied to the source you pulled it from; every consequential action is
appended to a hash-chained event log that cannot be edited after the fact without
detection. If the workpaper is the narrative, the provenance ledger is the
black-box flight recorder underneath it. Use the `vr-provenance` MCP for both.

The four tools, and nothing you have to fabricate:
- `record_read` — register a source you read a number from (system, document, report run + parameters, statement, screenshot path) and the value/scope you took.
- `append_event` — append one consequential action to the hash-chained ledger.
- `verify_chain` — recompute the chain and confirm no entry was altered, inserted, or removed.
- `build_dossier(client, period)` — assemble the recorded reads + events into a single exam-ready package.

## When to use
- You are about to **pull a number** from any system into a JE, schedule, recon, or comm → `record_read` the source first.
- You take any **consequential action** → `append_event` it as you do it, not in a batch afterward.
- A reviewer, partner, regulator, or peer-review/exam team asks for **support** → `build_dossier(client, period)`.
- Before a handoff, a RED gate, or any claim that the record is complete → `verify_chain`.

## record_read — provenance for every input
Before a number enters your reasoning, record where it came from. A reviewer must
be able to re-pull the exact same value.
- Record the **system + the call**: e.g. `qb_general_ledger` with its date range and basis, `qb_trial_balance_export`, `qb_bill_list`, a bank statement date, an invoice #, a `screenshot` path of a portal, a vr-ledger `balance_of` result.
- Record the **value/scope you took** (the balance, the line, the page), not "I looked at QB."
- One read = one source. If you tie A to B, that's two `record_read` calls, then an `append_event` for the tie.
- Re-run, don't reuse, a source whose parameters differ from the period — and record the new read. A stale read is a silent error.

## append_event — every consequential action, in order
Append, never edit. The ledger is the timeline of what the agent actually did.
Record at minimum:
- **Tool calls that change state or money** — `qb_journal_entry_create`, `qb_bill_pay`, `qb_check_create`, `qb_transfer_create`, `qb_sales_tax_payment_create`, `qb_invoice_create`.
- **JEs prepared** (even before posting) — what, why, the supporting reads (cross-ref the `record_read` ids).
- **Approval lifecycle** — approval *requested* (RED gate raised), and approval *granted/denied* by the human partner. Both are events; the grant names the human authorizer.
- **Gate classifications** — every GREEN / YELLOW / RED decision and the basis for it.
- **Money & filing actions** — anything that moves funds or submits a tax/payroll filing.
- **Exceptions** — every item routed to the EXCEPTIONS QUEUE, with its cross-reference.
Each event carries: actor (`RealDeal CPA (agent)`), timestamp, action, the inputs it relied on (read ids), and the outcome. The chain links each event to the prior one's hash — that's what makes after-the-fact tampering detectable.

## Disclosure is a feature, not a footnote (the hard guardrail, by construction)
The no-client-deception line is INVARIANT: client- and regulator-facing output
never implies a licensed human did the work that the agent did. The provenance
ledger *enforces* this rather than relying on memory.
- Every event records **who acted** — the agent — and every approval records **who authorized** — the named human partner. The separation of "prepared by agent" from "authorized by human" is written into the immutable record, not asserted after the fact.
- The dossier therefore *shows*, on its face, exactly which steps were AI-performed and which were human-signed. That transparency is the selling point to an exam or peer-review team, not a liability to bury.
- Never append an event that attributes agent work to a human, or backdate/reword an action to look human-performed. That is the cardinal sin here and it defeats the entire purpose of the chain.

## verify_chain — prove no tampering
Run `verify_chain` and confirm it passes before you assert the record is complete:
at handoff, before a RED gate, before building a dossier, and on a periodic
cadence (e.g. each close, each standup sweep). A passing verify is itself worth an
`append_event`. A **failing** verify is a stop-the-line event — the record's
integrity is in question; do not proceed, do not "repair" silently, escalate to
the human partner immediately as a RED exception. You never edit history to make
the chain re-verify; a broken chain is a finding, not a chore.

## build_dossier — the exam-ready package
On demand, `build_dossier(client, period)` collects the recorded reads and the
event chain into one regulator/exam/peer-review-ready bundle. Use it when:
- A reviewer or partner asks for support for a client/period.
- A regulator, IRS exam, or financial-statement audit requests the trail.
- A peer review samples the engagement.
Before you deliver a dossier: `verify_chain` first (a dossier over an unverified
chain is worthless), confirm the client + period scope match the request, and
cross-reference the dossier back to the relevant workpaper indexes (`A-1`, `PR-3`,
…) so the narrative and the evidence line up. The dossier complements the
workpaper; it does not replace `workpaper-standard`.

## Procedure
1. **Read → record.** Before any number enters your work, `record_read` the source with its parameters and the value/scope taken.
2. **Act → append.** As you perform each consequential action, `append_event` it, citing the read ids it relied on.
3. **Classify → append.** Log every GREEN/YELLOW/RED gate decision and its basis.
4. **Approvals → append both sides.** Event for the request (RED raised); event for the human grant/denial, naming the authorizer.
5. **Verify** with `verify_chain` at handoffs, before RED gates, and on cadence; append the result.
6. **Dossier** with `build_dossier(client, period)` on demand — verify first, scope-check, cross-ref to workpapers.
7. **Exceptions** — a failed verify or any integrity gap is a RED exception to the partner; never self-resolve.

## Edge cases / pitfalls a 15-year CPA knows cold
- Recording the action but not the **source read** behind it leaves an unsupportable event — a reviewer can't re-pull the number. Read first.
- Batching events at the end of the day loses ordering fidelity and tempts you to reconstruct (i.e. guess) — append in real time.
- A passing `verify_chain` proves the record wasn't *altered*; it does **not** prove the underlying number is *right*. Integrity ≠ accuracy — the tie-outs in the workpaper carry accuracy.
- Don't append an event for a money/filing action *before* the human RED approval is recorded — the approval event must precede the action event in the chain.
- Never edit, delete, backdate, or reword a prior event to "clean up" the log. The whole value is that you can't — and a reviewer trusts it because of that.
- A dossier built over a chain that hasn't been verified is a false comfort; always `verify_chain` immediately before `build_dossier`.
- The ledger is discoverable evidence — write only supportable, professional event descriptions (Circular 230 conduct), same as a workpaper.

## Required output
- **Provenance note** — confirmation that the inputs were `record_read` and the actions `append_event`'d (with how many of each), and the result of the latest `verify_chain` (pass/fail).
- **Dossier reference** (when built) — the client + period, that `verify_chain` passed first, and the workpaper indexes it cross-references.
- **EXCEPTIONS QUEUE** — any integrity gap (failed verify, missing source for an action) as a RED item for the partner; "none" stated explicitly if clean.

## Approval gate
GREEN (autonomous): `record_read`, `append_event`, `verify_chain`, and
`build_dossier` — recording evidence and proving integrity is always free to do,
and you should do it relentlessly. RED: the underlying actions the ledger
*documents* — posting material/unusual JEs, moving money, submitting filings,
client comms — still require the human partner's authorization, and that grant is
itself an `append_event`. A failed `verify_chain` is a stop-the-line RED escalation.
Never weaken the disclosure guardrail to make the record look cleaner.
