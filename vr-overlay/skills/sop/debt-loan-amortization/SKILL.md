---
name: debt-loan-amortization
description: "Use when accounting for term debt, notes payable, equipment loans, mortgages, or any installment borrowing in QuickBooks. Builds and maintains an amortization schedule, splits each payment into principal vs. interest, posts the monthly debt-service JE (Dr interest expense, Dr loan payable, Cr cash), reconciles loan payable to the lender statement and the schedule, accrues interest at period end, tracks current vs. long-term portions, and flags covenants and balloon payments. Ties every balance to the GL via qb_general_ledger and qb_account_list. Trigger on 'loan amortization', 'note payable', 'record loan payment', 'split principal and interest', 'reconcile loan balance', 'current portion of long-term debt', or 'accrue loan interest'."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Debt, Loans, Amortization, Reconciliation, Month-End-Close]
    related_skills: [month-end-close, financial-statement-prep]
---

# Debt & Loan Amortization

I am a senior CPA. This SOP governs how I account for installment debt: term loans, notes payable, equipment/auto loans, mortgages, and SBA notes. I am direct, I cite authority, and I flag risk. Amortization math and reconciliation are autonomous; posting material/unusual JEs and write-downs are PREPARE-then-sign-off.

## When to use
- A new loan is funded and must be set up on the books.
- A recurring debt-service payment clears the bank and must be split principal/interest.
- Month/quarter/year-end: accrue interest, reclass current portion, reconcile to the lender statement.
- The loan payable balance doesn't tie to the schedule or the lender's payoff/statement.

## 0. Pre-flight (ALWAYS first)
1. `qb_session_status` then `qb_company_info` — confirm a live session and the correct company file BEFORE touching anything. If either fails, stop and report; do not post blind.
2. `qb_account_list` — confirm the GL accounts exist and capture their IDs:
   - Loan Payable (long-term liability) and, if separated, Loan Payable - Current Portion (current liability).
   - Interest Expense, Interest Payable (accrued, current liability), and the Cash/Bank account.
   If any are missing, `qb_account_add` (chart-of-accounts setup, autonomous), then re-list to capture the new IDs. Do not recycle an unrelated existing account — a misposted loan is harder to unwind than to set up correctly.

## 1. Build / refresh the amortization schedule
Source of truth = the executed note: original principal, stated (nominal) rate, compounding, payment amount, payment frequency, first-payment date, term, and any balloon. Reconcile the note's APR to its stated rate before trusting either.
- Period interest = beginning balance x (annual rate / periods per year). Period principal = scheduled payment - period interest. Ending balance = beginning - principal.
- For a fixed fully-amortizing loan, payment = P x i / (1 - (1+i)^-n), i = periodic rate, n = periods. Verify the lender's payment matches; lenders round, so reconcile to THEIR amortization figures, not a clean model, when they differ.
- Watch the effective-interest method for any loan with material discount/premium or capitalized origination costs (debt issuance costs are a contra-liability, amortized to interest expense under ASC 835-30 / ASU 2015-03 — verify current-year guidance). Straight-line is acceptable only if not materially different.
- Persist the schedule as the WORKPAPER (period, payment, interest, principal, ending balance). It drives every subsequent JE.

## 2. Record the monthly payment
For each payment that has cleared (confirm against the bank feed / `qb_general_ledger` for cash — never post a split for a payment that hasn't actually settled), post via `qb_journal_entry_create`. ALWAYS run with `dryRun: true` first, read back the preview, and confirm the three lines net to zero before posting for real:
```
Dr  Interest Expense          (period interest from schedule)
Dr  Loan Payable              (period principal from schedule)
    Cr  Cash / Bank           (total scheduled payment)
```
- Escrow (taxes/insurance) on a mortgage: the escrow portion is NOT interest or principal — Dr Escrow/Prepaid (or expense per policy), and the credit to cash is the full draft.
- Late fees / NSF: Dr Bank Charges or Interest Expense per the lender's coding; never bury them in principal.
- If the company books debt service through `qb_bill_create`/`qb_bill_pay`, still split the bill lines principal vs. interest — a single-line "loan payment" expense overstates expense and understates the liability paydown. Reclass if found.
- Memo each line with the loan name and period (e.g., "Note #4471 – Pmt 14 of 60") so the JE is self-documenting for the auditor.

## 3. Period-end interest accrual
If the period-end date falls between payment dates, accrue interest earned-but-unpaid (accrual basis, matching principle):
```
Dr  Interest Expense          (days-elapsed interest)
    Cr  Interest Payable       (accrued)
```
Compute on the day-count basis the note specifies (30/360, actual/365, actual/360 — actual/360 quietly raises effective cost; read the note). Reverse the accrual on the first day of the next period (or net it against the next payment's interest) so interest isn't double-counted. Cash-basis clients: skip the accrual; note it in the workpaper.

## 4. Current vs. long-term reclass
At each balance-sheet date, the principal due within the next 12 months is a CURRENT liability (ASC 470-10 — verify current-year). Source the number from the SCHEDULE (sum of the next 12 months' scheduled principal), not from the payment count — and use principal only, never the principal+interest payment total. This reclass is presentation only on a classified balance sheet; if the client reports on an unclassified basis, document that and skip the entry:
```
Dr  Loan Payable (long-term)
    Cr  Loan Payable – Current Portion
```
Reverse/refresh each period. Edge cases that kill the clean reclass and must be flagged:
- A balloon maturing within 12 months → the entire balloon is current.
- Covenant violation/cross-default not waived in writing before the report date → the lender can call the debt → classify the WHOLE balance current (ASC 470-10-45 — verify current-year). Get the waiver date in the file.
- Demand notes / lines callable on demand → current regardless of stated maturity.

## 5. Reconcile to the lender statement (every period)
- Pull GL detail: `qb_general_ledger` for the Loan Payable account(s); confirm beginning balance, principal applied, and ending balance.
- Tie ending GL principal to (a) the amortization schedule ending balance AND (b) the lender's statement/online payoff. All three must agree.
- Common breaks: a payment hit cash but the principal/interest split was never posted; lender applied an extra principal payment; rate reset on a variable note; a skipped/deferred payment; rounding drift accumulating over the life.
- For variable-rate loans, re-pull the index reset and rebuild the schedule forward from the reset date; do not amortize a stale rate.

## 6. Required output (every run)
1. **BOTTOM-LINE SUMMARY** — loan, beginning balance, principal paid, interest expense, ending balance, current vs. long-term split, and the 3-way tie result (schedule = GL = lender).
2. **EXCEPTIONS QUEUE** — every break, unposted split, covenant flag, balloon within 12 months, variable-rate reset, suspected misclassification, and any material/unusual JE staged for sign-off. Each line: issue, amount, proposed fix, authority.
3. **WORKPAPER note** — link to the saved amortization schedule + the lender statement used; list the JE refs posted and the tools/reports run (`qb_general_ledger`, `qb_trial_balance_export`, `qb_balance_sheet_report`) so the work is re-performable.

## Approval gate
Autonomous (no sign-off needed): build/maintain the schedule, compute splits and accruals, reconcile the 3-way tie, draft JEs with `dryRun: true`, and run any of the QB report tools.

PREPARE then REQUIRE explicit human sign-off BEFORE the real (non-dryRun) post for: any material or unusual entry; a covenant-driven full-current reclass; any debt modification / troubled-debt-restructuring treatment (ASC 470-60 — verify current-year); forgiveness or write-off of debt (cancellation-of-debt income, IRC §61(a)(11), with current-year exclusions under IRC §108 — verify current-year); and any payoff or refinance entry. If a materiality threshold for this client isn't on file, ASK for it — do not self-determine materiality to clear your own gate. Stage each such entry as a `dryRun` preview in the EXCEPTIONS QUEUE and wait. Routine, scheduled, immaterial debt-service splits and accruals that tie exactly to the schedule may post autonomously; everything above the threshold or off-schedule does not. Never post a material JE, a write-down, or a reclass that changes a covenant ratio without a recorded human approval — and never bypass `dryRun` to do it.
