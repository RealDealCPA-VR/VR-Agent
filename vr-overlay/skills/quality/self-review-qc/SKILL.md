---
name: self-review-qc
description: "Pre-handoff self-review and quality control. Run this on YOUR OWN finished work product (a close, a reconciliation, a tax workpaper, a set of journal entries, a financial statement) BEFORE handing it to a human or marking a task complete. Checks that it balances, subledgers tie to the GL, retained earnings rolled, no negative/illogical balances, nothing changed vs prior period unexpectedly, every exception is captured, the workpaper is complete, and RED approval gates were respected (not silently crossed). Produces a QC verdict: PASS / PASS-WITH-NOTES / FAIL, with the specific defects and where they sit. Use whenever you finish an accounting or tax deliverable and before any handoff, sign-off request, or 'done' claim."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Quality-Control, Self-Review, Tie-Out, Workpaper, Close, Handoff, Approval-Gate]
    related_skills: [accounting, month-end-close, bank-reconciliation, workpaper-standard, payroll-tax-prep-filing]
---

# Self-Review QC

The habit a senior demands: you never hand work up until you have reviewed your own
output as if you were the reviewer who signs it. A 15-year CPA does not present a close
that does not tie. This skill runs a disciplined pre-handoff QC pass on **your own work
product** and returns a verdict. It is a GREEN activity — review only, it changes nothing.

## When to run
Immediately AFTER you finish any deliverable and BEFORE you: hand it to a human, request
sign-off, send a client communication, or say "done/complete". Required for: month-end
close, any reconciliation, journal-entry batches, financial statements, tax/payroll
workpapers, and anything feeding a RED gate.

## Inputs you pull (read-only)
- The deliverable itself: your entries, recon summary, statements, workpaper notes,
  exceptions queue, and the approval-gate status you recorded.
- `qb_session_status` + `qb_company_info` FIRST (confirm you reviewed against the right
  company/period). Then read-only reports as needed:
  the QB report tools — Trial Balance, Balance Sheet, P&L, General Ledger, AR/AP Aging.
- `vr-ledger` — `validate`, `balances`, `balance_sheet`, `income_statement`,
  `cash_flow_statement` for ledger-format books.
- Prior-period figures (prior TB / prior close workpaper) for the change-vs-prior check.

## The QC checklist — run every line, record PASS/FAIL with evidence
1. **It balances.** Trial Balance total debits = total credits to the penny. Balance Sheet:
   Assets = Liabilities + Equity. Every journal entry: Dr = Cr. Pull the TB
   (`qb_trial_balance_export` / vr-ledger `validate`) and prove it.
2. **Subledgers tie to the GL.** AR subledger (aging) = GL AR control account. AP aging =
   GL AP control. Inventory/fixed-asset subledger = its control account. Bank/CC reconciled
   balance = GL cash account. Compute each tie-out; any difference is a defect with the $.
   **If the deliverable includes a statement of cash flows**, also tie the indirect-method
   roll: net income + non-cash adjustments (depreciation, etc.) ± working-capital changes =
   net change in cash, and that net change must equal the period's actual GL/bank cash
   movement and the B/S cash delta (`vr-ledger cash_flow_statement`). Any break is a defect.
3. **Retained earnings rolled.** Current RE = prior-period ending RE + net income − dividends
   /distributions (no direct posts to RE unless intended and documented). Prior-year net
   income must have closed into RE, not still sitting in current-year income.
4. **No negative / illogical balances.** Scan the TB: no contra-normal balances
   (negative cash unless a true overdraft, debit balance in a revenue account, AP with a
   debit balance, negative accumulated depreciation sign error, asset with a credit balance).
   Each anomaly is flagged with the account and amount.
5. **Change vs prior — expected only.** Diff this period's TB/statements against prior.
   Every material swing must have a known cause (real activity, a booked adjustment, a
   reclass). Set the threshold to the entity, not a flat number: a % move (e.g. >10%) AND a
   dollar floor scaled to the entity's size — anchor the floor to a basis such as ~0.5–1% of
   revenue or total assets, so a $5k swing is material for a small client but noise for a
   large one. Unexplained movement is a defect, not a rounding note.
6. **Exceptions captured.** Every ambiguous, material, or unresolved item is in the
   EXCEPTIONS QUEUE — not buried, not silently guessed. Confirm count and that each has
   owner + $ + the open question. A guessed material item is an automatic FAIL.
7. **Workpaper complete.** Every posting/adjustment has its one-line note: what, why,
   source doc, amount, date, resulting balance. Basis (cash vs accrual) and period stated.
   Numbers are exact decimals. No "TBD" left in a workpaper presented as final.
8. **Approval gates respected.** Confirm no RED action was actually executed without human
   sign-off: no material/unusual JE posted live, no client comm sent, no money moved, no
   tax/payroll filing submitted. RED items must be in **prepared-pending-approval** state.
   A crossed gate is an automatic FAIL — escalate immediately.

## Verdict logic
- **FAIL** — any of: out of balance; a subledger doesn't tie; a crossed RED gate; a guessed
  material item; an unexplained material change. Do NOT hand off. Fix or route to exceptions,
  then re-run QC.
- **PASS-WITH-NOTES** — ties and gates clean, but immaterial open items / minor workpaper
  gaps remain. List them; handoff allowed with the notes attached.
- **PASS** — every line passes, exceptions complete, gates intact, workpaper final.

## Pitfalls a senior catches
- A TB that balances but whose subledgers don't tie — balanced ≠ correct. Always tie out.
- Net income agreeing on the P&L but not flowing to the B/S (RE / current-earnings break).
- "Reconciled" claimed with stale or duplicated outstanding items inflating the match.
- Sign-flipped accumulated depreciation or contra-revenue that nets right but is wrong.
- Rounding masking a real variance — never round away a difference you can't explain.
- Marking RED work "done" because the prep is finished — prep done is not authorized.
- Empty exceptions queue on a messy month: usually means items were guessed, not absent.

## Output (required)
1. **Bottom line first** — the verdict: `QC: PASS` / `PASS-WITH-NOTES` / `FAIL`, one line on
   why (e.g. "FAIL — AR subledger out $1,240 vs GL control; RE rolled, TB balances").
2. **QC checklist table** — each of the 8 lines: Check | Result (PASS/FAIL) | Evidence/amount.
3. **EXCEPTIONS QUEUE** — every defect and open item: description, account, $, owner, the
   ask. Anything material or ambiguous goes here for the partner — never guessed.
4. **WORKPAPER note** — "Self-review QC run on <deliverable> for <entity/period>, vs prior
   <period>; verdict <X>; defects <n>; gates intact <Y/N>." Date and basis stated.

## Approval gate
This skill is GREEN — read/review only, it posts nothing. But it is the gatekeeper for
others: if QC = FAIL, do not hand off and do not advance any RED gate. Fix the defect or
escalate to the EXCEPTIONS QUEUE for the partner, then re-run QC until PASS /
PASS-WITH-NOTES before handoff or sign-off request.
