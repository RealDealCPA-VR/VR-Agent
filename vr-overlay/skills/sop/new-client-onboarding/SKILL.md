---
name: new-client-onboarding
description: "Stand up a brand-new client from scratch: intake (entity type, fiscal year, tax IDs, prior returns, bank/portal access), build/clean the chart of accounts, load opening balances and tie out the beginning trial balance, scope historical cleanup, wire systems/integrations, push engagement scope + deadlines into KarbonCopy, and build the durable client profile the firm learns from. Use at the very start of any new engagement, after a partner accepts the client, or when re-onboarding a messy book. Produces a workpaper-grade onboarding packet, an EXCEPTIONS QUEUE for the partner, and a persistent client profile. RED gates on opening JEs, money movement, and any filing; everything else is autonomous."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Onboarding, Intake, Chart-Of-Accounts, Opening-Balances, Trial-Balance, Engagement, Practice-Mgmt, Client-Profile, SOP]
    related_skills: [accounting, bookkeeping, practice-management, tax-research]
---

# New Client Onboarding

You are the new senior accountant setting up a client the firm just signed. Onboarding is
where you LEARN the client — every fact you capture now is reused by every later task, so
capture it once, exactly, and write it to the client profile. Do not guess; unknowns are
explicit TODOs, not silent gaps.

## When to use
- A partner accepted a new client and the books/files have not been set up in your systems.
- Re-onboarding an existing client whose books are a mess (treat history as cleanup scope).
- Migrating a client between accounting systems.

## Tools you drive
- **KarbonCopy MCP** — `list_clients`/`list_contacts` (dedupe before creating), `list_work`,
  `list_tasks`, `list_time`, `list_invoices`, `list_deadlines` — the system of record for the engagement.
- **QuickBooks Desktop MCP** (`qb_*`) — `qb_session_status` + `qb_company_info` FIRST, then
  `qb_company_list`/`qb_company_open`, `qb_account_*` (CoA), `qb_journal_entry_create` (opening
  entries — the canonical posting tool per the QuickBooks Operating Guide; always `dryRun: true`
  first), the QB report tools (Trial Balance / Balance Sheet to tie out).
- **vr-ledger MCP** — `validate`, `balances`, `balance_sheet`, `income_statement` for clients
  kept in ledger format or for a fast independent tie-out.
- **browser / web_search** — verify entity status on the state SoS, confirm current-year due
  dates, check EFTPS/DOR portal enrollment. **desktop MCP** — portals with no API.

## Procedure

**1. Intake (GREEN).** Collect and record to the client profile, marking each VERIFIED or TODO:
- Legal name + DBA; entity type (Sch C / 1065 / 1120-S / 1120 / 990); state(s) of formation
  and operation; EIN and (if applicable) state tax IDs / sales-tax permit.
- **Fiscal year end** and accounting basis (cash vs accrual) — drives every period after this.
- Tax classification and elections on file (S-elec **Form 2553**, accounting-method elections).
- Prior-year returns (federal + state), prior depreciation schedules / **Form 4562**, and the
  prior accountant's closing trial balance. Owner(s)/ownership %, responsible party.
- Bank/CC accounts, payroll provider, merchant processors; **portal/access notes only — never
  store live credentials in the profile** (note "credentials in firm vault", who holds them).
- Open payroll/sales-tax/1099 obligations and their filing status.

**2. Chart of accounts (GREEN).** `qb_account_list` (or vr-ledger `balances`) to read the
existing CoA. Map it to the firm's standard CoA and the tax-return line mapping for the entity
type. Clean: merge duplicates, mark inactive dead accounts (don't delete with history), fix
mis-typed account types (a liability sitting in equity throws the whole B/S). Adding accounts is
GREEN; **renaming/merging accounts that already hold posted history is a mutation — confirm
first.** Leave a workpaper note for every mapping decision.

**3. Opening balances & beginning-TB tie-out (mix).** Source of truth = the prior accountant's
final trial balance (or the most recent filed return's balance sheet, **Form 1120/1120-S Sch L
/ 1065 Sch L**). **Sch C / single-member LLC has no return balance sheet** (1040 carries no Sch L
and no Retained Earnings) — fall back to prior books + a bank/asset/loan schedule, and clear OBE
to **owner's capital/draws**, not Retained Earnings. Build the opening entry to Opening Balance
Equity, then clear OBE to the entity's equity (Retained Earnings for C/S-corp, members' capital
for a partnership, owner's capital for a sole prop). **For an S-corp, carry opening Retained
Earnings, the AAA/AE&P split, and shareholder stock/debt basis from the prior return — never plug
them** (see edge cases on negative RE / basis-in-excess-of-distributions; queue it, don't bury an
assumption inside the OBE clear). **Prove the beginning TB balances to the penny** via the QB report tools
(Trial Balance + Balance Sheet) or vr-ledger `validate`/`balance_sheet`. Reconcile each bank/CC
opening balance to the actual statement as of the conversion date. **Posting the opening JE is
RED** — prepare it, show full Dr/Cr, prove it balances, then get partner sign-off before posting
via `qb_journal_entry_create` (run `dryRun: true` first). A non-zero OBE after cleanup is an EXCEPTION.

**4. Historical cleanup scoping (GREEN).** Define the conversion date and how far back you must
rebuild: unreconciled periods, uncategorized transactions, negative AR/AP, suspense/ask-my-
accountant balances, commingled personal expenses, missing 1099 vendor W-9s. Estimate hours and
hand the partner a scoped cleanup plan + fee impact. Do **not** silently start a large cleanup —
scope it, queue it, get approval. Pre-conversion errors go to the EXCEPTIONS QUEUE, not fixed by
guess.

**5. Systems & integration setup (GREEN, money-touching parts RED).** Open/confirm the QB
company (`qb_session_status`, `qb_company_open`) — note SIMULATION vs live. Configure bank
feeds, document/receipt capture, payroll and sales-tax integrations. Verify portal enrollment
(EFTPS, state DOR, e-file/EFIN) via browser/desktop — **note status only; enrolling for payment
or initiating any e-file/payment is RED** and needs human authorization.

**6. Engagement scope & deadlines into KarbonCopy (GREEN).** Dedupe with `list_clients`/
`list_contacts` first, then create the client, contacts, the engagement/work item with scope and
billing terms, and the recurring deadlines for the entity: income tax (**1120/1120-S/1065/1040**)
+ extensions, payroll (**941** quarterly, **940** annual, **W-2**), **1099-NEC** (Jan 31),
state income/franchise, and sales-tax cadence. **Verify each current-year due date** (web_search
the IRS/state calendar) — write "verify current-year" rather than assume a shifted weekend date.

**7. Build the client profile (GREEN).** Persist a durable profile the whole firm reuses: entity
+ tax facts, FY/basis, CoA mapping decisions, conversion date, opening-balance source, system/
integration map, portal-access map (vault pointers, not secrets), key contacts, partner-in-
charge, quirks learned, and the open EXCEPTIONS QUEUE. This is the memory layer — keep it the
single source of truth and update it as facts get verified.

## Edge cases a 15-year CPA knows cold
- **Short first/initial year** or a fiscal-year election changes every due date — flag it.
- **S-corp without an accepted 2553** is a landmine; confirm the election before treating it as
  an S-corp. Mid-year S-election = split-year reporting.
- **Cash vs accrual mismatch** between the prior return and the books — reconcile before tie-out.
- **Negative retained earnings / basis issues** (S-corp distributions in excess of basis) —
  exception, not a plug.
- **Sales-tax nexus** in states beyond formation; **responsible-party** EIN data stale on file.
- Prior accountant's "final" TB that doesn't balance, or a Sch L that doesn't tie to it — stop
  and queue it; do not force OBE to zero.
- Mixing personal and business in the bank feed — scope as cleanup, never auto-categorize.

## Required output
1. **Bottom line** (1-2 lines): e.g. "1120-S, FYE 12/31, accrual; CoA mapped, beginning TB ties
   to $0 OBE pending JE sign-off; 3 exceptions for partner."
2. **Onboarding packet**: intake summary table, CoA mapping table, beginning-TB tie-out (Dr/Cr,
   proven to the penny), cleanup scope + hours, integration map, KarbonCopy deadlines created.
3. **EXCEPTIONS QUEUE**: every ambiguous/material item for the partner — never guessed.
4. **WORKPAPER note** for each decision: what, why, source doc, amount, date, resulting balance.
5. **Client profile** written/updated.

## Approval gate (RED — prepare, then require human sign-off)
Posting the opening journal entry or any material/unusual JE; renaming/merging accounts with
posted history; moving money or enrolling for payments; submitting or e-filing ANY tax/payroll
filing; sending client communications. The agent prepares and may pre-fill the portal/QB
(use `dryRun`), then a human reviews and authorizes the submit. Everything else above is
autonomous. Never fabricate a balance, a "reconciled" status, or a citation; when unsure on a
current-year figure or date, write "verify current-year".
