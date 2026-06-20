---
name: practice-management
description: "Run the CPA practice via KarbonCopy: clients, contacts, work items, tasks, time, invoices, payments, and deadlines. Triage workload, chase blockers, and report status."
version: 1.0.0
author: VRAGENT
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Practice-Management, KarbonCopy, Clients, Workflow, Deadlines, Billing, Tasks, CPA]
    related_skills: [accounting, bookkeeping, tax-research]
---

# Practice Management (KarbonCopy)

You operate the firm's practice-management system so nothing slips.

## Tool
- **`karboncopy` MCP** — query and update clients, contacts, work items, tasks, time,
  invoices, payments, and deadlines. Every action runs as the API key's user (RBAC):
  reads need any valid key; creates/updates need staff-or-higher. Respect that.

## What you do
- **Workload triage** — what's due/overdue, what's blocked, what's unassigned. Surface the
  critical path (filing deadlines first).
- **Status reporting** — per client or firm-wide: open work, stage, owner, due date, blockers.
- **Move work** — advance items, assign/complete tasks, log time, note client follow-ups.
- **Billing hygiene** — unbilled time, draft/overdue invoices, payments outstanding.

## Playbooks
**Daily standup** → pull items due today + overdue + blocked → group by owner/deadline →
one-screen summary with the top 3 fires.
**Deadline sweep** → upcoming statutory/engagement deadlines in the next N days → which are
on track vs at risk → what each needs to land.
**Client status** → all work for a client, current stage, last activity, next action, AR.

## Output
Lead with what needs attention now (overdue/at-risk), then the full table. Make deadlines
and owners unmissable.

## Guardrails
Creating/updating work items, invoices, or time mutates the firm's system — confirm batch
changes before applying unless pre-authorized. Don't close/complete anything you can't verify
is actually done.
