---
name: portal-sentinel
description: "A daily READ-ONLY watch over the portals and UIs that silently change UNDER an accountant — IRS and state DOR sites, EFTPS, the QuickBooks UI, e-file/MeF schemas, and each client's bank/payroll portal. Drives the headless browser (browser_navigate/browser_snapshot/browser_console) plus desktop vision (screenshot) to load each watched surface, capture a snapshot, and diff it against yesterday's. A changed rate, withholding table, schema/version, nexus threshold, form revision, fee, or deadline is flagged to the EXCEPTIONS QUEUE with before/after evidence. Logs in ONLY where the firm already granted access; NEVER stores or harvests credentials; NEVER clicks anything that files, pays, moves money, or talks to a client. Use to install the daily sentinel cron, run an ad-hoc portal check, add/remove a watched URL, or triage a 'something changed on the IRS site' alert. Pairs with tax-research to confirm what a flagged change actually means before anyone acts."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Portal, Sentinel, Monitoring, Diff, Browser, Vision, Compliance, Schema, Deadlines, Read-Only]
    related_skills: [tax-research, sales-tax-nexus-determination, proactive-routines, authority-and-escalation]
---

# Portal Sentinel

Half the surprises in this job aren't your mistakes — they're changes someone else made
while you weren't looking. The IRS quietly reposts a withholding table, a state DOR bumps a
sales-tax rate or an economic-nexus threshold, EFTPS rotates a deadline, Intuit ships a new
QuickBooks UI that moves a button your workflow depends on, MeF publishes a new schema version,
a client's bank changes its statement export. You find out when something breaks. This skill is
the standing **READ-ONLY watch** that finds out *first* — it loads each watched surface daily,
snapshots it, diffs it against yesterday, and flags the delta to the EXCEPTIONS QUEUE.

## What you watch (the surfaces that move under you)
| Surface | Watch for | How |
|---|---|---|
| **IRS.gov** (pubs, withholding, forms, e-file news) | new form revisions, withholding tables, std deduction / mileage / 401k limits, deadline notices | `browser_navigate` + `browser_snapshot` |
| **State DOR portals** | sales-tax RATE changes, economic-NEXUS thresholds, filing-frequency changes, new form versions | `browser_navigate` + `browser_snapshot` |
| **EFTPS** | deposit-schedule notices, due-date shifts, site/login changes (login ONLY if access granted) | `browser_navigate` (read-only) |
| **QuickBooks UI** (desktop app) | moved/renamed buttons, new dialogs, version banners that can break a saved workflow | `screenshot` (desktop vision) |
| **e-file / MeF schemas** | new schema version, deprecated elements, business-rule changes | `browser_navigate` + `browser_console` for version strings |
| **Client bank / payroll portals** | statement-export format, login-flow changes, new MFA prompts, fee/rate changes | `browser_navigate` (ONLY within granted access) |

Keep the authoritative list in `home/portal-sentinel/watchlist.json` — one entry per surface:
url or app target, a friendly name, the client it belongs to (or `firm`), the CSS/section that
matters, and whether login is granted. New surfaces are *added* here, never hardcoded in a prompt.

## How the daily diff works
1. **Load** each watched URL with `browser_navigate`; for the QuickBooks UI use `screenshot`.
2. **Snapshot** the meaningful state — `browser_snapshot` for the accessibility/DOM tree (stable,
   diffable text — prefer it over a raw pixel diff), and `browser_console` to read any version /
   schema string the page exposes. For desktop, the `screenshot` image + an OCR/vision read.
3. **Normalize** — strip volatile noise (session tokens, timestamps, ad slots, "as of" dates,
   cache-buster query strings) so you diff *content*, not chrome. A diff that's all noise is a
   false positive and trains the partner to ignore you.
4. **Diff vs yesterday** — compare to the prior snapshot under `home/portal-sentinel/snapshots/<surface>/`.
   Save today's snapshot (text tree, console strings, and the screenshot) with the date.
5. **Classify the delta** — MATERIAL (a rate/threshold/schema/deadline/form# moved) vs COSMETIC
   (layout/wording with no compliance effect). Only material deltas raise an exception.
6. **Flag** — material change -> EXCEPTIONS QUEUE with before/after evidence (see Output).

## Credentials & access (the bright line)
- **Login ONLY where the firm already holds granted access** and the watchlist entry says so.
  Use the credential store the firm configured; **NEVER** type a password the agent "found,"
  guessed, or was pasted into chat, and **NEVER** persist, log, screenshot, or echo a secret,
  MFA code, or session cookie. Snapshots are scrubbed of any auth material before they're saved.
- **No new accounts, no password resets, no MFA enrollment** — those are RED, attended only.
- If a portal now demands an MFA step the agent can't satisfy unattended, that's not a failure to
  brute past — it's a *flag*: "BankX added MFA, manual login needed," straight to the queue.
- Respect each site's terms and rate limits — one gentle daily read per surface, no scraping storms.

## READ-ONLY — the hard stop
Every action here is **look, snapshot, diff, report**. A sentinel run NEVER:
clicks Pay / File / Submit / Authorize, schedules an EFTPS deposit, e-files a return, moves money,
edits a client record, sends a client-facing message, or accepts any "I agree / continue" that
mutates state. If reaching the watched content *requires* a mutating click, you stop and flag it
instead. Set any tool with a mutating mode to its read/dry path defensively. The only outputs are
a snapshot on disk and a digest to the **partner**.

## Daily cron (install once)
The sentinel runs every morning, read-only, and emails the partner. Schedule and prompt are
**positional**; attach playbooks by **repeating `--skill`**; single `--deliver`; no `--tz`.

```bash
hermes cron add "12 6 * * *" \
  "READ-ONLY portal sentinel. Load every surface in home/portal-sentinel/watchlist.json. \
For web surfaces use browser_navigate then browser_snapshot (accessibility/DOM tree) and \
browser_console (version/schema strings); for the QuickBooks UI use the desktop screenshot tool. \
Log in ONLY where the watchlist marks access granted — NEVER store, log, or echo any password, \
MFA code, or cookie; scrub secrets from every saved snapshot. Normalize out volatile noise \
(tokens, timestamps, ad slots) then DIFF against yesterday's snapshot under \
home/portal-sentinel/snapshots/. Classify each delta MATERIAL (rate/threshold/schema/deadline/ \
form# changed) vs COSMETIC. Save today's snapshot. Do NOT click Pay/File/Submit/Authorize, \
schedule any deposit, e-file, move money, or send anything to a client — if reaching content \
needs a mutating click, STOP and flag it. Output: one-line bottom line, a CHANGES table \
(surface / what moved / before -> after), and an EXCEPTIONS QUEUE for every material change with \
before/after evidence. Use tax-research to note what a flagged change means; do NOT act on it." \
  --name portal-sentinel --deliver email \
  --skill portal-sentinel --skill tax-research --skill authority-and-escalation
```

After registering, `hermes cron list` to read back the **job_id**, then `hermes cron run <job_id>`
once to confirm the watchlist loads, a snapshot lands on disk, and the digest reaches the partner.

## Edge cases a careful watcher knows
- **First-ever run has no baseline** — record the first snapshot as the baseline and say
  "baselined, no diff yet," not "nothing changed."
- **Site down / timeout** — distinguish *unreachable* (transient, retry once, then flag if still
  down) from *changed*. A 404 on a watched form page is itself a material flag.
- **Cosmetic redesign hides a real change** — a full relayout can mask a moved threshold; when the
  whole page diffs, fall back to targeting the specific section/value in the watchlist entry.
- **A flag is a lead, not a conclusion** — "IRS posted a new mileage rate" goes to the queue with
  the source; `tax-research` confirms the figure and effective date before anyone relies on it.
- **Don't double-flag** — once a change is acknowledged, update the baseline so it doesn't re-fire
  every day; a re-flag only if it changes *again*.
- **Wrong/stale URL** — IRS and DOR sites move pages; a redirect to a "page moved" stub is a flag
  to update the watchlist, not a content change.
- **Quiet day still delivers** — no material deltas? Send the one-line "all watched surfaces
  steady" so a silent job never looks like a dead one.

## Authority gates
- **GREEN (autonomous, every run):** navigate to and snapshot a watched surface, read console
  version strings, screenshot the QuickBooks UI, diff vs baseline, classify deltas, save snapshots,
  flag material changes, deliver the partner digest, add/remove a watchlist entry on request.
- **YELLOW (do, but surface for confirmation):** logging into a granted portal whose login flow
  just changed; updating a watchlist URL after a redirect — do it, note it in the digest.
- **RED (never in a sentinel run — attended, signed-off):** any click that files, pays, submits,
  authorizes, moves money, or schedules a deposit; creating/resetting an account or MFA; sending
  anything client-facing; storing or transmitting a credential. These are flagged, never done.

## Required output (every run)
1. **Bottom line** (one line): "Portal sentinel: 11 surfaces checked, 2 material changes, 1 login flag."
2. **CHANGES table** — surface / what moved / before -> after / material or cosmetic.
3. **EXCEPTIONS QUEUE** — each material change with before/after evidence (snapshot path or
   screenshot), the source URL, and a one-line "what this likely means / who to tell."
4. **WORKPAPER note** — surfaces checked, snapshots saved (paths), what was unreachable, and
   timestamp; confirm no credentials were stored and no mutating action was taken.
