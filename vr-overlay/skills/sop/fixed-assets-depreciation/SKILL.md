---
name: fixed-assets-depreciation
description: "Use to maintain a client's fixed-asset register and run depreciation in QuickBooks: apply the capitalization / de minimis safe harbor policy to decide capitalize-vs-expense, add new assets to the register, compute book depreciation (straight-line or declining-balance), post the monthly depreciation JE, track accumulated depreciation, record additions and disposals with gain/loss, keep a tax-vs-book schedule for the return preparer, and reconcile the register to the GL fixed-asset and accumulated-depreciation accounts. Drives qb_account_list, qb_general_ledger, qb_journal_entry_create/_list, and the QB report tools. Produces: bottom-line summary, depreciation/disposal schedules, register-to-GL reconciliation, EXCEPTIONS QUEUE, and WORKPAPER notes. Trigger on 'run depreciation', 'book monthly depreciation', 'fixed-asset register', 'capitalize this asset', 'record a disposal/sale of equipment', 'depreciation schedule', or a recurring fixed-asset engagement."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Fixed-Assets, Depreciation, Capitalization, Disposals, Tax-vs-Book, QuickBooks, Workpaper, GAAP, IRC]
    related_skills: [month-end-close, financial-statement-prep]
---

# Fixed Assets & Depreciation

You own the fixed-asset register and the depreciation cycle. You **prepare, compute, and reconcile
autonomously (GREEN)**; you **draft but do not post** material/unusual entries — write-downs,
impairments, disposal gain/loss, and material true-ups — without human sign-off (**RED**). Goal: the
register ties to the GL to the penny, every asset depreciates on the right method/life, disposals are
clean, and the preparer gets a tax-vs-book schedule they can drop straight onto Form 4562 / M-1.

## When to use
Recurring monthly depreciation, a new acquisition, a disposal/trade-in, an annual register-to-GL
tie-out, or building the register for a new client. Confirm up front: the **period**, the **book**
**depreciation policy** (methods, useful lives, convention, salvage), the client's **written**
**capitalization policy**, and the **engagement materiality / posting threshold** separating a GREEN
routine entry from a RED sign-off entry. No written policy or no agreed threshold is itself an
exception — flag it; never invent a threshold to self-clear an entry into GREEN.

## Step 0 — Open the file (always first)
1. `qb_session_status` then `qb_company_info` — confirm the right company, live vs SIMULATION, period.
2. `qb_account_list` — identify every fixed-asset account, its paired **accumulated depreciation**
   (contra-asset) account, and the **depreciation expense** account. Note any asset class booked to
   the wrong account type.
3. Pull `qb_general_ledger` for those accounts and `qb_trial_balance_export` — these are your control
   balances. Save to the workpaper folder.

## Step 1 — Capitalize vs expense (capitalization policy)
- Apply the **de minimis safe harbor** (Treas. Reg. 1.263(a)-1(f)): expense items at/under the
  per-item or per-invoice threshold — **$2,500/item without an Applicable Financial Statement**,
  **$5,000/item with an AFS** — only if the client has the **written policy in place at the start of**
  **the year** and elects it annually on the return. **Verify current-year** thresholds and that the
  policy exists; the higher limit requires both an AFS and the policy.
- Above the threshold and with a useful life >1 year → **capitalize**. Include freight, installation,
  sales tax, and other costs to place the asset in service (capitalized cost, not just invoice price).
- Distinguish **repairs/maintenance** (expense) from **betterments/restorations/adaptations**
  (capitalize) per the tangible property regs (Treas. Reg. 1.263(a)-3). Routine maintenance safe
  harbor and small-taxpayer safe harbor may apply — **verify current-year** limits.
- Land is **not** depreciated; split land from building on a purchase. **Leasehold improvements** are
  tangible fixed assets — capitalize and depreciate them over the shorter of useful life or the
  remaining lease term — distinct from the **lease itself** (right-of-use asset / lease liability),
  which falls under ASC 842. Don't equate the two; flag the lease accounting, don't guess.

## Step 2 — Maintain the asset register
- For each asset record: ID/tag, description, class, **in-service date**, capitalized cost, salvage
  value, **method**, **useful life/recovery period**, convention, accumulated depreciation, net book
  value, location, and disposal status. The register is the authoritative subledger; the GL is the
  control total.
- New additions → add to the register with full cost detail (Step 1) before any depreciation runs.

## Step 3 — Compute book depreciation
- **Straight-line**: (cost − salvage) ÷ useful life, prorated by convention for the in-service period.
- **Declining-balance (e.g. 200%/150% DB)**: rate × beginning net book value; never depreciate below
  salvage; switch to straight-line in the year it yields a larger deduction if that's the policy.
- Apply the **half-year / mid-month / mid-quarter convention** consistently for the first and final
  periods. Book basis follows the client's GAAP policy and useful lives — **not** MACRS lives.
- An asset is depreciated only once **placed in service** (available for use), which can differ from
  the purchase date.
- Stop depreciating when accumulated depreciation = depreciable base (fully depreciated); keep the
  asset on the register at NBV (often salvage) until disposed.

## Step 4 — Post the monthly depreciation JE
- Standard entry, per asset account or summarized by class:
  - **Dr Depreciation Expense** / **Cr Accumulated Depreciation** — amount = the period's computed book
    depreciation.
- Routine, scheduled, below-threshold monthly depreciation that matches the standing schedule: post
  via `qb_journal_entry_create` with `dryRun` first to prove the entry, then for real, leaving a
  WORKPAPER note tying the amount to the depreciation schedule. `qb_journal_entry_list` to confirm it
  posted; `_update`/`_delete` only to correct your own current-period error before sign-off. Use
  `qb_journal_entry_batch_create` only for the routine per-class depreciation set, never to bundle a
  RED entry in with green ones.
- A catch-up / true-up (missed months, method correction, prior-period error) at or above the agreed
  materiality threshold, or any off-schedule/unusual entry, is **RED** — prepare, `dryRun`, and present
  for sign-off; do not post silently.

## Step 5 — Additions
- Confirm the asset hit the fixed-asset account (not expense) at full capitalized cost. If it was
  expensed in error and is material, prepare a reclass JE (**Dr Fixed Asset / Cr the expense**) — RED
  if material. Begin depreciation in the correct in-service period with the right convention.

## Step 6 — Disposals, sales & trade-ins
- On disposal, remove the asset: **Dr Accumulated Depreciation** (its full balance for that asset),
  **Dr Cash/Receivable** (proceeds, if any), **Cr Fixed Asset** (original cost), and **Dr Loss** or
  **Cr Gain** on disposal for the difference. The entry must balance and zero the asset out of both
  the cost and accumulated-depreciation accounts.
- Depreciate up to the disposal date first (partial-period per convention) before computing gain/loss.
- **Gain/loss on disposal is a RED entry** — prepare, `dryRun`, require sign-off. Note that tax gain/
  loss differs (different basis, §1245/§1250 recapture, like-kind nuances) — that's a tax-return item,
  flag it on the tax-vs-book schedule, don't book it to the books.
- Like-kind/trade-in: book the new asset and remove the old; tax deferral under §1031 is now **real**
  **property only** — **verify current-year** and leave §1031 treatment to the preparer.

## Step 7 — Tax-vs-book schedule (for the preparer)
- Maintain a parallel schedule: per asset, **book** cost/method/life/accum/NBV vs **tax** basis/MACRS
  class/convention/§179/bonus/accum. You compute book; you **flag** tax positions, you don't elect them.
- Note current-year **§179** expensing and **bonus depreciation** as awareness items — both have moving
  limits and were changed by recent legislation (OBBBA). **Verify current-year** §179 dollar cap,
  phase-out threshold, and the bonus depreciation percentage before stating any number; never quote a
  rate from memory. The §179/bonus election and the resulting M-1/Form 4562 entries are the **preparer's**
  call — you supply the schedule.

## Step 8 — Reconcile register to GL
- Tie the register's total cost to the GL fixed-asset account(s) and the register's total accumulated
  depreciation to the contra account(s), per `qb_general_ledger`. **Must tie to the penny.**
- Roll-forward each account: beginning + additions − disposals ± reclasses = ending; depreciation
  expense for the period must equal the JE posted in Step 4.
- Any variance → investigate (un-recorded disposal, asset booked to expense, depreciation posted to
  the wrong account, manual GL entry bypassing the register). Unexplained variance → EXCEPTIONS QUEUE.

## Edge cases a 15-year CPA knows cold
- Accumulated depreciation exceeding cost = over-depreciated (wrong life or double-posted) — investigate.
- Fully-depreciated assets still in use sit at NBV on the register; don't write them off until disposed.
- A debit balance in accumulated depreciation (contra should be a credit) signals a posted-backwards JE.
- Assets sold/scrapped but never removed inflate both cost and accum depreciation — reconcile to find them.
- "Repairs" line that spikes = a capitalizable betterment expensed; scan for items over the cap threshold.
- Constructed/CIP assets don't depreciate until placed in service; watch a stale CIP balance.
- Land lumped with building gets wrongly depreciated; split it.
- Book and tax depreciation diverging is normal (M-1) — they should **not** be forced to match.
- Bonus/§179 fully expensed an asset for tax while book still depreciates it — that's a deferred-tax
  timing difference, not an error.

## Required output
1. **Bottom line** (1-2 lines): e.g. "June book depreciation $X posted (Dr Depr Exp / Cr Accum Depr);
   register ties to GL to the penny; 1 disposal prepared awaiting sign-off; 1 mis-capitalized item in
   the exceptions queue." State the period and basis (book).
2. **Depreciation schedule** — per asset/class: cost, method, life, prior accum, current period, ending
   accum, NBV.
3. **Disposal schedule** (if any) — asset, proceeds, cost removed, accum removed, gain/loss, Dr/Cr.
4. **Register-to-GL reconciliation** — cost and accumulated depreciation roll-forwards, GL balance,
   variance, status (tied / open).
5. **Tax-vs-book schedule** — per asset book vs tax columns; §179/bonus flags marked "verify current-year".
6. **EXCEPTIONS QUEUE** — every mis-capitalized item, unrecorded disposal, GL variance, missing-policy
   flag, or ambiguous asset, each with the question for the partner. Never guessed.
7. **WORKPAPER note** per posted entry and per recon: what, why, source doc, amount, in-service/disposal
   date, resulting balance. The GL/TB before and after is the binder's control sheet.

## Approval gate
GREEN (autonomous): read, build/maintain the register, apply the capitalization policy, compute
depreciation, reconcile, build the tax-vs-book schedule, and post **routine, scheduled, below-threshold**
monthly depreciation that matches the standing schedule (`dryRun` to prove the entry, then real),
workpapers. RED (prepare, `dryRun`, then **require human sign-off** before posting): write-downs/
impairments, disposal gain/loss, reclasses or catch-up/true-up entries at or above the agreed
materiality threshold, any **unusual** or off-schedule entry regardless of size, and any §179/bonus
election. When materiality is undetermined or the entry is unusual, treat it as RED. Never fabricate
a balance, a tax figure, a current-year limit, or a "reconciled" status; never post a RED entry
without sign-off.
