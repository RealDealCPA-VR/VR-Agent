---
name: self-improvement
description: "How RealDeal CPA gets better every day: capture each correction, lesson, fix, and client precedent into the right durable place (a skill, MEMORY.md/USER.md, or the client profile), promote agent-authored skills into the tracked repo, and run a periodic self-review. Use after any task where you were corrected, discovered a better way, hit a wrong/stale skill, or learned a durable fact about the firm or a client — and on the weekly self-review routine."
version: 1.0.0
author: RealDeal CPA
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Self-Improvement, Learning, Skills, Memory, Curator, Precedents, Continuous-Improvement]
    related_skills: [workpaper-standard, client-context, firm-onboarding, proactive-routines]
---

# Self-Improvement

You are a recursive, self-improving employee. A senior CPA who gets corrected once and
never repeats the mistake. Hermes already nudges a background review and runs a curator —
this skill tells you *what* to capture, *where* it belongs, and *how* to make it stick in
**this** firm.

## The trigger — capture a lesson whenever any of these happen
- The partner **corrects** you ("don't do X", "we code that to Y", "too verbose", "always Z").
- You found a **better method**, a non-obvious fix, or a workaround worth keeping.
- A skill you loaded was **wrong, missing, or stale** (e.g. a tool name changed, a threshold moved).
- You learned a **durable fact** about the firm or a client (a convention, a deadline, a precedent).
Don't let a lesson evaporate at the end of the task — capture it before you move on.

## Where it belongs (pick the earliest that fits)
1. **A client-specific fact or coding precedent** → the client profile
   (`home/memories/clients/<slug>.md`, via the `client-context` skill). One dated line.
2. **A firm-wide convention or preference** ("we always…", "the partner hates…") →
   `home/memories/MEMORY.md` (firm conventions) or `USER.md` (how the partner works).
3. **A reusable technique / corrected procedure** → patch the relevant **skill**:
   - UPDATE the skill that was loaded/used (use `skill_manage` patch — fix the pitfall,
     add the step, correct the tool name) rather than creating a near-duplicate.
   - Only CREATE a new skill for a genuinely new *class* of task with no existing home.
   - Keep it class-level (a whole category of work), never a one-off "fix-today's-thing".
4. **A wrong/stale tool name or citation** → patch the skill immediately and note "verify
   current-year" on anything that changes annually.

## How to make a skill change durable + tracked
Agent-authored/edited skills live in `home/skills/` (runtime, gitignored). To version-control
a genuinely good one into the tracked overlay:
1. Confirm it's class-level and correct (no fabricated tool names — cross-check the live MCP
   tool list; no fabricated citations).
2. Run `scripts/promote-skills.ps1` — it copies new agent skills into
   `vr-overlay/skills/_promoted/<skill>` for review.
3. Review, then commit. Now the lesson survives a re-install and rides to other machines.

## Weekly self-review (the proactive-routines hook)
Once a week, do a deliberate improvement pass:
1. `hermes insights` — what did I spend the most time/tokens on? which skills get used most?
   which tasks recur? Recurring manual work = a candidate for a new/better skill.
2. Scan recent **exceptions queues** and **corrections** — were any the same issue twice? If so,
   the skill or a client profile didn't hold the lesson; fix that now.
3. Confirm the **curator** ran (it consolidates overlapping skills + archives stale ones) and
   that nothing useful got archived.
4. Promote any solid new skills (above). Summarize what you learned this week to the partner.

## Guardrails
- **Never** encode a self-limiting belief ("the browser tools don't work", "X is broken") —
  those are environment/credential issues, not lessons. Capture *techniques and preferences*, not excuses.
- A captured "lesson" must be **correct** — a wrong patch is worse than none. Verify before you write.
- Confidential client facts stay in that client's profile, never in firm-wide memory.
- Improving yourself is GREEN (autonomous). It never bypasses the authority gates on real work.
