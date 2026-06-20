---
name: financial-statement-prep
description: "Prepare and review a full set of financial statements from QuickBooks Desktop or vr-ledger books: P&L, Balance Sheet, Statement of Cash Flows, and Trial Balance. Run analytical review (trend/variance vs prior period and budget, ratios, margins), tie the Balance Sheet to its subledgers, roll retained earnings, tie cash to bank recs, state basis/period disclosure, and write plain-English management commentary. Use when asked to 'prepare financials', 'close-package financials', 'monthly/quarterly/annual statements', 'review the financials', a 'reporting package', or an 'analytical review'. Reads via the QB report tools and vr-ledger; flags exceptions; leaves workpapers. Statements are GREEN to prepare; releasing to a client/lender is RED."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Financial-Statements, Reporting, Analytical-Review, Tie-Out, GAAP, QuickBooks, Ledger, Workpapers]
    related_skills: [accounting, month-end-close, tax-research]
---

# Financial Statement Preparation & Review

You build and review a complete financial statement package to a workpaper standard. The
agent PREPARES (GREEN); a partner reviews and a human authorizes any release to a client,
lender, or board (RED). Statements that have not tied out or that rest on a guessed number
do not leave the building.

## When to use
- Monthly/quarterly/annual reporting package after month-end close is substantially done.
- A standalone "review the financials" / analytical review request.
- A draft set for a lender, board, or tax-prep handoff (still RED to release).
Do NOT use to post the underlying adjustments — that is the `accounting` / `month-end-close`
skill. Statements reflect the books AS POSTED; if you find a needed entry, route it there
and note it in the EXCEPTIONS QUEUE.

## Step 0 — Frame the engagement (do this first, every time)
1. **Basis & period.** Confirm cash vs accrual and the exact period (e.g., "Accrual,
   month ended 2026-05-31, FY2026") and the comparatives (prior month, prior year, budget).
   The basis drives everything downstream — never assume.
2. **Connect & verify the source.** For QB: `qb_session_status` → `qb_company_info` FIRST;
   confirm the right company file is open and the close-through date. For ledger clients:
   `vr-ledger validate` to confirm the books parse and balance before you report on them.
3. **Reporting framework.** GAAP, tax-basis, or other comprehensive basis (OCBOA)? This sets
   the disclosure language and whether the package is "prepared in conformity with…".

## Step 1 — Pull the four statements (read-only, GREEN)
Pull each at the SAME basis and period, with comparatives where available:
- **Trial Balance** — `qb_trial_balance_export` (or vr-ledger `balances`). This is your
  control total; everything ties back here.
- **Profit & Loss** — `qb_pnl_report` (vr-ledger `income_statement`), with
  prior-period and budget columns.
- **Balance Sheet** — `qb_balance_sheet_report` (vr-ledger `balance_sheet`), comparative.
- **Statement of Cash Flows** — vr-ledger `cash_flow_statement`; for QB use the Cash Flow
  report and verify the method (indirect is standard). QB's SCF lacks the fidelity of a true
  indirect statement and in practice usually needs reconstruction — rebuild from the
  comparative BS + P&L (begin-to-end deltas, add back non-cash, classify O/I/F) and label the
  method. Never present QB's raw cash-flow output as a finished indirect SCF without tie-out.

## Step 2 — Tie-outs (the part juniors skip; you don't)
Prove each of these and record the result in the workpaper. Any break that you cannot
resolve to the penny goes to the EXCEPTIONS QUEUE with the variance and where it likely sits.
- **TB ⇄ statements.** Every P&L and BS line foots to the Trial Balance. Debits = credits.
- **BS ⇄ subledgers:**
  - AR control = A/R Aging total → `qb_ar_aging`.
  - AP control = A/P Aging total → `qb_ap_aging`.
  - Inventory = stock valuation / item report; Fixed assets = depreciation schedule;
    Loans = amortization/lender statements; Payroll liabilities = 941/payroll clearing.
- **Cash ⇄ reconciliations.** Each cash/CC GL balance equals the reconciled balance per the
  latest bank rec (reconciled date, not "today"). Unreconciled = exception, not a footnote.
- **Retained earnings roll.** Beginning RE + net income − distributions/dividends ± prior-
  period adjustments = ending RE. Tie beginning RE to last period's ending RE; tie current
  net income to the P&L bottom line. Equity must roll cleanly or it is an exception.
- **Inter-statement ties.** Net income on P&L = net income line feeding the cash-flow
  reconciliation = the RE roll. Change in cash on the SCF = change in BS cash. Beginning +
  net change = ending cash. If the SCF doesn't tie to BS cash, the SCF is wrong — fix it.

## Step 3 — Analytical review (this is where you earn the fee)
- **Trend / variance.** Current vs prior period AND vs prior year AND vs budget. Compute $ and
  % change per line. Set a CONCRETE materiality threshold up front — a real dollar figure, not
  an abstraction (e.g., greater of 5% of the line and $X where X is, say, $1,000 for a small
  entity or a % of pretax income; size it to the engagement) — record it in the WORKPAPER note,
  and EXPLAIN every variance above it — don't just list it.
- **Margins.** Gross margin %, operating margin %, net margin %; trend them. Investigate
  margin compression that the client hasn't flagged.
- **Ratios** (label each, show the formula, compare to prior/benchmark):
  current ratio, quick ratio, AR days (DSO), AP days (DPO), inventory days, debt-to-equity,
  interest coverage, return on equity. Ratios that moved sharply are leads, not conclusions.
- **Reasonableness / smell tests.** Negative cash, debit balances in liability accounts and
  credit balances in assets, "Ask My Accountant"/Uncategorized/suspense balances, round-
  dollar or duplicate journal entries, expenses with no period-over-period activity that
  should recur (rent, payroll, depreciation), revenue without matching COGS. Each oddity is
  either explained in commentary or raised as an exception.

## Step 4 — Disclosure & basis note
State, in the package header: entity, period(s), basis of accounting (cash/accrual/tax/
OCBOA), reporting framework, comparatives shown, and that the statements are
management-prepared / internal draft unless a formal compilation/review/audit is engaged
(you do NOT provide assurance here — Circular 230 and AICPA standards govern any report
language; do not imply an audit/review you didn't perform). If GAAP departures exist on a
tax/OCBOA basis, note them. Use "verify current-year" for any rate/threshold you can't
confirm live.

## Step 5 — Management commentary (plain English)
2–5 short paragraphs a non-accountant owner understands: how the period performed vs prior
and budget, what drove the biggest swings, liquidity/solvency posture from the ratios, and
the watch-items. Direct, exact with numbers, no fluff. Tie every claim to a number in the
statements.

## Output (required structure)
1. **Bottom line** — one or two sentences (e.g., "May P&L: revenue $312,400, +8% MoM, +14%
   YoY; net income $41,900 at 13.4% margin. Statements tie; cash and SCF reconcile. Two
   exceptions for partner review.").
2. **The four statements** — comparative, as tables, with the basis/period header.
3. **Analytical review** — variance table (with explanations above threshold), margins, and
   ratio table vs prior/benchmark.
4. **EXCEPTIONS QUEUE** — numbered, for the partner: each item = what, amount, where it
   likely sits, your recommendation, and what's needed to clear it. Material/ambiguous items
   go here; never guess them into the statements.
5. **WORKPAPER note** — basis & period, source (company file + close-through date or ledger
   commit), every tie-out with its result (tied / variance $X), thresholds used, comparatives,
   and preparer/date. This is the evidence trail.

## Edge cases a 15-year CPA knows cold
- **Cash-basis BS oddities.** True cash basis shouldn't show AR/AP; if it does, the books are
  mixed-basis — flag it, don't paper over it.
- **Prior-period restatement.** If a prior column changed since last issued, that's a
  restatement — disclose it and reconcile the change; don't silently overwrite.
- **Intercompany / consolidations.** Eliminate intercompany before presenting consolidated;
  un-eliminated IC inflates both sides. Flag if elimination entries aren't present.
- **Distributions vs. expense.** Owner draws/distributions hit equity, not the P&L; a
  distribution booked as expense overstates costs and understates equity — exception.
- **SCF traps.** Non-cash items (depreciation, gain/loss on disposal), financing vs operating
  classification of loan proceeds/repayments, and working-capital sign conventions are the
  usual breakpoints when cash doesn't tie.
- **Negative retained earnings / going concern.** Persistent losses or negative equity are a
  commentary item and may be a disclosure matter — surface it.

## Guardrails
- Preparing, tying out, analyzing, and drafting commentary is **GREEN** — fully autonomous.
- **RED** — releasing the package to a client, lender, board, or any external party; attaching
  compilation/review/audit report language; or emailing/transmitting the statements. Prepare
  it, then stop for human sign-off.
- Never fabricate a balance, a "tied" result, or a current-year rate. If it doesn't tie and
  you can't resolve it, the package is DRAFT and the break is an exception — say so.
