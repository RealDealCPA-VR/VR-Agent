"""
VRAGENT vr-capacity MCP server.

Deterministic realization + surge-triage engine (the math, not the LLM) for a
CPA firm's engagement workload. Tracks budget-vs-actual hours, deadlines, and
completion per engagement in a local SQLite store, then ranks engagements by a
blended risk score (deadline proximity + incompletion + over-budget overrun) so
the agent knows what to work on first during a surge.

Pure in-process, stdlib only. LOCAL SQLite at home/capacity/capacity.db.
Registered in config.yaml under mcp_servers.vr-capacity. Runs over stdio.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vr-capacity")

# Runtime DB under HERMES_HOME (gitignored), portable across machines.
DB_DIR = Path(os.environ.get("HERMES_HOME") or (Path(__file__).resolve().parents[3] / "home")) / "capacity"
DB_PATH = DB_DIR / "capacity.db"


def _conn() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS engagements (
            client          TEXT PRIMARY KEY,
            budget_hours    TEXT NOT NULL,
            actual_hours    TEXT NOT NULL,
            deadline_iso    TEXT NOT NULL,
            completion_pct  TEXT NOT NULL
        )
        """
    )
    return conn


def _dec(value) -> Decimal:
    """Coerce an int/float/str/Decimal into a Decimal, raising on garbage."""
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"not a number: {value!r}")


def _q2(d: Decimal) -> float:
    """Round a Decimal to 2dp and return as float for JSON output."""
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _clamp_pct(d: Decimal) -> Decimal:
    if d < 0:
        return Decimal("0")
    if d > 100:
        return Decimal("100")
    return d


def _json(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


@mcp.tool()
def load_engagement(
    client: str,
    budget_hours: float,
    actual_hours: float,
    deadline_iso: str,
    completion_pct: float,
) -> str:
    """Upsert one engagement's budget-vs-actual hours, deadline, and % complete.

    client:         client / engagement name (primary key — re-loading updates).
    budget_hours:   budgeted hours for the engagement (> 0).
    actual_hours:   hours burned so far (>= 0).
    deadline_iso:   filing/delivery deadline as ISO date YYYY-MM-DD.
    completion_pct: percent of work done, 0-100 (clamped).
    """
    budget = _dec(budget_hours)
    actual = _dec(actual_hours)
    pct = _clamp_pct(_dec(completion_pct))
    if budget <= 0:
        raise ValueError("budget_hours must be > 0")
    if actual < 0:
        raise ValueError("actual_hours must be >= 0")
    # Validate the deadline parses as a real ISO date.
    date.fromisoformat(deadline_iso)

    conn = _conn()
    try:
        conn.execute(
            """
            INSERT INTO engagements
                (client, budget_hours, actual_hours, deadline_iso, completion_pct)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(client) DO UPDATE SET
                budget_hours   = excluded.budget_hours,
                actual_hours   = excluded.actual_hours,
                deadline_iso   = excluded.deadline_iso,
                completion_pct = excluded.completion_pct
            """,
            (client, str(budget), str(actual), deadline_iso, str(pct)),
        )
        conn.commit()
    finally:
        conn.close()

    return _json(
        {
            "client": client,
            "budget_hours": _q2(budget),
            "actual_hours": _q2(actual),
            "deadline_iso": deadline_iso,
            "completion_pct": _q2(pct),
            "status": "loaded",
        }
    )


def _rows():
    conn = _conn()
    try:
        cur = conn.execute(
            "SELECT client, budget_hours, actual_hours, deadline_iso, completion_pct"
            " FROM engagements"
        )
        return cur.fetchall()
    finally:
        conn.close()


def _score(budget: Decimal, actual: Decimal, deadline_iso: str, pct: Decimal, today: date):
    """Return (score, driver, components) for one engagement.

    Three normalized 0..1 sub-scores, then a weighted blend (0..100):
      deadline : closer (and especially past-due) deadlines score higher.
      incomplete: remaining work = (100 - completion_pct) / 100.
      overrun  : over-budget fraction = max(0, actual/budget - 1), capped.
    """
    # Deadline proximity over a 30-day surge horizon. Past-due saturates at 1.0.
    days_left = (date.fromisoformat(deadline_iso) - today).days
    horizon = 30
    if days_left <= 0:
        deadline_sub = Decimal("1")
    elif days_left >= horizon:
        deadline_sub = Decimal("0")
    else:
        deadline_sub = (Decimal(horizon) - Decimal(days_left)) / Decimal(horizon)

    incomplete_sub = (Decimal("100") - pct) / Decimal("100")

    ratio = actual / budget if budget > 0 else Decimal("0")
    overrun_raw = ratio - Decimal("1")
    if overrun_raw < 0:
        overrun_raw = Decimal("0")
    # Cap overrun contribution at 100% over budget (ratio 2.0 -> 1.0).
    overrun_sub = overrun_raw if overrun_raw < 1 else Decimal("1")

    w_deadline = Decimal("0.50")
    w_incomplete = Decimal("0.30")
    w_overrun = Decimal("0.20")

    score = (
        w_deadline * deadline_sub
        + w_incomplete * incomplete_sub
        + w_overrun * overrun_sub
    ) * Decimal("100")

    components = {
        "deadline": _q2(w_deadline * deadline_sub * Decimal("100")),
        "incompletion": _q2(w_incomplete * incomplete_sub * Decimal("100")),
        "overrun": _q2(w_overrun * overrun_sub * Decimal("100")),
    }
    driver = max(components, key=components.get)
    return score, driver, components, days_left


@mcp.tool()
def triage(today_iso: str) -> str:
    """Rank all engagements by surge-risk score (most urgent first).

    today_iso: the 'as-of' date YYYY-MM-DD used for deadline proximity.

    Score (0-100) blends deadline proximity (50%), incompletion (30%), and
    over-budget overrun (20%). Each entry reports the score, the dominant
    driver, the component breakdown, and days-to-deadline (negative = past due).
    """
    today = date.fromisoformat(today_iso)
    out = []
    for client, budget_s, actual_s, deadline_iso, pct_s in _rows():
        budget = _dec(budget_s)
        actual = _dec(actual_s)
        pct = _dec(pct_s)
        score, driver, components, days_left = _score(
            budget, actual, deadline_iso, pct, today
        )
        out.append(
            {
                "client": client,
                "risk_score": _q2(score),
                "driver": driver,
                "days_to_deadline": days_left,
                "completion_pct": _q2(pct),
                "over_budget": actual > budget,
                "components": components,
            }
        )
    # Most-urgent first; tie-break by soonest deadline then name for determinism.
    out.sort(key=lambda e: (-e["risk_score"], e["days_to_deadline"], e["client"]))
    return _json({"as_of": today_iso, "engagements": out})


@mcp.tool()
def realization_summary() -> str:
    """Per-client realization: budget vs actual hours and the realization ratio.

    realization_pct = budget_hours / actual_hours * 100 (capacity efficiency:
    >100 means under budget / efficient, <100 means over budget / eroding
    realization). If no hours have been burned yet it is reported as null.
    over_budget flags actual_hours > budget_hours.
    """
    clients = []
    for client, budget_s, actual_s, _deadline, _pct in _rows():
        budget = _dec(budget_s)
        actual = _dec(actual_s)
        if actual > 0:
            realization = _q2(budget / actual * Decimal("100"))
        else:
            realization = None
        clients.append(
            {
                "client": client,
                "budget_hours": _q2(budget),
                "actual_hours": _q2(actual),
                "realization_pct": realization,
                "over_budget": actual > budget,
            }
        )
    clients.sort(key=lambda c: c["client"])
    return _json({"clients": clients})


if __name__ == "__main__":
    mcp.run()
