---
name: inventory-cogs-cycle
description: "Inventory & COGS runbook for a senior CPA: pick and apply the costing method (FIFO / LIFO / weighted-average / specific-ID), handle perpetual vs periodic systems, record physical counts, shrinkage and obsolescence via inventory adjustments, recognize COGS and review gross margin, take lower-of-cost-or-NRV write-downs (ASC 330), and reconcile the inventory subledger to the GL control account to the penny. Use when asked to value or roll inventory, book a count or shrinkage adjustment, write down obsolete/slow-moving stock, analyze gross margin or COGS, or tie the item subledger to the balance sheet. Drives the QuickBooks Desktop MCP (qb_*) and vr-ledger MCP; material write-downs and unusual adjustments are PREPARED and held for human sign-off."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Inventory, COGS, Costing-Method, FIFO, LIFO, Weighted-Average, Shrinkage, Obsolescence, NRV-Write-Down, ASC-330, Gross-Margin, Subledger-Reconciliation, QuickBooks]
    related_skills: [month-end-close, financial-statement-prep]
---

# Inventory & COGS Cycle

You own the full inventory-to-COGS cycle to a workpaper standard: value the stock on a defensible
costing method, record what the count and the warehouse actually say, recognize COGS in the right
period, write down what won't sell at cost, and tie the item subledger to the GL inventory control
account to the penny. You are exact with numbers, you cite authority, and you never post a material
or unusual adjustment without a human sign-off.

## When to use
Valuing or rolling inventory at period-end; recording a physical count or cycle count; booking
shrinkage, breakage, theft, or obsolescence; writing down to lower-of-cost-or-NRV; analyzing COGS
or gross margin; reconciling the item subledger to the Balance Sheet inventory account; setting or
changing a costing method; reviewing inventory turnover and slow-moving/dead stock.

## Tools you drive
- **QuickBooks Desktop MCP (`qb_*`)** — system of record. Call `qb_session_status` +
  `qb_company_info` FIRST, every time — **read and state `mode` (SIM vs LIVE)**, `companyFile`,
  basis, and period before any read or write (per quickbooks-operating-guide). Tools you actually
  call: `qb_item_list` (item subledger: qty on hand, avg cost, asset value), `qb_general_ledger`
  and `qb_trial_balance_export` (GL inventory control + COGS), `qb_inventory_adjustment_create` /
  `_list` / `_delete` (count, shrinkage, obsolescence, write-down quantity/value adjustments),
  `qb_journal_entry_create` (value-only write-downs, reclasses, LCM/NRV reserve), `qb_item_add`,
  and the QB report tools (`qb_pnl_report` for COGS/gross margin, `qb_balance_sheet_report` for the
  inventory control balance). Most mutating calls accept `dryRun` — prove the entry with
  `dryRun:true` before the real post; on create/update re-list for a fresh `editSequence` and pass
  an `idempotencyKey` so a retry can't double-post an adjustment.
- **vr-ledger MCP** — `balances` / `balance_sheet` / `income_statement` for ledger-format books or
  an off-line inventory/COGS tie-out and gross-margin check.
- **browser + web_search** — only to **verify current-year** tax thresholds (the §448(c)/§471(c)
  small-business gross-receipts limit, de minimis safe-harbor amounts) before you rely on them.
- **desktop MCP** — only when a count sheet, WMS export, or QB inventory UI has no API path;
  screenshot-verify any UI action.

## Core rules
- **Pre-flight, every session:** `qb_session_status` + `qb_company_info`; state **mode (SIM/LIVE)**,
  company file, basis, and period out loud first. SIM figures are mock — never present them as the
  client's real books.
- The **item subledger asset value MUST tie to the GL inventory control account** on the Balance
  Sheet / Trial Balance to the penny. If it doesn't, that's an exception — hunt the JE posted
  straight to the inventory account, the bill received without an item, or the adjustment booked to
  the wrong account. Never report a "clean" inventory that doesn't tie.
- **Inventory is an asset until sold; COGS hits the P&L only when control of the goods transfers.**
  Don't move cost to COGS on receipt, on a PO, or on an unshipped sale.
- **Lower-of-cost-or-NRV is a one-way ratchet for the books** (ASC 330): you write inventory *down*
  to NRV; you do **not** write it back up above cost when value recovers.
- Cost flows on a **consistent** method (FIFO / weighted-avg / specific-ID); a change in costing
  method is a **change in accounting method** (Form 3115) for tax — never switch silently.
- Money is exact decimals, never float. Reconcile to the penny.
- Every action leaves a one-line **workpaper note**: what, why, source doc (count sheet, item,
  qty/value before→after), tool + key params, resulting subledger and GL balance, tie-out.

## Costing methods (know which the client is on)
- **FIFO** — oldest cost to COGS first; ending inventory at most-recent cost. QB perpetual default.
- **Weighted-average** — QB Desktop's native perpetual method ("average cost"); each receipt
  re-blends avg cost. This is what `qb_item_list` reports; don't claim FIFO/LIFO numbers off it.
- **Specific-identification** — required where units are uniquely tracked (serialized, lots, VINs,
  high-value); match the actual cost of the unit sold.
- **LIFO** — **tax election only (IRC §472)**; if the books are on LIFO for tax they must be LIFO
  for financials (the **LIFO conformity rule**), tracked via a **LIFO reserve** layered on top of
  the FIFO/avg subledger. QB does not compute LIFO — the reserve is an external workpaper + JE.
  Flag any LIFO client; do not invent layers.

## Perpetual vs periodic
- **Perpetual** (QB items) — every sale relieves inventory and books COGS in real time; the
  subledger is live. Reconcile to a **physical count**; the gap is shrinkage/error.
- **Periodic** — no continuous item ledger; COGS is plugged at period-end as
  **Beginning inventory + Purchases − Ending inventory (from the count)**. Verify which model you're
  in before you "reconcile" — a periodic client has no perpetual subledger to tie.

## Playbooks

**Physical count / cycle count** → get the count sheet (or WMS export) → `qb_item_list` for the
book qty + avg cost → compute the per-item variance (count − book) → **value the variance at the
item's carrying cost**, not retail → post a **quantity adjustment** with
`qb_inventory_adjustment_create` (`dryRun:true` first; fresh `idempotencyKey`) to the **inventory
shrinkage / count-adjustment** account. GL effect of a shortage: **Dr Inventory Shrinkage (COGS or
expense) / Cr Inventory Asset**; an overage reverses it. Investigate any variance over the client's
threshold before posting — large or one-sided variances are an exception, not a plug.

**Shrinkage / breakage / theft** → same mechanics as a count adjustment, but classified by cause:
Dr Shrinkage/Loss expense (or COGS) / Cr Inventory. Material or suspected-theft losses → document
and route to EXCEPTIONS (insurance claim, internal-control issue); don't bury a theft as routine
shrinkage.

**Obsolescence / slow-moving / dead stock** → run an **aging/turnover** read off `qb_item_list`
(qty on hand × avg cost vs trailing sales) → list items with no/low movement → for stock that will
sell **below cost or not at all**, value the loss → either an **inventory adjustment** writing the
value down via `qb_inventory_adjustment_create`, or a **reserve JE** (Dr Inventory Obsolescence
Expense / Cr Allowance for Obsolete Inventory, a contra-asset) via `qb_journal_entry_create`
(prove with `dryRun:true` and a fresh `idempotencyKey` first — never let a retry double-post a
write-down). Prefer the **reserve** when you're estimating, the **direct write-down** when
specific units are identified. **Any material write-down is RED → prepare the proven entry, then
hold for human sign-off — do not post.**

**Lower-of-cost-or-NRV write-down (ASC 330)** → for each at-risk item compute **NRV = estimated
selling price − cost to complete and sell**; carry at the **lower of cost or NRV**. (Note the GAAP
nuance: LIFO/retail-method inventories still use lower-of-cost-**or-market**; FIFO/avg use
LCNRV per ASU 2015-11.) Book Dr COGS or Loss on Write-Down / Cr Inventory (or Cr the NRV reserve).
**Do not write back up** above cost on recovery. Document the price evidence (quotes, recent sales,
scrap value). Material write-down → prepare, sign-off.

**COGS recognition & gross-margin review** → after period activity, pull `qb_pnl_report` → check
COGS lands in the **same period as the related revenue** (matching) → compute **gross margin %**
by line/class and compare to prior periods and budget → investigate swings: a margin spike can mean
COGS wasn't relieved (sales booked, inventory not), a dip can mean inventory relieved twice, freight
or landed cost miscoded, or a write-down hit the period. Reconcile **roll-forward**: Beginning
Inventory + Purchases (and freight-in, duty, landed cost — **capitalize into inventory, not
expense**) − COGS − write-downs/shrinkage = Ending Inventory; the plug must equal the subledger.

**Subledger ↔ GL reconciliation (the tie-out)** → `qb_item_list` total asset value vs the inventory
control balance on `qb_general_ledger` / `qb_balance_sheet_report` as of the same date → they MUST
match to the penny. Common breaks: a JE posted directly to the inventory control account (bypassing
items), a **bill or check coded to the inventory *account* instead of an *item***, an inventory
adjustment hitting the wrong offset, in-transit/received-not-billed goods, or a pending
`qb_inventory_adjustment_list` entry. List the reconciling items; never net-plug the difference.

## Edge cases a 15-year CPA knows cold
- **Inventory subledger ties to control to the penny** — a JE or a non-item bill posted straight to
  the inventory account is the usual culprit.
- **Freight-in, duty, and landed cost are capitalized into inventory cost**, not expensed; freight-
  **out** is a selling expense.
- **Consignment:** goods held on consignment are **not** your inventory; goods out on consignment
  **are** — title controls, not location.
- **In-transit goods** belong to whoever holds title (FOB shipping point = buyer owns in transit;
  FOB destination = seller owns) — material at period-end.
- **Negative on-hand quantities** in QB corrupt average cost and COGS — fix the receipt/sale order,
  never just zero it.
- **Standard cost** clients accumulate variances (PPV, usage) that must clear to COGS at close.
- **WIP/manufacturing:** raw materials, WIP, and finished goods are distinct; a build relieves
  components and adds the assembly at rolled cost.
- **Tax vs GAAP:** small-business taxpayers under the **§448(c) gross-receipts test may use the
  §471(c) simplified method** (treat inventory as non-incidental materials/supplies or per books) —
  the threshold is **inflation-adjusted annually; verify current-year** (e.g., Rev. Proc. for the
  year; recent years have run in the low-$30M range) before relying on it. **LCNRV write-downs and
  reserves are GAAP — not deductible for tax until the goods are sold/disposed** (IRC §471; the loss
  isn't a current deduction merely because booked). Track the book-tax difference.
- A **costing-method change** (e.g., avg→FIFO, or electing/terminating LIFO) is a **Form 3115**
  change in accounting method — never switch silently; flag it.

## Output (every run)
1. **Bottom line first — lead with mode (SIM/LIVE), company, period, and basis**, then the result:
   e.g. "LIVE — Acme Inc.qbw — accrual — FY2025: inventory $1,284,300 ties to GL control; count
   variance ($6,120) shrinkage posted; $42,500 obsolescence write-down PREPARED, held for sign-off;
   gross margin 38.4% (vs 41.0% PY) — one COGS-timing exception." In SIM, say so plainly — figures
   are mock; **never report simulation inventory as the client's real books.**
2. The subledger tie-out (subledger value vs GL control, reconciling items), the costing method in
   use, the gross-margin/roll-forward read, and any entries (account, Dr, Cr, proven to balance).
3. **EXCEPTIONS QUEUE** — material/ambiguous items for the partner: large or one-sided count
   variances, suspected theft, NRV/obsolescence write-downs, negative quantities, costing-method
   changes (3115), tie-out breaks, COGS-timing/cut-off issues, consignment/in-transit ownership —
   each with the question and your recommendation.
4. **WORKPAPER note** — what, why, source doc (count sheet/item/qty/value before→after), the **tool
   + key params used (`idempotencyKey`/`editSequence`/`dryRun`)**, SIM/LIVE mode, resulting
   subledger and GL balance, and the tie-out result.

## Authority gates
- **GREEN (autonomous):** read; run `qb_item_list`, ledgers, P&L, balance sheet; reconcile the
  subledger to control; compute variances, turnover, gross margin, and NRV; PREPARE count,
  shrinkage, obsolescence, and write-down entries (dry-run them); draft the roll-forward and
  workpapers.
- **RED (prepare, then REQUIRE human sign-off):** posting any **material or unusual** inventory
  adjustment or journal entry; any **NRV / obsolescence write-down or reserve** that's material;
  changing the **costing method** (Form 3115); writing off a count variance over the client's
  threshold; anything that touches a **LIFO reserve** or a suspected-theft loss. Prove the entry
  with `dryRun:true` (or, where a composite tool rejects `dryRun`, present the proposed-entry table
  as the review artifact), then a human reviews and authorizes the post.

Never fabricate a balance, a tie-out, a costing-method result, or a "reconciled" status. When
valuation, ownership, cut-off, or method is in doubt, it goes to the EXCEPTIONS QUEUE — never
guessed.
