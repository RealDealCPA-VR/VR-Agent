---
name: accounts-payable
description: "AP runbook for the firm's clients: enter and code vendor bills, run 3-way match (PO/receipt/invoice), prevent duplicate payments, route the approval workflow, build payment runs that capture early-pay (terms) discounts, keep the vendor master clean, collect W-9s and track 1099-NEC reportability, produce AP aging, and accrue unbilled costs at month-end. Drives QuickBooks Desktop (qb_bill_*, qb_vendor_*, the QB report tools), vr-ledger, KarbonCopy, browser/desktop for vendor portals. Use for bill processing, vendor onboarding, cutting checks/ACH, AP close, or any 'pay this / who do we owe' request. Preparing payments is GREEN; releasing money is RED (human sign-off)."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Accounts-Payable, AP, Vendor, 3-Way-Match, 1099, W-9, Payment-Run, Accrual, QuickBooks, Month-End]
    related_skills: [accounting, bookkeeping, tax-research, practice-management]
---

# Accounts Payable

You run the full AP cycle to a workpaper standard: bill in, coded right, matched, approved,
paid on the best terms, with a clean vendor master and correct 1099 treatment. You PREPARE
everything; a human RELEASES money and SUBMITS filings.

## When to use
Bill entry/coding, 3-way match, duplicate-payment checks, approval routing, building a
payment run (and catching early-pay discounts), vendor onboarding/W-9, 1099 tracking, AP
aging, and month-end accrual of received-but-unbilled costs.

## Start every session
1. `qb_session_status` then `qb_company_info` — confirm the right company file is open and the
   period/basis (AP is accrual by nature even if the P&L is cash). If multi-company, `qb_company_list` → `qb_company_open`.
2. Pull a baseline: `qb_ap_aging` and `qb_bill_list` (open bills) so you know the
   current liability before you touch anything.

## Procedure

### 1. Bill entry & coding (GREEN)
- For each invoice: capture vendor, invoice #, invoice date, due date, amount, and the GL
  coding (expense/asset account + class/job if the client uses them).
- Match vendor to the master via `qb_vendor_list` (paginate/`autoExhaust` past ~500 rows);
  never create a new vendor if it's a spelling variant of an existing one (see hygiene below).
- Set terms from the vendor record (Net 30, 2/10 Net 30, etc.) so the due date and any
  discount window compute correctly.
- Code to the natural expense account. Capitalize per the **de minimis safe harbor — $2,500
  per item/invoice** (Treas. Reg. 1.263(a)-1(f); $5,000 only with an AFS). Items over the
  threshold → fixed asset, route to month-end depreciation, not expense.
- Enter via `qb_bill_create` (use `dryRun` first to preview the posting; pass a per-bill
  `idempotencyKey` so a timeout retry doesn't double-enter). Bill entry is GREEN.

### 2. 3-way match (GREEN; mismatch → EXCEPTION)
Match **PO ↔ receiving/packing slip ↔ invoice** on vendor, item, quantity, and unit price.
- Quantity/price within tolerance (typ. ≤ $25 or 2%) → pass, code and enter.
- No PO required (utilities, rent, professional fees) → 2-way match invoice to contract/approval.
- Mismatch (short ship, price variance, no receipt, no PO where one's required) → DO NOT pay
  the disputed portion; park to the **EXCEPTIONS QUEUE** for buyer/partner resolution.

### 3. Duplicate-payment prevention (GREEN — run EVERY time)
Before entering OR paying, screen for dupes — the most common AP loss:
- Same vendor + same invoice # (the hard stop). Then same amount + same/near date, and same
  amount to a vendor variant (see hygiene). Check `qb_bill_list` and recent `qb_bill_pay`.
- Watch credit memos applied twice, statements paid as if invoices, and the classic
  vendor-entered-twice (e.g. "ABC Inc" and "ABC, Inc."). Any hit → EXCEPTIONS QUEUE, do not pay.

### 4. Approval workflow (GREEN to route; payment release is RED)
- Route per the client's authority matrix (dollar thresholds → approver). If none on file,
  flag and use a conservative default; don't invent authority.
- Log approvals (who/when) to the workpaper. Track routing/SLAs in KarbonCopy (`tasks`,
  `time`, `deadlines`) so nothing ages past terms unapproved.
- Unapproved + due → EXCEPTIONS QUEUE before the discount/due date lapses.

### 5. Payment run & early-pay discounts (PREPARE GREEN → RELEASE RED)
- Build the proposed run from open, approved, matched bills. Sort by due date and discount window.
- **Capture discounts that beat the hurdle:** 2/10 Net 30 ≈ **~37% annualized**
  (2/98 × 365/20) — almost always take it; pay by day 10. Note the discount account/coding.
  Don't pay early with no discount — preserve cash to the due date.
- Net any open vendor credits/credit memos against the run.
- Confirm remit-to, payment method (check/ACH), and that bank funds cover the run.
- Produce the proposed run as a table (vendor, inv #, gross, discount, net, pay date, method),
  then **STOP at the RED gate** — a human authorizes before any `qb_bill_pay` / ACH / check.
  **`qb_bill_pay` rejects `dryRun` (`9006`)** — there is no safe preview on the payment itself,
  so the proposed-run table IS your review artifact; once authorized, release ONE bill first and
  verify it posted before running the batch. Verify ACH/remit changes out-of-band (callback to a
  known number) — wire/ACH change requests are the #1 BEC fraud vector; never act on an emailed
  bank-change alone.

### 6. Vendor master hygiene (GREEN)
- One record per legal entity. Dedupe variants; merge in QB rather than leaving doubles.
- Each active vendor needs: legal name, remit-to address, EIN/SSN (from W-9), terms, 1099 flag,
  and a verified payment method. Flag missing/stale data to EXCEPTIONS.

### 7. W-9 collection & 1099 tracking (GREEN; filing is RED)
- **Get a Form W-9 BEFORE first payment** — establishes name/TIN and 1099 status; without it,
  24% **backup withholding** applies (IRC 3406).
- Mark 1099-reportable vendors. **1099-NEC** for $600+ of nonemployee compensation/services
  (Box 1); **1099-MISC** for rents ($600, Box 1) and **royalties ($10, Box 2)**, among others.
  Corporations are generally exempt **except** attorneys (legal fees always reportable) and
  medical/health payments. Use `qb_1099_summary`/`qb_1099_detail` to build the year-end set.
- Exclude payments made by credit card / third-party network — those are reported on 1099-K by
  the processor, not you. Track YTD reportable totals against the $600 threshold all year so
  January isn't a fire drill. Preparing 1099s is GREEN; **filing them is RED** (human submits;
  due to recipient & IRS by Jan 31 — verify current-year date).

### 8. AP aging (GREEN)
- `qb_ap_aging` (as of period end). Review buckets (current / 1-30 / 31-60 / 61-90 / 90+). Flag
  past-due (lost discounts, late fees, vendor-hold risk), debit balances (prepaids/over-payments/
  missing credits), and stale items. Tie the aging total to the AP control account on the trial
  balance (`qb_trial_balance_export`); reconcile any variance to the penny.

### 9. Month-end accrual of unbilled costs (PREPARE GREEN; posting material JE is RED)
- Accrue goods/services **received but not yet invoiced** so expense lands in the right period
  (accrual basis / matching). Sources: open POs received not billed, recurring services, known
  invoices-in-transit.
- Draft the JE: Dr expense / Cr **Accrued Liabilities (AP accrual)**; reverse next period. Show
  it balances and ties to support via `qb_journal_entry_create` (`dryRun`). **Posting a material
  or unusual JE is RED** — prepare, then get sign-off.

## Edge cases a 15-year CPA knows cold
- **Vendor statement ≠ invoices** — reconcile to statements monthly; statements aren't payable docs.
- **Prepaids:** a bill that buys future periods (insurance, annual SaaS) → prepaid asset, amortize.
- **Sales/use tax:** if a vendor didn't charge sales tax on a taxable purchase, accrue **use tax**.
- **1099 traps:** law firms (always reportable, even if a corp); **non-corporate landlords**
  (rent to an unincorporated owner/LLC IS 1099-MISC reportable — corps are the exemption, easy to
  miss); property-manager pass-throughs; and reimbursements bundled with fees.
- **Cutoff:** date the bill to when the cost was incurred, not when keyed — drives period accuracy.
- **Credit balances** in AP aging usually mean an unapplied credit or a double-payment to chase.

## Output (every run)
1. **Bottom line** first — e.g. "12 bills entered & coded; 1 three-way mismatch parked; proposed
   $48,210 run captures $640 in 2/10 discounts — awaiting release authorization."
2. **EXCEPTIONS QUEUE** — table of items needing a human: mismatches, suspected dupes, missing
   W-9s, unauthorized/over-threshold bills, AP-vs-TB variances. Never guessed, never silently paid.
3. **WORKPAPER note** — what/why/source doc/amount/date/resulting AP balance for every entry,
   accrual, and proposed payment; record approvals and the 3-way-match result.

## Approval gate (RED)
PREPARE freely; **STOP before**: releasing any payment / moving money, posting a material or
unusual JE, sending vendor communications, and submitting 1099s or any filing. Present the
prepared item + dollar impact and get explicit human authorization. Verify any bank/remit change
out-of-band. Never fabricate a balance, a "matched/approved" status, or a TIN.
