# Compliance — running RealDeal CPA on a Claude Max subscription

This documents *why* the Claude Code build can legitimately run on a Max subscription, where the
boundary is, and the sources. **It is not legal advice and not an Anthropic determination** —
for anything binding, confirm with Anthropic. It reflects research current as of 2026-06-23.

---

## The bottom line
- ✅ **PERMITTED:** A custom, branded agent built **on Claude Code**, authenticated with your
  **Max subscription** (`claude login` / OAuth), used **solely for your own internal firm work** —
  including scheduled headless (`claude -p`) runs.
- ⛔ **NOT PERMITTED:** Powering a **third-party framework** (Hermes, or any non-Anthropic agent
  runtime) with your subscription credentials. That is a Terms-of-Service violation that Anthropic
  actively enforces. (This is exactly why the current Hermes build must use an API key, and why this
  re-platform onto Claude Code exists.)

## Why Claude Code is the sanctioned path
- A Claude Pro/Max **subscription** entitles you to Anthropic's **first-party** products — the
  claude.ai apps and **Claude Code**. Claude Code, including its **headless** mode and automated/cron
  use, is covered by the subscription when you authenticate with `claude login`. No API key required.
- The **Claude Agent SDK** is *not* a subscription path — it **requires an API key**. So "use the
  subscription" specifically means "use Claude Code as the runtime," not the SDK and not Hermes.
- The **Anthropic API** is the separate, metered, commercial product (per-token). The current
  Hermes build uses it; this build replaces it with subscription-backed Claude Code.

## The acceptable-use boundary (do not cross)
Anthropic's test, in plain terms: *would a reasonable person see this as **your** work, AI-assisted —
not an AI product you're reselling?*

| Permitted (this build's scope) | Not permitted on a subscription |
|---|---|
| You, doing your own firm's work | Reselling the agent or its access |
| Internal automation / co-pilot | A client-facing or multi-user SaaS |
| Scheduled background runs for your firm | A generic LLM proxy/backend for another app |
| Custom branding, skills, MCP, subagents | Tunneling a third-party framework through subscription auth |

**Carried hard line (independent of billing):** the agent never implies to a **client or a
regulator** that it is a licensed human CPA. Client-facing deliverables stay under human review,
in your name, or labeled AI-assisted. This is a professional-ethics rule, not just a ToS one.

## What this build does to stay inside the line
- **Single user, internal only.** No client login, no multi-tenant serving, no resale. (PRD §3, §5.)
- **Subscription auth via `claude login`** — never subscription credentials wired into a third-party tool.
- **Secrets never committed** — model auth is the subscription (no key in repo); external-tool
  secrets (QuickBooks/Karbon) stay in gitignored launchers.
- **Deterministic guardrails** (authority-gate hooks) keep money/filing actions human-approved.

## The usage-limit caveat (operational, not legal)
Subscriptions have **rolling-window usage limits** (Max is higher than Pro). Heavy, always-on
automation can hit them; the API has no such cap (it just bills per token). This build is scoped for
a **single CPA's bursty, working-hours** use, where the cap is acceptable. If usage outgrows the
subscription, the same MCP servers + skills can run under an API key again — keep that door open
(PRD §9).

## Caveats on this document
- Not legal counsel; not an official Anthropic ruling. Confirm specifics with Anthropic before
  relying on them commercially.
- Anthropic's terms and Claude Code's capabilities evolve. **Re-verify** the subscription/headless
  position and the acceptable-use language at build time.

## Sources (as of 2026-06-23)
- Use Claude Code with your Pro/Max plan — Anthropic Help Center.
- Subscription vs API separation — Anthropic Help Center ("why pay separately for the API").
- Using Agents according to the Usage Policy — Anthropic Help Center.
- Claude Code docs (auth, headless): https://code.claude.com/docs
- Claude Agent SDK requires an API key (not subscription) — Agent SDK overview + tracking issue.
