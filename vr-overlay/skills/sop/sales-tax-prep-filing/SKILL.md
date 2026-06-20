---
name: sales-tax-prep-filing
description: "Prepare and file state/local sales & use tax returns. Use at filing time (monthly/quarterly/annual) or when asked to compute sales-tax liability, reconcile sales-tax-payable, or check nexus. Determines nexus and taxable sales by jurisdiction, validates exemption/resale certificates, splits gross vs taxable vs exempt, computes liability at current-year rates, reconciles to the GL sales-tax-payable, prepares the return, and pre-fills the state DOR portal via browser. Drives QuickBooks MCP (the QB report tools, qb_account_*, qb_invoice_*), vr-ledger, web_search for current rates/rules, and the browser tools for the DOR portal. GREEN through prepare + pre-fill; SUBMIT is RED — requires human review and authorization. Leaves a filing log + workpaper."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Sales-Tax, Use-Tax, Nexus, Exemption-Certificate, State-DOR, Compliance, Filing, QuickBooks]
    related_skills: [accounting, tax-research, practice-management]
---

# Sales & Use Tax — Prepare & File

You prepare jurisdiction-correct sales/use tax returns to a workpaper standard, then pre-fill
the state DOR portal and stop at the submit gate for a human to authorize. State-by-state law
varies wildly — rates, brackets, filing frequency, sourcing (origin vs destination), and what's
taxable all differ. **Verify current-year rates and rules; never assume last period's are still good.**

## When to use
- A sales/use tax return is due (monthly / quarterly / annual — frequency is state-assigned).
- Asked to compute liability, reconcile sales-tax-payable, validate exemption certs, or assess nexus.
- A new state/marketplace is added, or sales volume crossed a likely economic-nexus threshold.

## Tools you drive
- **QuickBooks MCP** — `qb_session_status` + `qb_company_info` FIRST. Then the QB report tools
  (Sales by Customer/Item, P&L for gross sales, General Ledger for the sales-tax-payable account),
  `qb_account_*` (locate the sales-tax-payable liability account + balance), `qb_invoice_*`
  (drill taxable vs non-taxable line detail, ship-to for destination sourcing).
- **vr-ledger MCP** — `balances` / `income_statement` for ledger-kept books or cross-check.
- **web_search** — confirm current-year state/local rates, economic-nexus thresholds, filing
  frequency, due dates, and prepayment rules. Cite the DOR page/date.
- **browser tools** — `browser_navigate/snapshot/type/click/console` to log into the state DOR
  portal and pre-fill the return. **Pre-fill only — do not click final Submit/File.**
- **KarbonCopy MCP** — `deadlines` / `tasks` to log the filing and set the next period's due date.

## Procedure

1. **Scope & nexus.** List jurisdictions with potential filing duty. Physical nexus (office,
   inventory, employees, FBA stock) and **economic nexus** (post-*Wayfair*, typically a
   $100k sales OR 200-transaction threshold — but state-specific; CA/NY/TX differ — verify
   current-year). Marketplace-facilitator states may already collect/remit for marketplace
   sales — exclude those from the return but reconcile them. **A return can only be filed into a
   jurisdiction where the client holds a sales-tax registration/permit (account number).** A state
   with nexus but no registration cannot be filed into — registration comes first. Unregistered-but-nexus
   = **EXCEPTION** (route to partner; do not attempt to file or pre-fill until a permit number exists).
   Confirm the active permit/account number for every jurisdiction you intend to file before step 8.

2. **Pull gross sales.** the QB report tools Sales by Customer/Item + P&L for the period. Tie total
   revenue to the GL. Record the period, basis (most sales tax is **accrual/invoice-date**, but
   some states allow cash — verify the registration), and sourcing rule (destination vs origin).

3. **Segment gross → taxable → exempt.** For each jurisdiction:
   - **Gross sales** (all sales sourced there).
   - **Exempt/deductible**: resale, exempt entities (gov/nonprofit), exempt products (often
     unprepared food, Rx, mfg inputs), services if not taxable, freight where excluded — **each
     exemption must be backed by a valid certificate on file** (resale/exemption cert with cert #
     and date). Missing/expired cert ⇒ treat as **taxable** and flag as EXCEPTION; do not waive tax
     on an undocumented claim — that's the auditor's first pull.
   - **Taxable sales** = Gross − Exempt. Apply the correct **combined state + county + local/district
     rate** at the ship-to address (destination states). Don't use a single statewide rate when
     district taxes apply (CA, TX, WA, etc.).

4. **Use tax (self-assessed).** Review purchases where vendor charged no sales tax but the item is
   taxable for own use (out-of-state/online buys, inventory withdrawn for use). Add consumer use
   tax to the same return where the state requires it.

5. **Compute liability.** Taxable × rate per jurisdiction = tax due. Apply **vendor/timely-filing
   discount** if the state offers one. Net any prepayments/credits. Sum to total remittance. Note: the
   discount reduces cash paid but **not** the collected liability — it lands in the GL as the plug
   (credit to other income, or a sales-tax-expense offset) so the remittance JE in step 10 still ties.

6. **Reconcile to GL.** Compare computed tax collected to the **sales-tax-payable** account balance
   (`qb_account_*` / GL via the QB report tools). They should tie. A difference means: under/over-collection,
   rounding, a rate change mid-period, mis-coded taxable flags, or a posting error. Reconcile to the
   penny; book a small rounding adjustment, but route any **material** variance to the EXCEPTIONS QUEUE
   — do not file over an unexplained gap.

7. **Prepare the return.** Build the workpaper schedule (jurisdiction → gross / exempt / taxable /
   rate / tax). Map each figure to the exact line of that state's return form.

8. **Pre-fill the DOR portal (GREEN).** Requires a confirmed registration/permit number (step 1).
   `browser_navigate` to the state DOR and log in under the client's registered account. **Login is
   itself a sensitive boundary:** use only firm-provisioned stored credentials for the matching
   account; **never store, cache, or auto-enter an MFA/OTP code** — if an MFA challenge prompts, hand
   off to the authorized human and do not bypass it. Once in, enter the figures line-by-line and
   `browser_snapshot` each screen. **Stop at the review/confirm page. Do NOT click Submit/File/Pay.**

9. **Approval gate (RED).** Present: total tax due by jurisdiction, the reconciliation result, any
   exceptions, the prepared portal state (screenshot), and the payment amount/method. A human must
   review and authorize the **submit + payment**. Only after explicit sign-off may a human (not you)
   file. Moving money / submitting a filing is RED.

10. **Post-file.** Capture the confirmation number, log it, and book the remittance JE: Dr
    sales-tax-payable (full collected liability) / Cr cash (amount actually paid) / Cr other income
    (the vendor/timely-filing discount taken in step 5), so the entry balances. Posting the JE is
    itself RED if material; otherwise draft it for review. Set the next period's deadline in
    KarbonCopy (`deadlines`).

## Edge cases a 15-year CPA knows cold
- **Zero/negative liability still requires a return** in most states — file a zero return; skipping it
  triggers a non-filer notice.
- **Filing frequency is state-assigned** and changes with volume; a state can move you monthly without
  obvious notice. Confirm frequency and due date (many are the 20th; some 15th/last day) — verify.
- **Destination vs origin sourcing**: intra-state may be origin while interstate is destination — don't
  mix them. SaaS/digital goods taxability varies hugely by state.
- **Marketplace facilitator** sales: included in gross but deducted as already-collected — don't
  double-remit, but don't omit from gross either, or the return won't reconcile.
- **Resale certs expire / blanket certs** must match the customer and be current; an exemption with no
  cert is the #1 audit assessment.
- **Rounding & district rates**: never use a single statewide rate where local/district taxes stack.
- **Prepayments**: large filers owe estimated prepayments mid-period (CA, others) — credit them.
- **Bracket/tax-table states** compute tax per-transaction, not as a flat % of the total — watch this.

## Required output
- **Bottom line first** — e.g. "Q2 sales tax: $14,238.52 due across CA + 3 districts; ties to GL
  payable within $0.18 rounding; 1 exception (expired resale cert, $1,920 sale)."
- **Liability table** — jurisdiction | gross | exempt | taxable | rate | tax due.
- **Reconciliation** — computed collected vs GL sales-tax-payable, with the variance explained.
- **EXCEPTIONS QUEUE** — missing/expired certs, nexus-without-registration, unexplained material
  variances, ambiguous taxability. Each goes to the partner; never guessed.
- **Filing log** — period, jurisdiction, return form, amount, due date, status (prepared / pre-filled /
  submitted), confirmation #, who authorized.
- **WORKPAPER note** — period, basis, sourcing rule, rate source (DOR page + date verified), reconciling
  difference, and the resulting payable balance.

## Guardrails
GREEN through step 8 (read, compute, reconcile, draft, pre-fill). **RED**: clicking Submit/File,
making the payment, or posting a material remittance JE — prepare it, then require human sign-off.
Never file over an unexplained material variance, never waive tax on an undocumented exemption, and
never fabricate a rate or threshold — if unsure, write "verify current-year" and route to the partner.
