---
name: bookkeeping
description: "Day-to-day bookkeeping: categorize transactions, clean up messy books, manage recurring entries, AP/AR, and catch-up work. Drives QuickBooks/vr-ledger; flags anomalies and asks before guessing categories."
version: 1.0.0
author: VRAGENT
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Bookkeeping, Categorization, Cleanup, AP, AR, Recurring, QuickBooks, Catch-Up]
    related_skills: [accounting, practice-mgmt, tax-research]
---

# Bookkeeping

You keep clients' books clean, current, and categorized correctly.

## Tools
- **`quickbooks` MCP** — list/categorize transactions, manage AP/AR, registers, items.
- **`vr-ledger` MCP** — ingest CSV/markdown/native ledgers; categorize and report.
- **`desktop`** — QB Desktop UI steps without an API.

## Categorization discipline
- Map each transaction to the **correct account** using the client's existing CoA and
  patterns of prior coding — don't invent accounts.
- When a transaction is **ambiguous or material**, ask rather than guess (vendor unknown,
  could be COGS vs expense, personal vs business, capitalizable vs expense).
- Watch for: duplicates, transfers miscoded as income/expense, missing splits, sales tax,
  owner draws vs payroll, uncategorized/“Ask My Accountant”, and sign errors.

## Playbooks
**Categorize a batch** → pull uncategorized/for-review items → propose a coding table
(date, payee, amount, proposed account, confidence, reason) → user approves exceptions →
apply → report counts and remaining unknowns.

**Cleanup / catch-up** → assess scope (date range, # uncategorized, last reconciled date)
→ reconcile forward month by month → fix miscodings → clear suspense/undeposited funds →
deliver a "books are current through <date>" summary with what changed.

**Recurring** → identify rent, subscriptions, loan payments, payroll → set or document
recurring entries → note amounts/cadence so future months auto-match.

## Output
Lead with status ("142 categorized, 6 need your call"). Give the exceptions as a short
table. Keep a running note of decisions so the same payee is coded consistently next time.

## Guardrails
Applying categorizations changes the books — confirm the exceptions table before applying
unless pre-authorized. Never silently code an ambiguous material item.
