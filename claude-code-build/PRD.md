# PRD — RealDeal CPA Agent on Claude Code

**Product:** RealDeal CPA — an AI senior-accountant teammate ("Remy")
**Owner:** Valentino (RealDeal CPA, sole user)
**Runtime target:** Claude Code (subscription-powered)
**Status:** Design / pre-build
**Doc version:** 1.0 (2026-06-23)

---

## 1. Summary
Rebuild the existing RealDeal CPA agent — today a Hermes-framework overlay that calls the
Anthropic API — as a **Claude Code** agent, so it runs on a **Claude Max subscription** while
preserving its full capability set. The product is an always-available, deeply-integrated
accounting/tax/advisory teammate for **one CPA firm's internal use**, not a resold product.

## 2. Problem & motivation
- The current build is excellent but is fueled by a metered API key (pay-per-token).
- The owner holds a Claude **Max** subscription and wants the agent powered by it.
- A subscription cannot legitimately power Hermes (third-party framework → API) — see
  [COMPLIANCE.md](./COMPLIANCE.md). The only sanctioned subscription path is **Claude Code**.
- Therefore: re-platform onto Claude Code, keep the capabilities, change the engine.

## 3. Target user & use context
- **Single user / internal only.** The owner, doing his own firm's work. Not multi-tenant,
  not client-facing-as-a-product, never resold. (This is the linchpin of compliance.)
- Windows desktop primary; QuickBooks Desktop, KarbonCopy, browser, email in the loop.
- Bursty, working-hours-weighted usage with some scheduled background routines.

## 4. Goals
1. **Capability parity** with the current build (see [INVENTORY-AND-PORT-MAP.md](./INVENTORY-AND-PORT-MAP.md)):
   - Domain expertise: accounting, bookkeeping, tax research, sales/payroll tax, advisory,
     marketing, email, practice management (the 47 skills).
   - Tooling: QuickBooks, KarbonCopy, double-entry ledger, deterministic verification,
     cryptographic provenance, cross-client benchmarking, liability/exposure, capacity —
     plus desktop GUI control and web browsing.
   - Behavior: the "Remy" persona, authority tiers (GREEN/YELLOW/RED), workpaper standard,
     adversarial self-review, commitments/continuity.
2. **Run on the Max subscription** via `claude login` (OAuth), including scheduled headless runs.
3. **Stronger guardrails than today**: make the RED authority gate **deterministic** via
   Claude Code hooks (not just persona instructions).
4. **Packaged + portable**: ship the whole agent as a single Claude Code **plugin** that can
   be installed on a fresh machine in minutes.
5. **A Command Center** view of the agent's work and subagents (rebuilt as a standalone app).

## 5. Non-goals (explicit)
- **Not** multi-provider. Claude Code is Claude-only; that's acceptable (the point is to use
  the subscription).
- **Not** a client-facing or resellable product. Any client deliverable stays under human
  review / labeled AI-assisted; the agent never deceives a client or regulator that it is a
  licensed human CPA. (Hard line, carried from the current build.)
- **Not** a port of Hermes-specific internals that have no Claude Code equivalent (holographic
  memory provider, curator daemon, skin engine, Slack gateway) — replaced by simpler
  equivalents or deferred (see port map).
- **Not** trying to beat the API on raw throughput — heavy 24/7 automation is out of scope
  (subscription usage limits; see §8).

## 6. Capability requirements (carried from the current build)
| Area | Requirement |
|---|---|
| Bookkeeping | Categorize, reconcile, month-end & continuous close, AP/AR, inventory/COGS |
| Tax | Sales-tax nexus + filing, payroll tax (941/940), 1099, research with citations |
| Verification | **Every number deterministically re-derived** (no LLM arithmetic) before assertion |
| Provenance | SHA-256 evidence + hash-chained activity ledger + one-click dossier |
| Advisory | 3-statement/DCF models, cohort benchmarking, capacity/realization |
| Desktop | See + drive Windows GUI (QuickBooks Desktop, any app) |
| Web | Browse + research |
| Persona | "Remy" — human register, right-sized messages, continuity, never deceptive |
| Authority | GREEN autonomous / YELLOW do-and-log / RED prepare-then-human-signs |
| Audit | Workpaper standard with re-perform manifest; adversarial independent review |

## 7. Success criteria (acceptance)
- The agent authenticates and runs on the Max subscription (no API key), interactively and
  in at least one scheduled headless routine.
- The 9 MCP servers connect under Claude Code and their tools are callable.
- A representative end-to-end task works: e.g., "reconcile this account and produce a
  workpaper" — using QuickBooks + vr-verify + vr-provenance, with a RED gate enforced by a hook.
- The 47 skills are discoverable/invocable.
- The Command Center shows live subagent/work state.
- The whole thing installs from the plugin on a clean machine.
- Zero secrets in the repo; subscription auth via `claude login`.

## 8. Key product decisions & rationale
- **Engine = Claude Code, not the Agent SDK.** The Agent SDK requires an API key; only Claude
  Code CLI accepts subscription auth. (Confirmed; see COMPLIANCE.)
- **Authority gate = hooks.** Today RED is a prompt instruction; on Claude Code a `PreToolUse`
  hook can *deterministically* block any posting/filing/money-moving tool call until a human
  approves. This is a real safety upgrade — adopt it.
- **Packaging = one plugin.** Bundle skills + subagents + hooks + `.mcp.json` so the agent is
  one installable unit.

## 9. The central tradeoff (decide before building)
| | Subscription (Claude Code) — this build | API key (current Hermes build) |
|---|---|---|
| Cost | Flat monthly (Max) | Per-token (Max credits offset some) |
| Usage | **Capped** (rolling-window limits) | Uncapped |
| Best for | Bursty, working-hours, single-user | Heavy/always-on automation |
| Providers | Claude only | Multi-provider |

**Recommendation:** For a single CPA's internal, working-hours-weighted use, the subscription
cap is acceptable and the flat cost is attractive. If the agent later needs to grind every
client every day 24/7, revisit the API. Design the build so the **same MCP servers + skills**
work under either runtime, keeping the door open.

## 10. Risks
- **Usage limits** throttle a heavy automation schedule → mitigate by scoping background runs
  and keeping interactive work primary.
- **Command Center rebuild** is the largest single work item → reuse the existing React Flow
  canvas; keep the backend thin.
- **Claude Code evolves** → pin a version; re-verify config formats against live docs at build time.
- **Compliance drift** → keep usage internal-only; re-confirm terms periodically (COMPLIANCE.md).
