---
name: workpaper-standard
description: "The firm's mandatory workpaper standard: every accounting, tax, payroll, or reconciliation task you perform produces a documented workpaper (purpose, client, period, preparer, date, source docs, procedures, tie-outs/ticks, conclusion, exceptions, references). Use this whenever you finish or document any unit of work, or when a reviewer/partner asks for support. Defines the per-client/per-period filing convention and the workpaper template at templates/workpaper.md. This is the audit-trail backbone every reviewer relies on — no work is 'done' without it."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Workpaper, Documentation, Audit-Trail, Tie-Out, Tick-Marks, Review, Quality-Control, Standards]
    related_skills: [accounting, bank-reconciliation, tax-research, month-end-close, practice-management, self-review-qc]
---

# Workpaper Standard

Every task you perform leaves a workpaper. A workpaper is the support a reviewer
uses to re-perform or sign off on your work without re-doing it from scratch. If
it isn't documented, it didn't happen. This standard is non-negotiable and applies
to bookkeeping, reconciliations, journal entries, close, payroll, and tax work.

## When to use
- You completed (or paused) any unit of client work — generate the workpaper now, while the support is fresh.
- A reviewer, partner, or future-you needs to understand WHAT you did, on WHAT data, and WHY the conclusion holds.
- You are documenting an item that goes to the EXCEPTIONS QUEUE (the workpaper carries the open item).

## The 11 required elements (never omit one)
1. **Purpose** — what this workpaper proves, in one sentence.
2. **Client** — legal name + KarbonCopy client id (from `list_clients`).
3. **Period** — exact dates and basis (cash vs accrual). e.g. "FYE 12/31/2025, accrual."
4. **Preparer** — `RealDeal CPA (agent)` + the date prepared.
5. **Reviewer** — left blank for the human partner sign-off (RED gate; never self-sign).
6. **Source documents** — every input, by name/location: QB report run + parameters, bank statement, invoice #, W-9, portal screenshot, file path. A reviewer must be able to re-pull each one.
7. **Procedures performed** — the steps you actually executed, in order, including the exact wired tools called (e.g. the QB report tools, `qb_journal_entry_create`, vr-ledger `validate`).
8. **Tie-outs / ticks** — the amounts you agreed and to what. Use the standard tick legend below; every tie must show both sides and the difference (0.00 or the variance).
9. **Conclusion** — the bottom line. State it plainly and only claim what you proved.
10. **Exceptions / open items** — anything unresolved, ambiguous, or material → cross-referenced to the EXCEPTIONS QUEUE. Never guess to "close" a workpaper.
11. **References (cross-refs)** — index code of this WP, links to related WPs, authority cited (IRC §, Treas. Reg., ASC, form #), and the prior-period WP if rolling forward.

## Standard tick-mark legend (use consistently)
- **TB** = agreed to trial balance / general ledger (`qb_trial_balance_export` / `qb_general_ledger`)
- **B** = agreed to bank/credit-card statement
- **F** = footed / cross-footed (column or row math re-added; recompute, don't eyeball)
- **PY** = agreed to prior-year workpaper / return
- **R** = recomputed independently (e.g. depreciation, accrual, payroll tax)
- **CF** = cross-referenced to another workpaper (give the index)
- **X** = exception — routed to the EXCEPTIONS QUEUE
Define any non-standard tick inline on the workpaper. Every tie shows: amount A, amount B, **difference**. A difference of 0.00 is a pass; anything else is documented and explained or becomes an exception.

## Filing convention (per client / per period)
Store under the client's workpaper tree so a reviewer can navigate by client → period → area:
```
workpapers/<ClientId>/<Period>/<Area>/<Index>-<slug>.md
```
- `<ClientId>` — KarbonCopy id (stable across periods).
- `<Period>` — `FY2025`, `2025-Q2`, `2025-06` (month), or `2025-941-Q2` for a filing.
- `<Area>` — `cash`, `ar`, `ap`, `payroll`, `tax`, `close`, `equity`, `recon`.
- `<Index>` — area letter + number: **A** cash, **B** AR, **C** prepaids/other assets, **E** AP/accruals, **N** equity, **P** P&L/revenue, **PR** payroll, **TX** tax. e.g. `A-1`, `PR-3`.
- `<slug>` — short kebab description.
Example: `workpapers/KC-00417/2025-06/recon/A-1-operating-bank-recon.md`.
Use the template at `templates/workpaper.md` — copy it, don't free-form. Keep prior-period WPs immutable; roll forward into a new file, never overwrite.

## Procedure
1. **Identify** the client (`list_clients`/`list_contacts`) and confirm period + basis before touching numbers.
2. **Copy** `templates/workpaper.md` to the filing path above; fill the header (elements 1-5).
3. **Capture source docs** as you go (element 6): record each the QB report tools you ran with its date range and basis; note statement dates, document numbers, file paths, and any `desktop` `screenshot` (the screenshot tool) of a portal you took. Always `qb_session_status` + `qb_company_info` first and record which company file you were in.
4. **Document procedures** (element 7) step-by-step with the exact tools and parameters used — a reviewer should be able to re-run them.
5. **Tie out** (element 8): agree every material balance to its source, foot the schedules, recompute estimates. Record both sides and the difference with a tick.
6. **Conclude** (element 9): write the bottom line; claim only what the ties support.
7. **Exceptions** (element 10): list open/ambiguous/material items, cross-ref to the EXCEPTIONS QUEUE; do not resolve by assumption.
8. **Cross-reference** (element 11) related WPs, prior period, and authority.
9. **Self-review** against `self-review-qc` before handoff — re-perform key ties, confirm every element is present, and clear or escalate exceptions; QC happens before the partner RED gate, not after.
10. **Leave the Reviewer line blank** — sign-off is a human RED gate.

## Edge cases / pitfalls a 15-year CPA knows cold
- A "reconciled" status with no listed reconciling items is a red flag — show the outstanding/unmatched items or it isn't a recon.
- Tie to the **source**, not to another QB report that shares the same error; a self-referential tie proves nothing.
- Re-run, don't reuse, a QB report whose date range or basis differs from the period — stale parameters silently break ties.
- Materiality is judgment: small but **unusual** (round-dollar transfers, related-party, period-end) items still go to exceptions even under threshold.
- Estimates (depreciation, accruals, allowances) must be **recomputed (R)**, never just agreed to the booked number.
- Round-tripping a number you don't understand to make a tie hit 0.00 is the cardinal sin — document the variance instead.
- Workpapers may be discoverable; write only supportable, professional statements (Circular 230 conduct).
- Never delete a prior workpaper; supersede with a new index and CF the old one.

## Required output
- **Bottom-line summary** — one or two lines: what was done and the conclusion (e.g. "A-1: operating bank reconciled to 6/30/25 statement; $0.00 difference; 2 outstanding checks listed").
- **EXCEPTIONS QUEUE** — bulleted open/material/ambiguous items for the partner, each cross-referenced to its WP index. Empty is fine; "none" must be stated explicitly.
- **WORKPAPER note** — the saved file path under the filing convention, with index, preparer, and date.

## Approval gate
GREEN (autonomous): preparing, indexing, filing, tying out, and writing workpapers — do this freely. RED: the **Reviewer** sign-off line, and any underlying action the WP supports that posts material/unusual JEs, sends client comms, moves money, or submits a tax/payroll filing — prepare and document, then hand to the human partner to authorize. Never self-sign the reviewer line.
