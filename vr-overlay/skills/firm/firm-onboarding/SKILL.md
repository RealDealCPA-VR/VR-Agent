---
name: firm-onboarding
description: "Your FIRST DAY at a new firm. Run a structured onboarding interview to learn THIS firm — services, software stack, client roster and each client's obligations, partner preferences/conventions, account-coding and naming conventions, approval thresholds/materiality, deadlines, and communication norms — then WRITE all of it into durable memory (home/memories USER.md and MEMORY.md) plus per-client profiles. Use this BEFORE doing any client work at a firm you have not been configured for, or whenever the partner says 'set you up', 'onboard', 'learn how we do things', or 'here's how the firm works'. Re-run sections to update conventions as they change."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Onboarding, Firm-Setup, Interview, Memory, Conventions, Client-Profiles, Materiality, Practice-Mgmt]
    related_skills: [client-context, new-client-onboarding, accounting, bookkeeping, practice-management, tax-research, email-management]
---

# Firm Onboarding

It's your first day. You're a senior CPA — competent, but NEW here. Before touching a
client's books you learn how THIS firm operates and commit it to memory. You do not assume
the last firm's conventions carry over. You ask, you confirm, you write it down.

## When to use
- First configuration at a firm, or any time the partner wants to (re)set your conventions.
- Adding a new client → run only the **Per-Client** section for that client.
- A convention changed (new threshold, new software, partner left) → re-run that section and
  rewrite the affected memory.

**Scope vs. sibling skills:** this sets up the **FIRM** (conventions, stack, thresholds,
roster). For a single client, `firm/client-context` (load/recall one client's profile) and
`sop/new-client-onboarding` (run the engagement-setup workflow for one new client) are the
right skills — don't use firm-onboarding to drive one-client work beyond seeding its profile.

## How the interview runs
- Conversational, grouped by topic, one topic at a time. Don't dump all questions at once.
- Echo back what you heard before writing it. **Never guess a firm convention** — if the
  partner is unsure or it's material, park it in the EXCEPTIONS QUEUE, don't invent a default.
- Capture verbatim where wording matters (engagement scope, sign-off language).
- Where you can verify yourself, do — `list_clients`/`list_work`/`list_deadlines` (KarbonCopy),
  `qb_company_list`/`qb_company_info` (QuickBooks) — then confirm with the partner rather than
  asking them to recite what the systems already know.

## Interview question set (ask, grouped)

**1. The firm & people**
- Legal/DBA name, EIN, office locations, time zone, fiscal year-end.
- Partners/principals and who is MY review partner (who signs off on RED items)?
- Staff I'll interact with, and who owns client relationships?
- PTIN/EFIN on file; firm's Circular 230 / state-board posture (anything I must never do)?

**2. Services offered**
- Which lines: bookkeeping, write-up, payroll, AP/AR, sales/use tax, income tax (1040/1120/
  1120-S/1065/1041/990), advisory/CAS, audit/attest, fractional CFO?
- Engagement types per client and what's explicitly OUT of scope (so I don't overreach)?

**3. Software stack**
- Accounting: QuickBooks Desktop vs Online (which company files?), or vr-ledger, or other?
- Tax prep software, payroll provider, document/portal, practice mgmt (KarbonCopy?),
  e-sign, bill-pay/payments rail, bank-feed tool.
- Where source docs live (drive/SharePoint/portal path) and naming of those folders.
- Credentials/SSO posture — what I'm authorized to log into vs. what needs a human.

**4. Client roster & per-client obligations** (loop per client — see Per-Client below)
- Pull the roster first via KarbonCopy `list_clients`; confirm additions/inactives.

**5. Chart-of-accounts, coding & naming conventions**
- Standard CoA template or per-client? Account-numbering scheme?
- Class/location/department tracking, job costing — used? how?
- Vendor/customer naming convention (e.g. "LASTNAME, First" vs "Company LLC"), memo style.
- Default coding rules for common items (merchant fees, owner draws, meals 50%, reimbursements).
- Capitalization policy & de minimis safe harbor per Treas. Reg. §1.263(a)-1(f): $2,500/item
  for a taxpayer WITHOUT an applicable financial statement, $5,000/item WITH an AFS — ask which
  tier each client falls under and confirm the firm's elected amount; verify current-year.

**6. Approval thresholds & materiality**
- Dollar threshold above which ANY journal entry needs partner sign-off?
- Materiality basis for review (e.g., % of revenue/assets, or a flat $)?
- Unusual/round-dollar/related-party entries — always escalate regardless of size?
- Payment/disbursement cap I may prepare vs. what a human must release?
- Auto-categorize confidence floor before something goes to the EXCEPTIONS QUEUE.

**7. Deadlines & cadence**
- Recurring client deadlines: payroll (941 quarterly, 940 annual, state), sales tax filing
  frequency, 1099-NEC/W-2 (Jan 31), income-tax due dates & extensions, month-end close day.
- Confirm against KarbonCopy `list_deadlines`/`list_work`; note who files vs. who reviews.
- Lead time the partner wants before each deadline; preferred close calendar.

**8. Communication norms**
- Client-facing channel (email/portal) and tone; may I email clients directly or DRAFT only?
- Internal channel for questions, and how to flag something urgent.
- Sign-off block / firm signature, disclaimer language, BCC/file-copy rules.
- Reporting format the partner likes (bottom-line-first, tables, PDF vs. workbook).

## Per-Client profile (loop for each client)
For each client capture: legal name + EIN; entity type & tax form; FYE & accounting basis
(cash/accrual); software file/company ID; services in scope; bank/CC accounts & feeds;
recurring obligations + filing frequencies (payroll/sales tax/1099); key contacts & who may
approve; client-specific coding quirks; materiality if different from firm default; portal
path; open items. Pull what you can from `qb_company_info` and KarbonCopy `list_contacts`/
`list_work`, then confirm.

## Write it to memory (this is the deliverable)
After each topic is confirmed, persist it — onboarding is worthless if it evaporates:
- **`home/memories/USER.md`** — the partner/firm identity, my review partner, communication
  norms, sign-off block, authorization posture (what I may do vs. RED items).
- **`home/memories/MEMORY.md`** — firm-wide conventions: software stack, CoA/coding/naming
  rules, approval thresholds & materiality, de minimis amount, deadline cadence, default
  playbook choices.
- **`home/memories/clients/<client-slug>.md`** — one profile per client (the fields above).
  This `clients/` subdirectory does not exist yet — **create it** (`mkdir -p`) before the first
  client write so the file lands where the agent expects, not in a stray path.

**File format — match what these files actually use.** USER.md and MEMORY.md are NOT keyed;
they are a single running document of short prose facts separated by a lone `§` on its own
line. So don't "update a key" — instead **read the file first, then patch in place**: if a fact
already exists, edit that `§`-block; if it's genuinely new, append one new `§`-delimited block.
Keep each block one tight fact, same voice as the existing blocks. Never append a duplicate
block for a fact already present (that's the failure mode the no-keys format invites). Per-client
profiles under `clients/` are fresh files you author, so a clean keyed/sectioned layout is fine
there. Write atomically; after writing, read it back and show the partner a short confirmation
of what's now in memory.

## Pitfalls a 15-year CPA knows cold
- Don't import the prior firm's thresholds or CoA — each firm differs; confirm every number.
- "We've always done it that way" is not a coded rule until it's in MEMORY.md — write it down.
- Wardrobe of defaults (meals %, owner draws, merchant fees) causes silent miscodings later if
  guessed — get the firm's actual rule or queue it.
- EFIN/PTIN and e-file authorization are firm-specific and legally gated — never assume I can
  submit a filing; that's always RED.
- Inactive/duplicate clients in the roster — reconcile KarbonCopy vs. QB company files.

## Output (every onboarding session)
1. **Bottom line** — what was set up today (e.g., "Firm + 12 clients onboarded; 3 conventions
   pending partner").
2. **Conventions table** — topic → value now in memory.
3. **EXCEPTIONS QUEUE** — every unanswered/ambiguous/material item, for the partner.
4. **WORKPAPER note** — date, what was captured, which memory files written, version.

## Approval gate
Reading systems, drafting the profile, and **writing to memory** are GREEN (autonomous).
Anything that ACTS on a client — posting entries, sending client comms, moving money, or
submitting a filing — is RED and out of scope here; that lives in the task skills and requires
my review partner's sign-off. Onboarding only learns and records; it never executes.
