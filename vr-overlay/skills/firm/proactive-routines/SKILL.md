---
name: proactive-routines
description: "The recurring cadence the firm employee OWNS and runs UNPROMPTED, as concrete scheduled cron jobs. Use to install, audit, or run the standing routines: a daily AM email-triage + deadline/at-risk standup; a weekly AP/AR aging + cash position + upcoming-filings digest; a monthly close kickoff; and quarterly estimated-tax (Form 1040-ES) and payroll-tax (941/940) reminders. Gives the exact `hermes cron add` commands, the SAFE read-only toolset for unattended runs, and the delivery channel for each. Unattended runs are GREEN-only: they read, analyze, draft, and deliver a digest — they NEVER post JEs, send client email, move money, or submit a filing. Anything material lands in the EXCEPTIONS QUEUE for the partner. Use when the partner says 'set up your routines', 'what do you do on your own', 'daily standup', 'weekly digest', or to review/repair the cron schedule."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Proactive, Cron, Routines, Cadence, Standup, Digest, Deadlines, Close, Estimated-Tax, Payroll-Tax]
    related_skills: [client-context, email-management, practice-management, accounting, month-end-close]
---

# Proactive Routines

You don't wait to be asked. A senior CPA who's been doing this 15 years runs a standing
cadence: the inbox is triaged before the partner is awake, aging is chased before it's
collection, filings are flagged weeks early, and close starts on day one of the month. This
skill defines that cadence as **scheduled cron jobs** and the **safe toolset** they run with.

## The cadence you own
| Routine | When (local) | Delivers | Purpose |
|---|---|---|---|
| **Daily standup** | Mon-Fri 07:00 | Email to partner | Inbox triage + today's deadlines + at-risk work |
| **Weekly digest** | Mon 07:30 | Email to partner | AP/AR aging + cash position + filings due in 14 days |
| **Monthly close kickoff** | 1st of month 07:00 | Email + KarbonCopy tasks | Open prior-month close, build the checklist |
| **Quarterly tax reminders** | Estimates & payroll-tax due cycle | Email to partner | 1040-ES estimates + 941/940 prep heads-up |

## SAFE toolset for unattended runs (GREEN only)
Unattended = no human watching, so every cron run is **strictly read/draft/deliver**. The
prompt for each job MUST constrain the agent to these:
- **Reads:** `qb_session_status`, `qb_company_info`, the QB report tools (P&L, Balance Sheet, AR/AP
  Aging, Trial Balance), `qb_account_*`/`qb_*_list` queries; KarbonCopy `list_clients`,
  `list_deadlines`, `list_work`, `list_tasks`, `list_time`, `list_invoices`, `list_payments`;
  vr-ledger `balances`,
  `income_statement`, `balance_sheet`, `cash_flow_statement`; the Email gateway in
  **read-only** + **draft** mode; `client-context` LOAD.
- **Produces:** a digest email (drafted/sent to the partner only — internal, not the client),
  KarbonCopy tasks/work items, and a workpaper note.
- **HARD STOP — never in a cron run:** posting any journal entry, voiding/editing a
  transaction, sending a CLIENT communication, moving money/cutting a payment, or SUBMITTING
  any tax/payroll filing. Those are RED — the routine surfaces them to the EXCEPTIONS QUEUE
  and the partner authorizes them in an attended session. Set any mutating tool to
  `dryRun: true` defensively even though the prompt forbids the call.

## Install the routines (exact commands)
Run these once to register the cadence. **CLI shape:** `hermes cron add <schedule> "<prompt>"`
— **schedule and prompt are POSITIONAL** (the schedule is a 5-field cron string OR a natural
form like `30m` / `every 2h`). The human name is `--name`; attach playbooks by **repeating
`--skill <name>`** (there is no `--skills` comma list); delivery is a **single**
`--deliver <platform>` or `--deliver <platform:chat_id>`. There is **no `--tz` flag** — cron
runs in the engine's single configured timezone (set it once in the engine config, not per job).
`--deliver email` routes to `EMAIL_HOME_ADDRESS` (the partner's configured inbox); use
`--deliver email:partner@firm.com` to pin a specific address.

```bash
# 1) DAILY AM STANDUP — Mon-Fri ~07:07 (off-round on purpose; see Timing)
hermes cron add "7 7 * * 1-5" \
  "Read-only morning standup. (1) Triage the inbox into Now/Reply/Delegate/FYI; \
draft replies for the partner to review — DO NOT SEND. (2) Pull KarbonCopy deadlines+work; \
list everything due today/overdue and any at-risk (blocked, no time logged, slipping). \
(3) qb_session_status+qb_company_info sanity check only. Output: one-screen bottom-line, \
top fires, drafted replies ready, and an EXCEPTIONS QUEUE. No mutations, no sends." \
  --name daily-standup --deliver email \
  --skill email-management --skill client-context --skill practice-management

# 2) WEEKLY DIGEST — Monday ~07:32
hermes cron add "32 7 * * 1" \
  "Read-only weekly digest, per active client. (1) the QB report tools AR Aging + AP Aging: \
flag >60/>90 day buckets, top overdue customers, bills coming due. (2) Cash position from \
Balance Sheet / vr-ledger cash_flow_statement; note runway concerns. (3) KarbonCopy \
deadlines: every filing/return DUE WITHIN 14 DAYS (941/940/sales tax/income), with form# \
and date. Output: bottom-line per client, aging tables, cash line, a FILINGS-DUE-SOON list, \
and an EXCEPTIONS QUEUE. No JEs, no payments, no sends." \
  --name weekly-digest --deliver email \
  --skill accounting --skill practice-management --skill client-context

# 3) MONTHLY CLOSE KICKOFF — 1st of month ~07:08
#    Digest goes to the partner via email; KarbonCopy tasks are CREATED inside the run
#    by the KarbonCopy MCP (per the prompt), NOT via --deliver.
hermes cron add "8 7 1 * *" \
  "Open the prior-month close for each active client. Build the close checklist: \
bank/CC recons, accruals, prepaids amortization, depreciation, payroll clearing, \
intercompany, suspense cleanup. Pull last-month P&L and B/S; flag anomalies vs prior period \
and any unreconciled/suspense balances. CREATE KarbonCopy tasks for each checklist line via \
the KarbonCopy MCP (allowed — internal work items). PREPARE recurring/standard JEs as DRAFTS \
only — do NOT post. Output: per-client close kickoff, checklist status, draft entries pending \
sign-off, EXCEPTIONS QUEUE." \
  --name monthly-close-kickoff --deliver email \
  --skill month-end-close --skill accounting --skill practice-management

# 4) QUARTERLY ESTIMATED-TAX REMINDER — ~3 weeks before each due date
hermes cron add "0 8 25 3,5,8,12 *" \
  "Estimated-tax (Form 1040-ES; corporate estimates computed on the current-year corporate \
estimated-tax worksheet (formerly Form 1120-W, discontinued after 2022 — verify the current \
vehicle)) heads-up for the upcoming due date \
(4/15, 6/15, 9/15, 1/15 — verify current-year; weekend/holiday shifts it). For each client \
with estimate obligations: pull YTD income (P&L), compute a safe-harbor target \
(prior-year 100%/110% or 90% current — verify current-year %s), and DRAFT the voucher \
figures. Do NOT submit or pay. Output: per-client estimate worksheet, safe-harbor basis, \
amount + due date, EXCEPTIONS QUEUE for anyone under-paid." \
  --name quarterly-estimates --deliver email \
  --skill tax-research --skill client-context --skill accounting

# 5) QUARTERLY PAYROLL-TAX REMINDER — ~2 weeks before 941/940 quarter-end filing
hermes cron add "0 8 15 1,4,7,10 *" \
  "Payroll-tax filing heads-up. Quarterly Form 941 is due the last day of the month \
following quarter-end (4/30, 7/31, 10/31, 1/31); annual Form 940 + W-2/1099-NEC due 1/31 \
(verify current-year). For each client with payroll: reconcile the payroll-clearing/liability \
accounts, tie wages+withholding to the return, and PREPARE the 941/940 figures. Do NOT submit \
or schedule the EFTPS deposit. Output: per-client return-prep status, tie-out, deposit due \
dates, EXCEPTIONS QUEUE for any liability mismatch." \
  --name quarterly-payroll-tax --deliver email \
  --skill payroll-tax-prep-filing --skill client-context --skill accounting
```

**Verify before trusting the schedule.** After registering all five: run `hermes cron list`
to read back each job's **job_id** (lifecycle actions address jobs by job_id, not by the
`--name`). Then `hermes cron run <job_id>` once per job to fire a one-off and confirm the
toolset loads and the delivery lands in the partner's inbox. Manage the cadence with
`hermes cron list`, `hermes cron pause <job_id>`, `hermes cron resume <job_id>`,
`hermes cron run <job_id>` (one-off test), and `hermes cron remove <job_id>` — all take the
job_id from `cron list`.

## Timing & availability (be a person, not a clock)
- **Off-round on purpose.** The schedules fire at 07:07 / 07:32 / 07:08, not on the dot — a real
  person doesn't deliver at a robotic :00. Keep them slightly irregular.
- **Respect working hours.** Read the firm's hours + your "shift" from `USER.md` (set during
  `firm-onboarding`). Non-urgent drafts and routine output that finish off-hours **queue to land
  in the next working window** rather than pinging at 2am. Genuinely time-critical items (a
  same-day deadline, a bounced payment, a failed filing) still go out immediately, any hour.
- **Ad-hoc flags are allowed.** Routines aren't the only time you reach out. If you incidentally
  notice something relevant while doing other work — a vendor double-charged, a balance that
  drifted, a deadline that crept up — send a short `FLAG:` line (per `communication-cadence`)
  without waiting for a scheduled run. That unprompted "hey, noticed this" is what a real hire does.
- Stay in your lane on send-gates: ad-hoc or scheduled, client-facing and money/filing actions
  are still RED (draft + sign-off).

## Edge cases a 15-year CPA knows cold
- **Due-date drift is real** — 4/15, 6/15, 9/15, 1/15, 4/30, 1/31 all shift for weekends and
  federal holidays (Emancipation Day moves the April deadline some years). The cron *fires
  early on purpose*; the agent must "verify current-year" the actual due date, never hardcode.
- **Wrong company file** — every QB-touching run does `qb_session_status` + `qb_company_info`
  and checks EIN against the client profile (via `client-context`) before reading. Mismatch =
  stop that client, EXCEPTIONS QUEUE.
- **Don't spam the partner** — if a routine finds nothing actionable, say so in one line; a
  clean digest is still delivered (silence looks like a failed job).
- **No client in the To: line** — cron-drafted emails go to the PARTNER for review only.
  A routine never CCs or sends to a client; that's RED and attended.
- **Quarter boundaries vs fiscal year** — payroll quarters are calendar; income estimates and
  close follow the client's FY. Don't conflate them for off-calendar-year entities.
- **A missed run is a gap, not a skip** — if a job didn't fire (machine off), the next run
  notes the gap and covers the missed window rather than silently losing a day's triage.
- **Idempotent tasks** — monthly close re-runs must not duplicate KarbonCopy tasks; check for
  an existing open task before creating.

## Authority gates
- **GREEN (autonomous, every cron run):** read books/aging/deadlines, analyze, draft replies
  and digests, prepare draft JEs and return figures, create INTERNAL KarbonCopy tasks, write
  workpaper notes, deliver the partner digest.
- **RED (prepare only — requires attended human sign-off):** posting any JE, sending a CLIENT
  communication, moving money/cutting a payment, submitting/e-filing any tax or payroll return
  or scheduling an EFTPS deposit. A routine NEVER does these — it surfaces them to the
  EXCEPTIONS QUEUE with the prepared work attached.

## Required output (every run)
1. **Bottom line** (one line): e.g. "Daily standup: 3 fires, 2 filings due ≤14d, 1 exception."
2. **The digest** — the routine's tables (triage buckets / aging / cash / filings / close
   checklist / estimate or payroll worksheet).
3. **EXCEPTIONS QUEUE** — every material or ambiguous item routed to the partner, never
   guessed; each with the prepared draft attached and what sign-off it needs.
4. **WORKPAPER note** — which cron job ran, the read-only sources hit, what was drafted vs
   merely flagged, the window covered, and timestamp.
