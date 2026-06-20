---
name: sales-tax-nexus-determination
description: "Determine where a client has sales-tax NEXUS (the obligation to register and collect) — distinct from preparing/filing returns. Use when a client sells into multiple states, launches e-commerce, uses marketplaces (Amazon/Etsy/Shopify), opens a location, hires remote staff, or asks 'do I have to collect tax in state X?'. Evaluates physical nexus (inventory, employees, agents, FBA stock) and economic nexus (post-Wayfair revenue/transaction thresholds, which vary by state and change yearly — always verified live, never from memory), applies marketplace-facilitator rules, assesses product/service taxability by state, and quantifies back-exposure for periods nexus already existed. Produces a state-by-state nexus matrix, registration recommendations, and a voluntary-disclosure (VDA) assessment. Registering, filing, or signing a VDA requires human sign-off. Feeds sales-tax-prep-filing."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Sales-Tax, Nexus, Multistate, SALT, Compliance, Wayfair]
    related_skills: [sales-tax-prep-filing, month-end-close, financial-statement-prep]
---

# Sales-Tax Nexus Determination

I am RealDeal CPA. This SOP decides WHERE a client must register and collect sales/use tax. It does NOT file returns — that is `sales-tax-prep-filing`, which consumes my output. Determining nexus is analysis (autonomous). Registering, filing, or signing a VDA is a legal commitment (sign-off required).

## When to use
- Client sells into multiple states; launches/scales e-commerce; adds a marketplace (Amazon FBA, Etsy, Walmart, Shopify-with-fulfillment).
- Opens a location, stores inventory in a 3PL/FBA warehouse, hires a remote employee/contractor, attends trade shows, or uses affiliates.
- Client asks "do I owe tax in state X," receives a state nexus questionnaire, or shows up undercollected in diligence.
- Annual refresh: re-run yearly (thresholds change) and any time the client enters a new state, channel, or product line.

Do NOT use this to file returns or compute the period's tax due — that is `sales-tax-prep-filing`. This SOP answers only "where must we be registered and why."

## Authority (verify current-year figures every engagement)
- *South Dakota v. Wayfair*, 138 S. Ct. 2080 (2018) — overturned *Quill*'s physical-presence rule; states may impose economic nexus.
- Each state's economic-nexus statute sets its own threshold. The common pattern is **$100,000 in sales OR 200 transactions** in the current or prior calendar year, but this is NOT universal: some states use AND (e.g., a high-dollar + transaction combo), some use sales-only, and many have **dropped the 200-transaction prong entirely**. Thresholds, measurement periods (prior vs. current year, gross vs. retail vs. taxable sales), and effective dates change yearly.
- **NEVER quote a threshold from memory.** For every state in scope, run `web_search`/`browser` against the state DOR or a maintained chart and record the figure + source + retrieval date. Write "verify current-year" anywhere a number would otherwise be hardcoded.
- Marketplace-facilitator laws: the marketplace generally collects on sales made *through* it, but the seller (a) may still cross thresholds on **direct/off-marketplace** sales, and (b) may have **physical nexus from marketplace-owned inventory** stored in-state (FBA). Verify per state.

## Procedure

1. **Open + scope.** `qb_session_status` and `qb_company_info` FIRST to confirm the right entity/file. Confirm the entity's legal name, FEIN, and home state.

2. **Build the activity profile (physical nexus).** Inventory the facts that create physical presence in each state: owned/leased property, employees, resident or traveling contractors/agents, inventory (including 3PL and FBA warehouse locations — pull the marketplace's inventory-placement report), trade-show/solicitation activity, drop-ship relationships, affiliate/click-through arrangements. Physical presence = nexus from day one of that activity, regardless of dollars.

3. **Quantify sales by state and channel (economic nexus).** Pull revenue by ship-to state and by channel (direct vs. each marketplace):
   - `qb_pnl_report` and `qb_general_ledger` for total revenue and the GL trail.
   - `qb_sales_tax_liability_report` for tax already collected/remitted by jurisdiction (reveals where collection is already happening — and where it is NOT).
   - `qb_invoice_list` / `qb_item_list` to reconstruct ship-to detail when QB's class/location tagging is thin. Reconcile QB totals to the marketplace and shopping-cart settlement reports — QB often understates gross because facilitator-collected sales net out.
   - Cross-check totals against vr-ledger `income_statement` if a parallel ledger exists.

4. **Apply thresholds per state.** For each state with any direct sales or physical contact: retrieve the current-year threshold (step in Authority), then compare the correct measure (most states = gross/retail sales for the prior OR current year) against the verified number. Flag: OVER (nexus established), APPROACHING (>=80% — monitor), or NONE. Note the **trigger date** — the date the threshold was crossed — because that date starts the collection obligation and the back-exposure clock.

5. **Apply marketplace-facilitator carve-outs.** For each state, subtract facilitator-collected sales where the state excludes them from the seller's threshold (varies), but KEEP physical nexus from in-state marketplace inventory. A seller can have ZERO economic-threshold sales yet still have physical nexus (and a filing obligation) because Amazon stored goods in that state's warehouse.

6. **Determine taxability.** Nexus only matters for taxable sales. Classify the client's products/services per state: tangible goods (usually taxable), SaaS/digital goods (taxable in some states, exempt in others — verify), professional/personal services (often exempt), groceries/clothing (state-specific exemptions), resale/exempt-entity sales (need a valid exemption certificate on file). A state where everything sold is exempt may create a registration-only (zero-tax) obligation or none — note which.

7. **Assess back-exposure + remediation.** Where nexus existed in PRIOR periods with no collection: estimate uncollected tax from the trigger date forward (tax base x verified rate per period — "verify current-year rate"), plus penalty and interest exposure ("verify current-year P&I"). Compare two paths and recommend one:
   - **Prospective registration** (register now, collect going forward) — appropriate when exposure is small/recent.
   - **Voluntary Disclosure Agreement (VDA)** — limits the lookback (commonly 3-4 years, state-specific) and typically abates penalties; available only BEFORE the state contacts the client. Some states run time-limited VDA windows — verify availability and deadlines per state before recommending.

8. **Make the registration decision per state.** For each OVER state, recommend: register prospectively, register + VDA, or register + amnesty. For each APPROACHING state, set a monitor trigger (re-check when sales reach ~90% of the verified threshold) and a registration deadline — most states require registration within 30-60 days of crossing (verify the grace window per state). Never recommend registering in a NONE state "to be safe": a permit creates an affirmative filing obligation (zero returns due every period, with late-file penalties) and starts trailing nexus.

9. **Document for re-run.** Capture the as-of date, every QB report pulled (with dates), every marketplace settlement/inventory report, and each verified threshold/rate with its source URL and retrieval date into the workpaper. Thresholds drift yearly; next year's determination re-runs this same SOP against fresh figures and diffs the matrix — so the inputs must be reproducible.

## Edge cases a 15-year CPA flags
- **FBA / 3PL inventory** silently creates physical nexus in fulfillment-center states; the client almost never knows where their stock sits — get the placement report.
- **Trailing nexus**: many states keep an obligation alive for a period after activity stops. Don't deregister the day sales drop.
- **Wholesale/resale-heavy sellers**: high gross may cross the threshold even if every sale is exempt — registration can still be required to file zero/exemption-supported returns.
- **Home-rule jurisdictions** (CO, LA, AL, AK locals) administer tax locally; state-level nexus analysis does NOT cover them — call them out separately.
- **Measurement-period traps**: prior-year vs. current-year, calendar vs. rolling 12-month, gross vs. taxable. Using the wrong measure mis-dates the trigger.
- **Marketplace ≠ safe harbor for direct sales**: a Shopify store running alongside Amazon is the seller's own direct channel and counts toward the threshold.
- **SaaS/digital taxability** is the most error-prone classification — verify each state, don't assume.

## Required output
1. **Bottom-line summary** — one paragraph: which states have nexus today, which are approaching, total estimated back-exposure (range), and the single most urgent action.
2. **NEXUS MATRIX** — one row per state in scope: `State | Physical nexus (Y/N + basis) | Direct sales $ | Txns | Threshold (verified + source + date) | Status (OVER/APPROACHING/NONE) | Trigger date | Taxable? | Marketplace-collected? | Recommended action`.
3. **EXCEPTIONS QUEUE** — anything I could not resolve autonomously: states where the threshold/rate couldn't be verified live, missing ship-to data, ambiguous SaaS/service taxability, home-rule locals, unconfirmed FBA locations, suspected pre-Wayfair or unfiled prior periods. Each item: what's missing, why it matters, what I need.
4. **WORKPAPER note** — record data sources (QB reports + dates, marketplace settlement/inventory reports, each verified threshold with its URL and retrieval date), methodology, assumptions, and conclusions, so the determination is defensible on audit and re-runnable next year.

## Approval gate
Preparing the matrix, quantifying exposure, and recommending registration/VDA are **autonomous**. The following are **PREPARE then REQUIRE human sign-off** — I draft the package and stop:
- **Registering** for a sales-tax permit in any state.
- **Signing or submitting a VDA** (binding lookback/disclosure commitment).
- **Filing any return** or remitting tax (that is `sales-tax-prep-filing`).
- Posting any **material** sales/use-tax **accrual or liability JE** for back-exposure.

When an approved exposure accrual is to be booked, I PREPARE the JE (run mutating QB tools with `dryRun` first): **Dr** Sales/Use Tax Expense (or prior-period adjustment per materiality) / **Cr** Sales Tax Payable, via `qb_journal_entry_create`, posted only after sign-off. I do not register, file, or remit without a human approving the specific state and amount.
