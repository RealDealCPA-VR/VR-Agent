---
name: month-end-close
description: "Use to run a full month-end (or period-end) close for a QuickBooks client: cutoff, bank and credit-card reconciliations, accruals/prepaids/deferrals, depreciation, payroll and loan clearing, intercompany, suspense and undeposited-funds cleanup, accrual-vs-cash basis check, analytical review vs prior period and budget, then a close checklist and partner sign-off. Drives the QB report tools (P&L, Balance Sheet, Trial Balance, General Ledger, AR/AP Aging) and qb_journal_* for adjusting entries. Produces a close binder: bottom-line summary, reconciliation status, EXCEPTIONS QUEUE, and WORKPAPER notes. Trigger on 'close the books', 'month-end close', 'period close', 'close out [month]', or a recurring close engagement."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Month-End, Close, Reconciliation, Accruals, Depreciation, Analytical-Review, QuickBooks, Workpaper, GAAP]
    related_skills: [accounting, bookkeeping, bank-reconciliation, financial-statement-prep]
---

# Month-End Close

You run the period-end close to a workpaper standard. You **prepare and reconcile autonomously
(GREEN)**; you **draft but do not post** material/unusual journal entries and you **never** lock
the period without partner sign-off (**RED**). Goal: tie every balance-sheet account to support,
explain every P&L swing, leave nothing unexplained, and hand the partner a one-page review pack.

## When to use
A recurring or one-off close for a QB-backed entity. If the engagement is just one reconciliation
or one entry, use `bank-reconciliation` / `accounting` instead. Confirm the **close period** and the
**reporting basis (accrual vs cash)** before touching anything.

## Step 0 — Open the file (always first)
1. `qb_session_status` then `qb_company_info` — confirm the right company, live vs SIMULATION, and
   the period. Verify the prior period is **closed/locked** (a moved closing-date balance is a
   classic error). If unlocked, note it; do not assume prior numbers are final.
2. Pull the starting **the QB report tools Trial Balance** for the close month and the **prior month** —
   this is your control. Save both to the workpaper folder.

## Step 1 — Cutoff
- Verify transactions are in the correct period: late vendor bills, unbilled revenue, deposits in
  transit, post-period checks dated into the month. Scan the GL (the QB report tools General Ledger) for
  entries dated outside the period or with future/blank dates.
- Revenue recognition: ensure earned-not-billed and billed-not-earned land per **ASC 606**; defer
  anything invoiced but not delivered (see Step 4 deferrals).

## Step 2 — Bank & credit-card reconciliations
- For each cash/CC account: pull the **GL ending balance** and the **statement ending balance**.
  Match cleared items; list outstanding checks, deposits in transit, and uncleared CC charges.
- The recon **must tie to the penny**. If it doesn't, report the variance and where it likely sits
  (timing vs error vs duplicate). **Do not mark "reconciled" unless it is.**
- Flag stale outstanding checks (>6 mo is an internal stale-dating trigger — escheatment/void
  *candidates* to investigate, not auto-escheat; actual unclaimed-property dormancy is
  state-specific, commonly 1-5 yr) and duplicate transactions.
- **Undeposited Funds** (Step 6) and **suspense** must be near zero by close.

## Step 3 — Accruals (prepare as JEs)
- Accrue expenses incurred but not yet billed: utilities, interest, professional fees, bonuses,
  accrued PTO. Match revenue/expense to period (matching principle).
- Reverse last month's accruals if you book full actuals this month (avoid double-count). Prefer
  auto-reversing entries; if QB won't reverse, queue the reversal for next month.

## Step 4 — Prepaids & deferrals
- **Prepaids**: amortize insurance, software, rent, retainers per their schedule (one month's
  expense Dr, prepaid asset Cr). Tie the remaining prepaid balance to the amortization schedule.
- **Deferred/unearned revenue**: recognize the earned portion; the liability balance must tie to
  the deferral schedule and remaining obligations (**ASC 606**).

## Step 5 — Depreciation & amortization
- Book monthly depreciation per the fixed-asset / depreciation schedule (book basis, not tax/MACRS).
  If the client keeps one set of books, the book-vs-tax difference isn't a close entry — it's tracked
  on the tax return (Form 4562 / Schedule M-1/M-3), not here.
- Apply the client's **de minimis safe harbor** policy so small assets are expensed, not capitalized:
  **$5,000/item** with an Applicable Financial Statement, **$2,500/item** without an AFS, applied
  per-invoice or per-item per Treas. Reg. 1.263(a)-1(f) — **verify current-year** and the client's
  written policy (the higher limit requires both an AFS and a policy in place at year start).
- Tie accumulated depreciation to the schedule; flag any asset disposals not yet recorded.

## Step 6 — Clearing & suspense cleanup
- **Payroll clearing**: tie wages, employer taxes, and withholdings to the payroll provider report;
  the clearing/liability accounts should net to the next remittance only. Reconcile 941/state
  liabilities (do **not** file — that's a separate payroll skill).
- **Loan clearing**: split each payment into principal (Dr loan) and interest (Dr expense) per the
  amortization schedule; tie loan balance to the lender statement.
- **Undeposited Funds**: every receipt should have cleared to the bank — clear stragglers.
- **Suspense / "Ask My Accountant" / opening-balance equity**: investigate and reclass every item.
  Anything you can't source goes to the **EXCEPTIONS QUEUE**, never guessed into a real account.

## Step 7 — Intercompany
- For multi-entity clients, intercompany due-to/due-from accounts **must agree** between entities
  (mirror balances). Reconcile and eliminate; flag any out-of-balance pair as an exception.

## Step 8 — Basis check
- Confirm the books are on the intended **basis (accrual vs cash)**. If the client reports cash but
  keeps accrual books, note that AR/AP, accruals, prepaids, and deferrals are accrual-only and the
  cash-basis report will differ. State the basis on every deliverable.

## Step 9 — Post adjusting entries (RED gate)
- Compile all proposed JEs into an **Adjusting Journal Entries (AJE) schedule**: each entry shows
  account, Dr, Cr (proving debits = credits), amount, reason, and source doc.
- Immaterial, routine, scheduled entries (depreciation, prepaid amortization, recurring accruals)
  you may post via `qb_journal_*` with `dryRun` first, then for real, leaving a workpaper note.
- **Material or unusual entries → STOP.** Present the AJE schedule and **require partner sign-off**
  before posting. Use `dryRun` to show the impact. Never post a reclass into equity or a prior
  period without approval.

## Step 10 — Analytical / fluctuation review
- Re-pull **the QB report tools P&L and Balance Sheet** (final) for the close month vs **prior month**,
  vs **same month prior year**, and vs **budget** if one exists.
- Explain every material swing (set a $ and % threshold, e.g. >$X or >10%). Unexplained swings are
  exceptions. Check: margins, expense ratios, negative balances, debit balances in liabilities (or
  vice-versa), AR/AP aging shifts (the QB report tools Aging), and any account that should be zero.

## Step 11 — Close checklist & sign-off
- Produce the **close checklist** with status per line (Cutoff / Bank recons / CC recons / Accruals
  / Prepaids / Deferrals / Depreciation / Payroll clearing / Loan clearing / Undeposited Funds /
  Suspense / Intercompany / Basis / Analytical review / AJEs posted).
- Re-pull final **Trial Balance**; confirm it balances and ties to the supported balances.
- **Closing the period / setting the closing date is a RED action** — recommend it, but the partner
  authorizes the lock.

## Edge cases a 15-year CPA knows cold
- Negative cash on the BS = unrecorded transfers, NSF, or timing — investigate, don't net.
- Opening Balance Equity with a balance after go-live = an unfinished migration; reclass it.
- Credit balance in AR / debit in AP = misapplied payments or duplicate bills — fix before close.
- Reversing accruals forgotten = double-counted expense next month; track the reversal.
- Sales-tax payable that never decreases = filings not recorded against the liability.
- A recon that "ties" only because of an unexplained adjustment is **not reconciled** — flag it.
- Round-number journal entries with no source are a red flag; source or queue them.

## Required output
1. **Bottom line** (1-2 lines): e.g. "April close complete on accrual basis; all bank/CC accounts
   reconciled to the penny; 3 AJEs posted, 1 material entry awaiting partner sign-off; 2 items in
   the exceptions queue." State the basis and period.
2. **Reconciliation status table** — each account: GL bal, statement bal, variance, status.
3. **AJE schedule** — every proposed/posted entry with Dr/Cr proving it balances.
4. **Analytical review table** — account, current, prior, $ Δ, % Δ, explanation.
5. **Close checklist** — each line with Done / Open / Exception.
6. **EXCEPTIONS QUEUE** — every unexplained/material/ambiguous item, with the question for the
   partner. Never guessed.
7. **WORKPAPER note** per recon and per posted entry: what, why, source doc, amount, date, resulting
   balance. The TB before and after is the binder's control sheet.

## Approval gate
GREEN: read, reconcile, amortize/depreciate schedules, draft AJEs, analytical review, workpapers.
RED (prepare, then require human sign-off): posting material/unusual JEs, reclasses into equity or
a prior period, and setting/locking the closing date. Prepare it, `dryRun` it, then wait for the
partner. Never fabricate a balance or a "reconciled" status.
