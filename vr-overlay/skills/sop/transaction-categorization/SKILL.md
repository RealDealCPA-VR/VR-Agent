---
name: transaction-categorization
description: "Code bank/credit-card/feed transactions to the correct GL account using the client's own chart of accounts and prior-month coding precedents. Use for daily/weekly bookkeeping passes, pre-close cleanup, or any 'categorize these transactions' request. Resolves the hard calls a 15-year CPA makes cold: COGS vs operating expense, capitalize vs expense (de minimis safe harbor, IRC 263(a) / Treas. Reg. 1.263(a)-1(f), $2,500/item), personal vs business, owner draws vs payroll, transfers, sales-tax collected, meals vs travel (IRC 274), and contractor vs employee (1099-NEC vs W-2). Scores confidence per line, auto-codes the obvious, and routes ambiguous or material items to the EXCEPTIONS QUEUE. Drives QuickBooks Desktop MCP; enforces consistency through client memory."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Bookkeeping, Categorization, Chart-Of-Accounts, COGS, Capitalization, De-Minimis, Contractor-Vs-Employee, QuickBooks, SOP]
    related_skills: [accounting, bank-reconciliation, month-end-close, tax-research]
---

# Transaction Categorization

You code uncategorized transactions to the correct GL account using the **client's own
CoA** and their **prior coding precedents** — not generic defaults. Consistency beats
cleverness: a vendor coded to "Subcontractors" last month is coded there again unless
something changed. Auto-code the clear ones; everything ambiguous or material goes to the
partner. You never guess on the books.

## When to use
Daily/weekly feed passes, pre-close cleanup, onboarding a backlog, or any "categorize
these" / "what account does this go to" request.

## Step 0 — Load context (always, in order)
1. `qb_session_status` → confirm live vs SIMULATION. 2. `qb_company_info` → confirm the
   right company file is open. 3. `qb_account_list` → pull the **actual CoA** (names, type,
   active). Never invent an account; if the right one doesn't exist, that's an exception.
4. Pull **precedents**: `qb_general_ledger` (or vendor history) for the last 1-3
   months + the client memory file `clients/<id>/coding-rules.md`. Build a vendor→account
   map (e.g. "Shell → Auto:Fuel", "ADP → Payroll Liabilities").
5. Note **basis** (cash/accrual) and the **entity type** (Sch C / 1120-S / 1065) — it
   changes owner-pay and meals treatment.

## Decision tree (apply top-down; first match wins)
1. **Transfer / internal move?** Money between the client's own accounts (bank↔bank,
   bank↔owned CC, loan paydown of principal). → Transfer, **not** income/expense. Never let
   a transfer hit P&L. Loan payments split: principal→liability, interest→Interest Expense.
2. **Owner money?** Owner taking cash out:
   - S-corp/C-corp owner-employee → must run through **payroll** (W-2, reasonable comp,
     IRC 162/§1.162-7); a raw transfer to owner is a Shareholder Distribution or Loan, and
     under-paid reasonable comp is an **exception** (IRS recharacterization risk).
   - Sole prop / partnership → **Owner's Draw / Partner Distribution** (equity), never an
     expense. Owner contributions → Owner's Equity.
3. **Personal vs business?** Personal spend on a business card → **Owner's Draw / Due from
   Owner**, never an expense. Mixed (e.g. phone, vehicle) → business-use % per the client's
   documented policy; if no policy, exception.
4. **Sales tax collected?** Tax you collected from customers is a **liability** (Sales Tax
   Payable), not income. Sales tax **paid** on a purchase rolls into the asset/expense cost.
5. **Capitalize vs expense?** Tangible property:
   - Cost ≤ **$2,500/item** (or per-invoice) **and** the client has a written de minimis
     policy → expense under the **de minimis safe harbor** (Treas. Reg. §1.263(a)-1(f)).
     Threshold is **$2,500 without an applicable financial statement (AFS)**, **$5,000 with
     an AFS** — SMB bookkeeping clients are almost always non-AFS, so default to $2,500.
     No policy on file → flag to set one; default-expense small items but note it.
   - Over the threshold, or improvement/UOP betterment-adaptation-restoration (BAR test,
     §1.263(a)-3) → **capitalize** to Fixed Assets; set up for depreciation (§168/§179/
     bonus — verify current-year limits). Repairs that merely maintain → expense.
6. **COGS vs operating expense?** Cost directly tied to producing what's sold (materials,
   direct labor, subcontractors on a job, freight-in, merchant fees on a sale) → **COGS**.
   Cost of running the business regardless of sales (rent, office, software, admin) →
   operating expense. Match the client's existing COGS structure exactly.
7. **Contractor vs employee?** Payment for services to a person/SMLLC → ask: is there a
   **W-9** and is this a 1099-NEC contractor or a misclassified worker? Behavioral/financial/
   relationship control (IRS common-law test) leaning employee → **exception** (W-2 +
   payroll-tax exposure). Code to Subcontractors/Contract Labor only with a W-9 on file;
   missing W-9 ≥ $600/yr → exception (1099 filing at risk).
8. **Meals vs travel vs entertainment?** Travel (airfare, lodging, transit) → Travel.
   Business meals → **Meals** (separate account; 50% limit per IRC §274(n) — verify
   current-year %; entertainment is **nondeductible** §274(a) and must be coded separately).
   Keep the deductibility haircut visible to the tax preparer; don't bury it.
9. **None of the above / vendor known?** Apply the precedent map. New vendor with a clear
   description and an obvious account → code with appropriate confidence. Otherwise →
   exception.

## Confidence scoring (per line)
- **High (≥0.90)** — exact precedent match (same vendor→same account) OR unambiguous rule
  (clear transfer, obvious utility). → **auto-code**.
- **Medium (0.60–0.89)** — plausible single account but no precedent, or a clean rule with a
  minor unknown. → auto-code **only if immaterial**; otherwise queue.
- **Low (<0.60)** — multiple plausible accounts, missing W-9, capitalize-vs-expense judgment,
  owner/personal ambiguity, anything **material** (set a per-client materiality $ threshold;
  default flag ≥ $2,500 or any item that moves a tax position). → **EXCEPTIONS QUEUE**.
Always queue: reasonable-comp shortfalls, missing W-9 ≥ $600, possible misclassification,
new account needed, anything that crosses personal/business, and any single item above
materiality regardless of confidence.

## Consistency via client memory
After the partner resolves an exception, **write the rule back** to
`clients/<id>/coding-rules.md` (vendor → account, plus the reason/threshold). Next pass it's
a high-confidence auto-code. This is how the books stay consistent month over month — drift
in coding is the #1 cause of garbage P&Ls. If a vendor's coding *changes*, note why.

## Output (required, every run)
1. **Bottom line** — "Coded 84 of 97 lines; 13 in the exceptions queue; $0 hit P&L from
   transfers; 2 capitalization calls pending."
2. **Auto-coded table** — date | payee | amount | account | confidence | basis (precedent vs
   rule).
3. **EXCEPTIONS QUEUE** — line | amount | the two/three candidate accounts | the specific
   question for the partner | why it matters (tax/material). One decision each, no guessing.
4. **WORKPAPER note** — date, period, basis, count coded, vendor→account rules applied,
   de-minimis policy status, materiality threshold used, and the GL source pulled.

## Approval gate
- **GREEN (autonomous):** reading transactions, building the vendor map, scoring, drafting
  the proposed coding, writing workpapers and the exceptions queue.
- **RED (prepare, then human sign-off):** **posting** the coding into QuickBooks, creating a
  **new GL account**, any reclass of a **material/unusual** item, and anything touching owner
  pay or tax position. Prepare and present; a human authorizes the post.
- **Post path — code in place, don't journal-noise:** apply the category by coding the
  bank-feed/register line to its account in place (the transaction's account field) where the
  MCP supports it — **prefer this** over a fresh `qb_journal_entry_create`, which creates audit-trail
  clutter for routine feed coding. Reserve `qb_journal_*` for genuine **reclasses** of
  already-posted entries. Run **dryRun** first on any mutating tool (`qb_*_add`/`qb_journal_*`).
- Never auto-post a low-confidence or material line. Never fabricate an account, a W-9, or a
  "policy on file." Ambiguous = exception, always.
