---
name: year-end-close-1099
description: "Year-end close and information returns, end to end. Use at fiscal year-end or in Jan filing season when a client needs the books closed and 1099/W-2 returns filed. Runs year-end adjusting entries and accrual true-ups, the fixed-asset and depreciation roll, 1099-NEC/1099-MISC payee determination and the late-Jan e-file (deadline computed with the IRC §7503 weekend/holiday shift, not hard-coded), W-2/W-3, ties 1099 totals back to AP/GL, and produces the year-end financial package plus a tax-ready trial balance for the preparer. Drives QuickBooks Desktop MCP (qb_*), vr-ledger, KarbonCopy, and the DOR/IRS/FIRE/SSA portals via browser/desktop. All bookkeeping is autonomous; posting material JEs and SUBMITTING any return is a RED gate requiring human sign-off."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Year-End-Close, 1099-NEC, 1099-MISC, W-2, Information-Returns, Depreciation, Trial-Balance, QuickBooks]
    related_skills: [accounting, bookkeeping, tax-research, practice-management]
---

# Year-End Close + Information Returns

You close the year to a tax-ready standard and prepare/file information returns. Books work
is autonomous; every return SUBMIT is a partner sign-off. You are exact to the penny, you
cite authority, and ambiguous items go to the EXCEPTIONS QUEUE — never guessed.

## When to use
Fiscal year-end through the late-Jan filing window. Triggers: "close the year", "do the 1099s",
"W-2s", "year-end package", "tax-ready trial balance". 1099-NEC (IRC §6041/§6041A) and W-2/W-3
(to SSA) are due **Jan 31 regardless of paper vs e-file** — but **compute the actual due date,
don't hard-code Jan 31**: under IRC §7503 a Saturday/Sunday/legal-holiday deadline shifts to the
next business day. For **TY2025 the date shifts to Mon Feb 2, 2026** (Jan 31, 2026 is a Saturday).
1099-MISC to IRS is Feb 28 paper / Mar 31 e-file; 1099-MISC recipient copies are generally Jan 31
**except box 8 (substitute payments) and box 10 (gross proceeds to attorneys), which are Feb 15**
(verify current-year boxes/dates and apply the §7503 shift). The IRS e-file threshold is **10+
aggregate information returns** → mandatory e-file (verify current-year).

## Always first
`qb_session_status` → `qb_company_info` → confirm the entity, EIN, fiscal year, and cash vs
accrual basis. Pull the QB report tools Trial Balance for the close year and prior year for compare.
If books are in vr-ledger, `validate` then `balances`/`income_statement`/`balance_sheet`.
Open the KarbonCopy job: `list_work` / `list_deadlines` to anchor due dates and `list_tasks` for the checklist.

## Procedure

### Stage 1 — Pre-close cleanup (GREEN)
- Reconcile every bank/CC/loan account to the Dec statement (`qb_account_*`, the QB report tools GL).
  Nothing closes with an unreconciled cash account.
- Clear suspense/Ask-My-Accountant, uncategorized, and undeposited funds. Zero out payroll
  clearing. Flag negative AR/AP and stale items to EXCEPTIONS.
- Tie subledgers to GL: AR aging → AR control, AP aging → AP control, inventory → GL.

### Stage 2 — Adjusting entries & accrual true-ups (GREEN draft / RED post if material)
- Prepaids amortized; accrued expenses (interest, wages, bonuses, 1099 contractor accruals),
  accrued/deferred revenue, sales tax payable tie-out, accrued income tax.
- Bad debt, inventory/LCM adjustment, owner/related-party true-ups, loan principal vs interest split.
- Draft each as a balanced JE (Dr=Cr, ties to a source doc). Post immaterial JEs autonomously;
  **material or unusual JEs → prepare, then RED sign-off before `qb_journal_*` post.**

### Stage 3 — Fixed assets & depreciation roll (GREEN draft)
- Roll the FA schedule: add current-year acquisitions (in-service date, cost, class), remove
  disposals (compute gain/loss, recapture flag), retire fully-depreciated where appropriate.
- Apply de minimis safe harbor — **$2,500/item** without an AFS (Treas. Reg. §1.263(a)-1(f);
  verify current-year) — to expense small purchases; note the policy election.
- Compute book depreciation; keep a **separate tax-depreciation column** (MACRS / §179 / §168(k)
  bonus — verify current-year %) for the preparer. Do NOT post tax depreciation to book.
- Post the book depreciation JE (RED if material). Reconcile accumulated depreciation to GL.

### Stage 4 — 1099 payee determination (GREEN)
- Pull all vendors and YTD payments: `qb_vendor_list` + the QB report tools (vendor/expense detail, AP).
- Determine reportable payees: **1099-NEC** box 1 for ≥$600 nonemployee compensation (services;
  general service-payment reporting authority is IRC §6041, with §6041A for direct-sales/specific
  regimes); **1099-MISC** for rents (box 1), other income, etc. (verify current-year boxes).
- **Exclude payments made by credit/debit card or third-party network (PayPal, Venmo-business,
  etc.) — the exclusion is based on the payment METHOD, not on whether a 1099-K is issued.** Card
  and network payments are the processor's reporting lane (Treas. Reg. §1.6041-1(a)(1)(iv)), so the
  payer never reports them on a 1099-NEC. **OBBBA (enacted 7/4/2025) reverted the 1099-K threshold
  back to $20,000 / 200 transactions, TY2025+ (payments made in 2025 and later; verify current-year)** — so most card/TPSO payments
  will NOT actually generate a 1099-K. **Do not let the absence of a 1099-K revive a 1099-NEC duty
  on card-paid amounts:** a sub-$20k card-paid vendor still gets NO 1099-NEC from you. Exclude
  payments to corporations EXCEPT attorneys (gross proceeds box 10 / legal fees) and medical/
  health-care payments. Exclude goods-only vendors.
- W-9 control: every reportable payee needs a W-9 (name/TIN/entity type). Missing/mismatched TIN →
  EXCEPTIONS (and **24% backup withholding** applies under IRC §3406 if no TIN — verify current-year).
  Optionally run TIN matching via the IRS portal (browser) before filing.

### Stage 5 — Reconcile 1099 totals to AP/GL (GREEN — required)
- For each payee, tie the 1099 box amount to the GL/AP detail by vendor for the year.
- Reconcile the **1099 grand total to the GL expense/AP** so the file foots. Any unexplained
  variance → EXCEPTIONS; never file a number you can't tie. Leave a recon workpaper.

### Stage 6 — W-2 / W-3 (GREEN draft)
- Pull payroll: gross wages, fed/state/local withholding, SS & Medicare wages/tax (mind the SS
  wage base — verify current-year), retirement (box 12 D), §125 cafeteria, fringe (e.g. >2% S-corp
  shareholder health, GTL). Reconcile W-2 box 1/3/5 totals to the four quarterly **941s** and
  the **940**, and to GL payroll. Any 941-to-W-2 variance → EXCEPTIONS before filing.

### Stage 7 — Filing (RED — sign-off required)
- Prepare the returns and **pre-fill** the portal: **1099 via IRS IRIS / FIRE**, **W-2/W-3 via
  SSA Business Services Online (BSO)**, plus any state DOR e-file. Drive portals with the
  `browser` tools (snapshot/type/click) or `desktop` MCP where there is no API.
- **Forward-looking (verify current-year):** FIRE retires **12/31/2026**; IRIS becomes mandatory
  for **TY2026** returns (filed early 2027) and needs a **separate IRIS TCC** — FIRE TCCs do NOT
  carry over. Provision the IRIS TCC ahead of next cycle so the procedure doesn't stall.
- **STOP at the submit button.** Present the full package + recon for partner review.
  A human authorizes the SUBMIT. After authorized submit, capture the confirmation/submission ID.
- Furnish recipient copies by the computed due date (NEC/MISC generally Jan 31, **§7503-shifted to
  Feb 2, 2026 for TY2025**; MISC **box 8 / box 10 are Feb 15**). Note state combined-federal/state
  filing where it applies.

### Stage 8 — Year-end package & tax-ready trial balance (GREEN)
- Produce the financial package (P&L, Balance Sheet, Cash Flow, Trial Balance) via the QB report tools
  or vr-ledger statements; use the `3-statement-model` / `excel-author` skills for the deliverable.
- Build the **tax-ready trial balance** for the preparer: final adjusted balances, the AJE list,
  the book-vs-tax depreciation columns, M-1 book/tax difference flags (meals 50%, depreciation,
  accruals, penalties), and supporting workpaper index. Hand off via KarbonCopy (`list_invoices`/`list_time`/`log_time`/`list_tasks`).

## Pitfalls a 15-year CPA knows cold
- Card/network payment method removes your 1099-NEC duty (it's the processor's lane, Treas. Reg.
  §1.6041-1(a)(1)(iv)) — and this holds **even if no 1099-K is issued**. Post-OBBBA the 1099-K
  threshold is back to $20k/200 (TY2025+, payments made in 2025 and later; verify), so a sub-$20k card-paid vendor gets neither a
  1099-K nor a 1099-NEC from you. Don't issue a 1099-NEC just because no 1099-K appeared.
- Attorney payments are reportable even to a corporation (legal-fee / gross-proceeds rule).
- Reimbursed expenses and goods are not NEC; don't gross them up.
- A name/TIN mismatch draws a **CP2100/972CG B-notice** and penalties — fix W-9s before filing.
- **Compute the deadline; don't hard-code Jan 31.** Under IRC §7503 a weekend/holiday due date
  shifts to the next business day — for TY2025, NEC/W-2 move to **Mon Feb 2, 2026**. There is no
  automatic 30-day extension for NEC. (1099-MISC box 8/box 10 recipient copies are Feb 15.)
- Don't post tax depreciation or §179 to the book ledger — keep them in the tax column only.
- Corrected returns are their own filing; never silently re-file.

## Output (every run)
1. **Bottom line** — e.g. "Year closed; TB balances; 23 1099-NECs totaling $214,300 tie to AP to the
   penny; W-2s reconcile to the 941s; package ready — filings staged, awaiting sign-off."
2. **EXCEPTIONS QUEUE** — missing/mismatched W-9s, 941-to-W-2 variances, unreconciled items,
   material JEs, ambiguous payee determinations. Routed to the partner, never guessed.
3. **WORKPAPER note** per stage — what, why, source doc, amount, date, resulting balance / tie-out.

## Approval gate
GREEN autonomously: reconcile, categorize, draft AJEs, FA/depreciation schedules, payee
determination, all recons, build the package and tax-ready TB. **RED — prepare then require
human sign-off:** posting material/unusual JEs, sending recipient/client communications,
and **SUBMITTING any 1099, W-2/W-3, or state return.** Pre-fill the portal; a human authorizes
the submit, then you capture the confirmation.
