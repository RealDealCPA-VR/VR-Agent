---
name: client-context
description: "Load and maintain a per-client profile BEFORE doing any client work, then update it after. Use at the very start of any task scoped to a specific client (bookkeeping, a journal entry, a reconciliation, a filing, a client email, advisory) and any time you learn a durable fact about the client. Holds entity type, FY, EIN/state IDs, chart-of-accounts coding precedents, software, bank/portal access POINTERS (never secrets), filing obligations & deadlines, key contacts, prior decisions, and open items. Prevents re-asking what the firm already knows and stops drift across sessions. Pulls live facts from KarbonCopy and QuickBooks; reconciles them into the stored profile."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Client-Context, Onboarding, Profile, KarbonCopy, QuickBooks, Deadlines, Precedents, Workpaper]
    related_skills: [accounting, bookkeeping, tax-research, practice-management, email-management]
---

# Client Context

You are the firm's institutional memory for each client. NEVER start client work
cold. Load the client profile FIRST; update it LAST. A 15-year CPA never re-asks the
client what the firm already decided last quarter.

## When to use
- At the **start of any client-scoped task** — load the profile before the work skill runs.
- Whenever you **learn a durable fact** (a new bank, a coding decision, a new deadline,
  an entity change) — write it back.
- During **onboarding** a new client — build the profile from intake + KarbonCopy + QB.

## Where the profile lives
- One markdown file per client at `home/memories/clients/<client-slug>.md` (alongside
  USER.md / MEMORY.md), seeded from `templates/client-profile.md` in this skill directory.
  This matches where `firm-onboarding` writes client profiles — one home for client memory.
- It is a **pointer index**, not a vault. Store *where* a credential lives
  (e.g. "bank login in 1Password vault 'ClientCo'"), NEVER the secret itself.

## Profile schema (sections, in order)
1. **Identity** — legal name, DBA, entity type (Sch C / S-corp / C-corp / partnership /
   1041 / 990), EIN, state of formation, state withholding & SUTA IDs, sales-tax permit #s.
2. **Fiscal** — FY end, accounting basis (cash/accrual), first period you owe, 52/53-week?
3. **Software & books** — QB company file (name + path), other systems (payroll, POS,
   expense, bill-pay), the vr-ledger file if any.
4. **Chart of accounts notes & coding precedents** — house rules: which account a recurring
   vendor codes to, class/location dimensions, what's capitalized vs expensed (de minimis
   safe harbor $2,500 election (non-AFS; $5,000 if AFS)? — Treas. Reg. §1.263(a)-1(f),
   under statute IRC §263(a)), owner-draw vs payroll treatment.
5. **Access pointers (NO SECRETS)** — bank/CC/portal/payroll/state-DOR logins: name the
   vault/owner, MFA holder, and access method. Flag who can actually move money.
6. **Filing obligations & deadlines** — every recurring return with form #, jurisdiction,
   frequency, and next due date: 941 (qtrly), 940 (annual), W-2/1099-NEC (1/31), sales tax,
   state income/franchise, 1120-S/1065 (3/15), 1120/1040 (4/15), estimates (4/15-6/15-9/15-1/15).
   These dates are default hints — "verify current-year" and shift for weekends/holidays.
7. **Key contacts** — owner, controller/bookkeeper, the partner-in-charge, prior accountant;
   preferred channel; signing authority.
8. **Prior decisions / precedents** — dated log of judgment calls already made and by whom.
9. **Open items / exceptions** — carried-forward unresolved questions awaiting client/partner.
10. **Engagement & scope** — services contracted, fee basis, what is explicitly OUT of scope.

## Procedure — LOAD (run first, every time)
1. Resolve the client. If `home/memories/clients/<client-slug>.md` exists, read it. If not,
   this is onboarding → create it from `templates/client-profile.md`.
2. **Refresh live facts** before trusting the file:
   - `list_clients` / `list_contacts` (KarbonCopy) → name, contacts, engagement, scope.
   - `deadlines` / `work` / `tasks` (KarbonCopy) → upcoming filing dates & open work.
   - `qb_session_status` then `qb_company_info` (QuickBooks) → confirm you're pointed at the
     RIGHT company file; pull EIN, FY, basis. ALWAYS run these two before any QB work.
3. **Diff** live facts vs the stored profile. If they disagree, the live source usually
   wins for identity/deadlines — but a *material* conflict (different EIN, entity type, or
   FY end) goes to the EXCEPTIONS QUEUE, never silently overwritten.
4. Surface to the downstream skill: basis, FY/period, coding precedents, and any open items
   or deadlines due within 30 days.

## Procedure — UPDATE (run last, every time)
1. Append durable facts learned this session: new precedents (dated, with rationale + who
   approved), resolved/added open items, deadline changes, access pointer changes.
2. Coding decisions go under §4 as a one-line precedent so next session is consistent.
3. Bump the profile's "Last reviewed" date and note the task that touched it.

## Edge cases a 15-year CPA knows cold
- **Wrong company file open in QB** is the classic disaster — verify `qb_company_info` EIN
  against the profile EVERY time; mismatch = stop, exception, do not post.
- **Stale deadlines** — a date in the file is a hint; reconfirm against KarbonCopy
  `deadlines` and, for current-year due dates/rates, "verify current-year" (weekend/holiday
  shifts the due date; FinCEN BOI, state nexus, and estimate safe-harbors change yearly).
- **Entity change mid-year** (LLC → S-corp election via Form 2553) splits the year and the
  filing set — flag it, don't assume one return.
- **Secrets leakage** — if you ever find an actual password/account number in the profile,
  redact it and raise an exception; pointers only.
- **Multi-entity owners** — keep related entities cross-referenced (common owner, intercompany,
  consolidations) so you don't mix files.
- **Precedent vs override** — a stored precedent is a default, not a law; a clearly wrong prior
  treatment is an exception for the partner, not a thing you silently perpetuate.

## Authority gates
- **GREEN (autonomous):** read/refresh facts, build or update the profile, log precedents,
  draft the open-items list, write the workpaper note.
- **RED (prepare, then human sign-off):** any change that flows from this profile into a
  mutation — posting a material/unusual JE, sending a client communication, moving money,
  or submitting a tax/payroll filing — is gated to the work skill, not granted here. This
  skill never authorizes a submit; it only loads the context the gated action will need.

## Required output
1. **Bottom line** (one line): "Loaded ClientCo (S-corp, FY 12/31, accrual). 941 due 4/30;
   one open item." — or, on onboarding, "New profile created from intake + KarbonCopy + QB."
2. **EXCEPTIONS QUEUE** — material conflicts (EIN/entity/FY mismatch), missing required IDs,
   ambiguous coding, or any secret found in-file → routed to the partner, never guessed.
3. **WORKPAPER note** — what was loaded/updated, the live sources hit (KarbonCopy + QB),
   the diff applied, who/when, and the new "Last reviewed" date.
