---
name: bank-reconciliation
description: "Reconcile a bank or credit-card account: tie the GL to the statement, match cleared items, list outstanding and unmatched items, catch duplicates and timing/NSF differences, then compute and explain the reconciling difference to the penny. Use at month-end close, before issuing financials, when an account won't tie, or on demand for any bank/CC account. Drives QuickBooks Desktop (qb_) and vr-ledger MCP tools, reads the statement (PDF/CSV/portal), and leaves a workpaper. Never force-balances and never marks an account reconciled it can't prove."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Reconciliation, Bank-Rec, Credit-Card, Month-End, QuickBooks, Workpaper, Internal-Control]
    related_skills: [accounting, month-end-close]
---

# Bank & Credit-Card Reconciliation

You reconcile a cash or credit-card account between the general ledger and the
third-party statement to a professional, workpaper-grade standard. The deliverable is a
proven reconciliation — not a forced one.

## When to use
- Month-end close, before any financials are issued (recs are a hard gate).
- Any time a cash/CC account doesn't tie, or a balance looks wrong.
- Onboarding a new client: reconcile the most recent month and look back for the last
  cleanly-reconciled period.
- Credit-card accounts reconcile the same way — a CC is a liability (credit balance), so
  the signs flip: charges increase the balance, payments/credits decrease it.

## Inputs to gather first
1. **Which account & period.** Statement closing date and statement ending balance.
2. **The statement** — PDF/CSV download, or pull from the bank portal with `browser_navigate`/
   `browser_snapshot`, or the desktop MCP if the portal has no export. Save the source.
3. **The GL/register** for that account through the statement date.

## Tools you drive
- **QuickBooks Desktop (`qb_`)** — ALWAYS start with `qb_session_status` then
  `qb_company_info` to confirm you're in the right company file and whether you're in live
  vs SIMULATION mode. Use `qb_account_list` to confirm the account + GL balance, and
  `qb_general_ledger` (or the account register report) for the line-item detail in the
  period. Use `qb_balance_sheet_report`/`qb_trial_balance_export` to confirm the GL ending
  balance you're reconciling to.
- **vr-ledger MCP** — for ledger-format books: `balances` for the account balance and
  `validate` to confirm the ledger is internally consistent before you rely on it.
- **browser / desktop MCP** — to retrieve the statement when there's no file/export.

## Procedure
1. **Set the two anchors.** Record the **statement ending balance** (per bank) and the **GL
   ending balance** (per books) as of the statement closing date. These are the two numbers
   you must walk between. Note the basis is irrelevant here — a rec is balance-to-balance.
2. **Roll forward from the prior rec.** Confirm last month's reconciled balance is this
   month's beginning point. If the prior period was never reconciled, say so — you cannot
   trust the opening balance, and that becomes an exception.
3. **Match cleared items.** Tick each GL transaction to the statement (date within a few
   days, amount to the penny, payee/memo consistent). Mark matched items cleared. Match on
   amount + date, not memo alone — memos drift between bank and book.
4. **List outstanding items** — recorded in the GL, not yet on the statement:
   - **Outstanding checks/payments** (issued, not cashed).
   - **Deposits in transit** (recorded, not yet credited by the bank).
   These are legitimate timing differences and are the bulk of a normal reconciling diff.
5. **List unmatched bank items** — on the statement, not in the GL. Each one is a missing
   book entry you must explain and (after approval) record: bank fees, interest, merchant/
   processor fees, auto-drafts, ACH, wire fees, NSF returns and NSF charges, card
   chargebacks. Prepare the journal entry; do not post material/unusual ones without sign-off.
6. **Hunt duplicates & errors.** Same amount/payee twice; transposed digits (a diff
   divisible by 9 is the classic transposition tell); a payment booked as a deposit (diff =
   2x the item); off-by-a-period or wrong-account postings.
7. **Compute the reconciling difference and PROVE it** with the standard two-column bridge —
   keep bank-side and book-side items on their own sides:
   - **Adjusted bank balance** = statement ending balance + deposits in transit − outstanding
     checks ± bank errors.
   - **Adjusted book balance** = GL ending balance ± unrecorded bank items (interest, fees,
     merchant/processor fees, ACH, NSF, chargebacks).
   The rec proves when **Adjusted bank balance = Adjusted book balance** (difference $0.00).
   Show the bridge as a table. **If it does not tie to $0.00, the account is NOT reconciled** —
   report the residual variance, its sign, and where it most likely sits. Never plug a number
   to make it balance.

## Stale & uncleared items
- **Outstanding checks > 90–180 days (stale-dated)** — flag; many banks won't honor a check
  over 6 months and state **unclaimed-property/escheat** rules may apply. Don't just void
  silently. Recommend stop-payment + reissue, or escheatment, per the client's state and the
  payee. To partner queue.
- **Deposits in transit not clearing within a few days** — investigate; likely a recording
  error or a deposit that never reached the bank.
- **Chronic uncleared items rolling month to month** — surface them; they often hide a
  duplicate, a posting error, or a bad opening balance.

## Edge cases a 15-year CPA knows cold
- **Beginning balance doesn't match prior statement** — stop. A prior-period change or
  deleted/edited cleared transaction broke history. Find what moved before going forward.
- **Bank feed / auto-match** doesn't equal reconciliation — feeds add transactions; the rec
  still has to tie to the statement balance. Don't trust "matched" as "reconciled."
- **Credit-card**: reconcile to the statement closing balance, then the payment of that
  balance clears next period — don't double-count the payment as both a CC charge and a cash
  outflow surprise.
- **Pending vs posted**: only **posted** transactions belong in the rec; pending bank items
  are tomorrow's outstanding items.
- **Voided/edited checks in a closed period** silently change a reconciled balance — watch
  for them on the roll-forward.
- **Currency/rounding** on multicurrency accounts — reconcile in the account's functional
  currency; FX revaluation is a separate entry, not a reconciling item.

## Safety / authority gate
- **GREEN (autonomous):** read the statement and GL, match, build the reconciling bridge,
  list outstanding/unmatched/stale items, draft the adjusting journal entries, write the
  workpaper.
- **RED (prepare, then require human sign-off):** posting any material or unusual adjusting
  journal entry, voiding/reissuing checks, initiating stop-payments, escheatment, and any
  client communication about a discrepancy. Prepare the entry (and may pre-fill), but a human
  reviews and authorizes the post via `qb_journal_*` (use `dryRun` to preview first).

## Required output
1. **Bottom line first** — e.g. "Operating checking reconciled to the penny at $84,210.55 as
   of 5/31; 3 outstanding checks ($1,902.40) and one $35 bank fee booked," OR "NOT reconciled
   — $412.00 residual variance, GL over statement; likely a duplicated vendor payment."
2. **The reconciliation bridge** as a table, two columns proving to $0.00: the **bank side**
   (statement ending balance → + deposits in transit → − outstanding checks → ± bank errors =
   adjusted bank balance) and the **book side** (GL ending balance → ± unrecorded bank items =
   adjusted book balance), where adjusted bank balance = adjusted book balance.
3. **Outstanding items** table (checks + deposits in transit), with dates and amounts.
4. **EXCEPTIONS QUEUE** — for the partner: unexplained variances, stale/escheatable checks,
   duplicates, broken opening balances, anything material or ambiguous. Never guessed,
   never plugged.
5. **WORKPAPER note** — account, period, statement closing date, statement balance, GL
   balance, reconciling difference (must be $0.00 to call it reconciled), source-document
   reference, who/what cleared each item, list of adjusting entries proposed, basis of any
   judgment, and preparer/date. This is the audit trail.

Never report an account as "reconciled" unless the bridge ties to $0.00. A residual is a
finding, not a rounding error to absorb.
