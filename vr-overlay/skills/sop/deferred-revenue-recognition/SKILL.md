---
name: deferred-revenue-recognition
description: "Recognize revenue under ASC 606 and run the deferred/unearned-revenue waterfall for a QuickBooks client: classify each contract through the 5-step model, build and roll the deferral schedule, recognize the period's earned portion, true-up over/under-billing (contract asset vs contract liability), and handle bundles, variable consideration, and contract modifications, then tie the deferred-revenue liability to the schedule and GL to the penny. Use when a client takes prepayments or sells subscriptions/SaaS, annual contracts, retainers, gift cards, milestone or %-of-completion work, maintenance/support, or any 'invoice now, earn later' arrangement — and at every close to release earned revenue. Drives the QuickBooks Desktop MCP (qb_journal_*, qb_invoice_*, the QB report tools) and vr-ledger. Recognizing revenue per a built schedule is GREEN; posting a material or judgmental recognition/true-up JE, or changing a recognition policy, is RED (human sign-off). Feeds month-end-close and financial-statement-prep."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Revenue-Recognition, ASC-606, Deferred-Revenue, Subscriptions, GAAP, Close, Workpaper]
    related_skills: [month-end-close, financial-statement-prep]
---

# Deferred Revenue & ASC 606 Recognition

I am RealDeal CPA. This SOP decides WHEN revenue is earned and moves it out of the deferred-revenue (contract-liability) account on the right schedule. It is the engine that `month-end-close` and `accounts-receivable` only touch lightly. Building and rolling a schedule and recognizing scheduled revenue are analysis/bookkeeping (autonomous). Posting a MATERIAL or judgmental recognition/true-up entry, or setting/changing a recognition policy, is a financial-statement assertion (sign-off required).

## When to use
- Client takes cash or invoices BEFORE delivery: subscriptions/SaaS, annual or multi-year contracts, retainers, prepaid services, memberships, gift cards/store credit, deposits, maintenance/support, warranties sold separately.
- Performance happens over time: milestone, percentage-of-completion, usage-based, or staged delivery.
- Bundled deals (software + implementation + support), discounts across elements, rebates, refunds, or variable/contingent fees.
- Every period close — release the earned slice and re-tie the liability.
- A contract is modified, renewed, cancelled, or partially refunded.

Do NOT use this to chase cash or age receivables — that is `accounts-receivable`. This SOP answers only "how much of what we've billed/collected is *earned* this period, and what stays deferred."

## Authority (ASC 606 is stable; client-specific terms and any rates are verified per engagement)
- **ASC 606-10** — *Revenue from Contracts with Customers*. The **5-step model**: (1) identify the contract; (2) identify the performance obligations; (3) determine the transaction price; (4) allocate it to the obligations (by **standalone selling price**, ASC 606-10-32-31); (5) recognize revenue as/when each obligation is satisfied — **over time** (606-10-25-27) or at a **point in time** (606-10-25-30).
- **Contract liability** (deferred/unearned revenue) vs **contract asset** vs receivable — ASC 606-10-45. A net liability when billings exceed earned revenue; a net asset when earned exceeds billings.
- **ASC 340-40** — incremental costs to obtain a contract (e.g., sales commissions) are capitalized and amortized over the benefit period, not expensed on sale, unless the amortization period is ≤1 year (practical expedient).
- **Variable consideration** (606-10-32-5 et seq.) — estimate via expected-value or most-likely-amount and apply the **constraint**: only include amounts that are *probable* of not significantly reversing.
- I do NOT fabricate a client's standalone selling prices, contract terms, or any tax/discount rate. Where a figure depends on facts I cannot see, I write **"verify current-year / confirm with contract"** and route it to the EXCEPTIONS QUEUE. Tax treatment of advance payments (e.g., IRC §451(c) deferral) is a **tax** position — flag it, do not assume book = tax.

## Procedure

1. **Open + scope.** `qb_session_status` and `qb_company_info` FIRST to confirm the right entity/file and the reporting **basis (accrual vs cash)** — ASC 606 is an accrual concept; on a cash-basis file, deferred revenue is a memo/workpaper adjustment, not a posted balance. Confirm the recognition **policy** already in use (don't silently change methods).

   - If no deferral schedule exists yet, reconstruct one from contracts/invoices before recognizing anything — never recognize off the GL balance alone.

2. **Inventory open contracts and the current liability.** Pull the deferred-revenue balance and its detail:
   - `qb_balance_sheet_report` / `qb_balance_summary` for the deferred-revenue (unearned) liability balance.
   - `qb_general_ledger` on the deferred-revenue and revenue accounts for the GL trail; `qb_account_list` to confirm the exact accounts.
   - `qb_invoice_list` and `qb_payment_receive`/`qb_deposit_create` history to find advance billings and prepayments that should sit in deferred revenue (not revenue).
   - Cross-check against vr-ledger `balance_sheet` / `income_statement` if a parallel ledger exists, and reconcile to any external billing/subscription system.

3. **Run the 5-step model per contract.** For each open arrangement: confirm an enforceable contract (step 1); list distinct performance obligations (step 2 — e.g., software license vs setup vs support are usually separate); set the transaction price including variable consideration under the constraint (step 3); allocate by relative standalone selling price (step 4 — verify SSP per element); pick the recognition pattern (step 5 — ratable over the service period, point-in-time on delivery, or measured by progress for over-time obligations). Document the judgment for each.

4. **Build / roll the deferral schedule.** For each contract, schedule the recognition by period (start date, total deferred, method, per-period amount, remaining balance). This schedule — not the GL — is the source of truth; the GL ties TO it. Update it for new billings, modifications, and refunds before computing this period's release.
   - **Split current vs long-term at initial booking, not just at close.** When you first defer a multi-period billing, classify the portion that will be earned within 12 months of the balance-sheet date as a current liability and the remainder as non-current; carry both columns on the schedule so each close reclasses the rolling slice automatically instead of re-deriving it. A 36-month prepaid SaaS deal is ~1/3 current, ~2/3 long-term on day one — booking the whole amount to a single current account overstates current liabilities and distorts working-capital ratios.

5. **Compute the period recognition + true-up.** From the schedule, total the amount earned this period and the residual that stays deferred. For **over-time** obligations, measure progress with a consistent **input** method (cost-to-cost, labor hours) or **output** method (units/milestones delivered) per ASC 606-10-25-31 — apply the same method to similar obligations; don't switch methods to shape results. Identify over/under-billing per contract: where earned > billed, recognize a **contract asset**; where billed > earned, it remains a **contract liability**. Catch revenue sitting in the wrong account (booked straight to income on invoice when it should have deferred).

6. **PREPARE the recognition JE(s) (dryRun first).** Standard release of earned revenue:
   - **Dr** Deferred/Unearned Revenue (liability) / **Cr** Revenue — for the earned slice, via `qb_journal_entry_create` (use `qb_journal_entry_batch_create` for many contracts; run with `dryRun` first).
   - Initial advance billing routed correctly: **Dr** Cash or AR / **Cr** Deferred Revenue (not income).
   - Contract-cost capitalization (ASC 340-40): **Dr** Capitalized Contract Cost (asset) / **Cr** Commission Expense at inception; then **Dr** Amortization / **Cr** the asset over the benefit period.
   - Refund/cancellation: reverse unearned portion **Dr** Deferred Revenue / **Cr** Cash or Refund Payable; reverse any over-recognized revenue.
   - Current/long-term reclass at close: **Dr** Deferred Revenue – Long-Term / **Cr** Deferred Revenue – Current for the slice now falling within 12 months (or maintain via the schedule's two columns and a single reclass JE) so the balance sheet presents the split correctly.
   Immaterial, scheduled ratable releases are autonomous; material or judgmental entries are PREPARED and held (see gate).

7. **Tie out + analytical review.** After posting, re-pull `qb_balance_sheet_report` and `qb_general_ledger`: the deferred-revenue GL balance MUST equal the sum of remaining schedule balances — reconcile to the penny. Review recognized revenue for reasonableness (recognized this period vs billings vs prior trend); a deferred-revenue balance that only grows or only shrinks is a red flag. Confirm the current vs long-term split posted in step 6 still agrees to the schedule after the period roll (portion earned beyond 12 months is non-current).
   - **Roll-forward proof:** opening deferred + new billings deferred − recognized this period − refunds/cancellations = closing deferred. Tie this to BOTH the schedule total and the GL balance; an unexplained plug here is an exception to queue, never a rounding fix.

8. **Document for re-run.** Capture the as-of date, every QB report pulled (with dates), the deferral schedule, SSP basis, recognition method per contract, and the JEs into the workpaper so next period rolls the same schedule and the position is audit-defensible.

## Edge cases a 15-year CPA flags
- **Bundled software + services**: license (often point-in-time), implementation (over time), and support (ratable) are usually *separate* obligations with *different* timing — recognizing the whole invoice ratably is a classic error.
- **Gift cards / store credit**: recognize on redemption; estimate **breakage** (unredeemed) per ASC 606-10-55-46 — verify the client's breakage rate, don't invent one.
- **Contract modifications**: a renewal or scope change may be a separate contract, a prospective change, or a cumulative catch-up (606-10-25-10) — pick the right treatment; it changes the schedule.
- **Variable consideration & the constraint**: don't recognize contingent fees/bonuses until probable of not reversing; revisit each period.
- **Material right / loyalty points**: a discount on future purchases can be its own performance obligation — defer a slice of today's price.
- **Principal vs agent** (606-10-55-36): if the client is an agent, revenue is the *net* fee, not gross — misclassifying inflates revenue.
- **Non-refundable upfront fees** (setup/activation): usually deferred over the expected service period, not earned at signing.
- **Over-time vs point-in-time misjudgment**: an obligation only qualifies for over-time recognition if it meets one of the three 606-10-25-27 criteria (customer consumes as you perform, you create/enhance a customer-controlled asset, or no-alternative-use asset + enforceable right to payment). If none apply, it's point-in-time — recognizing it ratably overstates early-period revenue.
- **Significant financing component** (606-10-32-15): multi-year prepaid or long-deferred-payment contracts may require imputing interest — verify whether the >1-year practical expedient applies.
- **Usage-based / metered / consumption billing**: when the price is a fixed rate per unit of usage that corresponds directly to value transferred, the **right-to-invoice expedient** (606-10-55-18) lets you recognize the amount you have the right to bill each period — there is no deferral for the variable usage piece. But a *fixed* platform/minimum commitment bundled with metered overage is two streams: ratably recognize the fixed minimum and recognize overage as consumed; don't lump metered revenue into the ratable schedule, and don't defer usage already delivered.
- **Book ≠ tax**: advance payments may be taxable on receipt or eligible for §451(c) one-year deferral — that's a tax position; flag to the preparer, never assume.
- **Cash-basis file**: deferred revenue is a workpaper adjustment only; don't post a contract liability the client's basis doesn't support.

## Required output
1. **Bottom-line summary** — one paragraph: revenue recognized this period, deferred-revenue balance carried forward (current vs long-term), whether the GL ties to the schedule, and the single most material judgment or exception.
2. **DEFERRAL WATERFALL** — one row per contract: `Contract | Customer | Total deferred | Method (ratable/point-in-time/progress) | Obligation(s) | Recognized this period | Remaining deferred | Current vs LT | Schedule end`.
3. **EXCEPTIONS QUEUE** — anything I could not resolve autonomously: unknown/contested standalone selling prices, ambiguous performance obligations, unverified breakage rates, unconstrained variable consideration, suspected revenue booked to income that should be deferred (or vice versa), contract mods needing a judgment call, book-vs-tax (§451(c)) questions, missing contract terms. Each item: what's missing, why it matters, what I need.
4. **WORKPAPER note** — record data sources (QB reports + dates, the deferral schedule, SSP basis, recognition method and judgment per contract, the JEs posted), methodology, assumptions, and conclusions, so the position is defensible on audit and re-runnable next period.

## Approval gate
Building/rolling the schedule, computing recognition, reconciling the liability, and recognizing **immaterial, routine, already-scheduled** ratable revenue are **autonomous (GREEN)**. The following are **PREPARE then REQUIRE human sign-off (RED)** — I draft the package, run mutating QB tools with `dryRun`, and stop:
- Posting any **material** revenue-recognition or true-up JE, any **catch-up/cumulative** adjustment, or a contract-modification re-allocation.
- **Setting or changing a recognition policy or method**, SSP allocation basis, or breakage estimate.
- Recognizing revenue that depends on a **judgmental** call (variable-consideration constraint, principal-vs-agent, distinct-obligation determination).
- Any **refund, write-off, or reversal** of previously recognized revenue.

I do not change how revenue is recognized, nor post a material entry, without a human approving the specific contract, method, and amount.
