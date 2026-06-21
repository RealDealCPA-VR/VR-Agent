---
name: quickbooks-operating-guide
description: "Operate QuickBooks Desktop safely and expertly through the qb_ MCP. Use whenever a task touches QB Desktop books: reading records/reports, classifying transactions, reconciling, prepping 1099s/W-2s, posting journal entries, creating invoices/bills, or month-end close. Covers the non-negotiable pre-flight (qb_session_status + qb_company_info), SIM-vs-LIVE confirmation, correct company file/period, dryRun before any mutation, editSequence/idempotency to avoid duplicate or stale writes, pagination iterators for large reads, closing-date discipline, and read-only-first exploration. Maps common accounting tasks to the exact qb_ tools and enforces the approval gate for any write."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [QuickBooks, Desktop, MCP, SOP, Reconciliation, Journal-Entry, Reports, 1099, Closing-Date]
    related_skills: [accounting, bookkeeping, tax-research, practice-management]
---

# QuickBooks Desktop — Operating Guide

You drive QuickBooks Desktop through the `qb_` MCP. This server has full read/write access
to a real firm's books. Treat every mutation as load-bearing: a stray call can create a
duplicate invoice, break a prior bank reconciliation, or write the wrong year's data.
**Read-only first; mutate only with intent, a dry-run, and a human sign-off.**

## When to use
Any task that touches QB Desktop bookkeeping: list/look-up records, run reports, classify
or memo-search transactions, reconcile a bank/CC statement, prep 1099s/W-2s, draft or post
a journal entry, create invoices/bills, or run month-end close. **Do not** open `qb_` tools
"to see what happens" — the books are live.

## Pre-flight — ALWAYS, before any other qb_ call
1. **`qb_session_status`** — confirm `connected: true`. Read `mode` (**live** vs **simulation**),
   `companyFile`, and the `readOnly` flag. Zero wire I/O — free to call.
2. **`qb_company_info`** — confirm the open `.qbw` is the **right client**. Wrong file →
   `qb_company_list` to discover, `qb_company_open` to switch. (In sim, `qb_company_open`
   resets the in-memory store: `simulationStoreReset: true`.)
3. **State mode and scope out loud** before doing anything: "LIVE — Acme Inc.qbw — accrual —
   FY2025." If `mode: simulation`, say so — numbers are mock and nothing reaches real books.
4. **Confirm the period and basis** (cash vs accrual) the task targets before reading reports
   or drafting entries. Reports take `basis` and dates; don't assume.
5. For pure exploration/diagnostics, prefer a **read-only session**:
   `qb_session_connect({ readOnly: true })` gates every mutation (returns `9001`). Toggle off
   with `qb_session_connect()` (no arg) when you're ready to write.

## Read-first task → tool map
| Task | Tool(s) |
|------|---------|
| Everything for a customer in a period | `qb_transaction_list({ customerName, fromDate, toDate, includeLineItems: true })` |
| Every line posted to an account | `qb_transaction_list_by_account({ accountName, fromDate, toDate })` |
| Find a transaction by memo | `qb_transaction_memo_search({ query, fromDate, toDate })` (a scope or date bound is required) |
| Trial balance | `qb_trial_balance_export({ asOfDate, basis })` |
| P&L / Balance Sheet / Cash Flows | `qb_pnl_report`, `qb_balance_sheet_report`, `qb_statement_of_cash_flows` |
| General Ledger | `qb_general_ledger` |
| AR / AP aging | `qb_ar_aging`, `qb_ap_aging` (as of period end) |
| Sales by customer | `qb_sales_by_customer_summary` / `qb_sales_by_customer_detail` |
| Sales by item | `qb_sales_by_item_summary` / `qb_sales_by_item_detail` |
| Expenses by vendor | `qb_expense_by_vendor_summary` / `qb_expense_by_vendor_detail` |
| Chart of accounts / customers / vendors | `qb_account_list`, `qb_customer_list`, `qb_vendor_list` |
| 1099 prep | `qb_1099_summary({ taxYear, formType: "NEC" })` → `qb_1099_detail({ vendorListId, taxYear })` |

## Mutation discipline (the rules that prevent damage)
- **Dry-run first — no exceptions.** Every mutation tool accepts `dryRun: true`, including the
  highest-risk RED composites: `qb_invoice_write_off`, the batch flows (`qb_invoice_batch_create`),
  the duplicate flows (`qb_invoice_duplicate`/`qb_bill_duplicate`), the convert-to-invoice flows
  (estimate/sales-order → invoice), and `qb_bill_pay`. Always dry-run before any real write.
  *Live-mode caveat:* composite/convert/batch tools return the **built QBXML envelope**
  (`previewSupported: false`) rather than an entity-after-mutation preview — so on those, confirm
  field mapping on a **single item** first, then scale. Single-entity creates/updates return a
  full result preview.
- **editSequence on every update/delete.** QB uses optimistic concurrency. **Re-list immediately**
  before the write to get a fresh `editSequence` (+ `ListID`/`TxnID`); never reuse one across
  prompts. Stale → `3170` (re-list and retry).
- **idempotencyKey on every retry-prone create.** Same key + same payload = safe replay
  (`idempotentReplay: true`). No key + a timeout retry = **a duplicate invoice/bill/JE.** Use a
  UUID per logical create. Different payload + same key → `9002` (use a fresh key).
- **Don't duplicate invoices/bills.** Before creating, search for an existing one
  (`qb_invoice_list` / `qb_bill_list` by customer/vendor + date + amount + ref/PO number). A
  matching ref number almost always means it's already entered.
- **Respect the closing date.** Never post into a closed period. `qb_closing_date_set` is an
  informational stub (returns `9005` with the manual UI path) — the closing date is set in QB's
  UI (Edit → Preferences → Accounting). If an entry must hit a closed period, that's an
  **EXCEPTIONS QUEUE** item for the partner, not a quiet override.
- **Make inactive, don't hard-delete.** Deleting an account/name with history returns `3260`.
  Use `qb_account_make_inactive` (history preserved) and note it.
- **Recurring work** uses `qb_*_duplicate({ sourceTxnId, ...overrides })` — the SDK has no
  memorized-transaction path.

## Large reads — pagination / iterators
7 list tools cap at ~500 rows (`qb_customer_list`, `qb_vendor_list`, `qb_account_list`,
`qb_employee_list`, `qb_invoice_list`, `qb_bill_list`, `qb_item_list`). For "give me everything,"
use **`autoExhaust: true`** (server-side; capped by `maxBatches`, returns `iteratorID` if capped),
or `paginate: true` and loop on `iteratorID` until `iteratorRemainingCount === 0`. Never assume
the first page is the whole list. `qb_item_list` requires `itemType` to paginate.

## Edge cases a 15-year CPA knows cold
- **SIM vs LIVE confusion is the #1 trap.** Sim numbers look real; never report sim figures as
  the client's books. Balance Sheet AS/LI/EQ in sim come from current `Account.Balance`
  (`asOfDate` advisory); the P&L walk is date-bounded in both modes.
- **Money:** wire is decimal strings; compute in integer cents or `toFixed(2)`. Prove JEs balance
  to the penny (`3030` = imbalance/invalid amount). Reconcile to the cent; report any variance and
  where it likely sits — never declare "reconciled" without proof.
- **Cache:** **Unfiltered** Account/Customer/Item/Terms/Class lists cache 5 min (`fromCache: true`);
  filtered calls always hit the wire and the cache clears on `qb_company_open`. After an out-of-band
  edit in the QB UI, `qb_cache_invalidate({ entity })` or pass `useCache: false`.
- **Edition/subscription gates:** `qb_audit_log` is Enterprise-only (`9003` otherwise — check
  `qb_host_query`). `qb_w2_summary` rejects two ways: `9003` on Pro edition (needs Plus/Enterprise)
  and `9004` when the payroll subscription is inactive/empty — read the code to know which gate
  you hit.
- **Status codes to read, not retry blindly:** `500` not found, `3120` missing/invalid field
  (read `hint.schemaOrder`), `3110` bad enum, `9005` no SDK write path (document the UI step).

## Approval gate (RealDeal safety model)
- **GREEN — autonomous:** read, run reports, classify, reconcile, memo-search, *prepare/draft*
  entries and workpapers, and dry-run any mutation.
- **RED — prepare, then REQUIRE human sign-off before the real write:** posting material/unusual
  journal entries (`qb_journal_*`), creating/paying bills or cutting payments (`qb_bill_pay`),
  any tool that **moves money** — customer payments, deposits, checks, transfers, sales-tax
  payments (`qb_payment_receive`, `qb_payment_apply`, `qb_deposit_create`, `qb_check_create`,
  `qb_transfer_create`, `qb_sales_tax_payment_create`), voiding/deleting, write-offs
  (`qb_invoice_write_off`), credit memos applied to a balance (`qb_credit_memo_apply`), and
  anything that **submits a tax/payroll filing or sends a client-facing document**. These RED
  items always require explicit human sign-off — they are **never** covered by a blanket
  pre-authorization. The agent dry-runs and stages the call; a human authorizes the commit.
- **Customer-facing AR creates** — issuing an invoice, sales receipt, statement charge, or
  credit memo (`qb_invoice_create`, `qb_sales_receipt_create`, `qb_statement_charge_create`,
  `qb_credit_memo_create`): each books AR/revenue and goes out to a client, so each needs an
  explicit confirmation. Routine, immaterial, individually-confirmed billing (≤ the engagement's
  materiality threshold — default **$1,000** per document absent a firm-specific figure) may be
  pre-authorized for a defined client/run; anything material, unusual, or batched
  (`qb_invoice_batch_create`, `qb_sales_receipt_batch_create`) is RED and requires sign-off.

## Required output
1. **Bottom line first** — e.g. "LIVE/Acme — TB ties; one $42.10 variance in Undeposited Funds."
   Always lead with mode (SIM/LIVE), company, period, and basis.
2. **Tables** for any set of numbers; show full Dr/Cr for entries and prove they balance.
3. **EXCEPTIONS QUEUE** — ambiguous or material items (closed-period hits, suspected duplicates,
   unexplained variances, missing source docs) listed for the partner. Never guessed.
4. **WORKPAPER note** for every action taken or staged: what, why, source doc, amount, date,
   tool + key params (and `idempotencyKey`/`editSequence` used), resulting balance, and SIM/LIVE.

## Worked sequences
**Month-end close** (use the `month_end_close` MCP prompt, or): per bank acct
`qb_uncleared_transactions` + `qb_cleared_status_update` → `qb_reconciliation_discrepancy` (catch
broken prior recs) → `qb_pnl_report` → `qb_ar_aging` + `qb_ap_aging` (as of period end) →
`qb_balance_sheet_report` + `qb_statement_of_cash_flows` → `qb_trial_balance_export` for the
workpaper → review vs prior period, list open items → close summary. **Post adjustments only
after sign-off.**

**Journal entry** → confirm accounts exist (`qb_account_list`) → draft Dr/Cr, prove it balances and
ties to a source → `qb_journal_entry_create({ ..., dryRun: true })` to verify mapping → **stop for
sign-off** if material/unusual → re-list for fresh `editSequence` if updating → post with a fresh
`idempotencyKey` → echo result + workpaper note.
