"""
VRAGENT vr-risk MCP server.

A running liability / exposure ledger. Every material (or routine) decision the
agent makes gets logged with its authority tier, the dollars at stake, and the
penalty exposure. The point is aggregation: 200 individually-immaterial GREEN
decisions can silently sum into a restatement-sized number, and exposure_summary
catches that. threshold_breached gives a hard tripwire against a dollar limit.

LOCAL SQLite at home/risk/risk.db. Decimal for money. Runs over stdio.
Registered in config.yaml under mcp_servers.vr-risk.
"""
from __future__ import annotations

import json
import os
import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vr-risk")

DB_DIR = Path(__file__).resolve().parents[3] / "home" / "risk"
DB_PATH = DB_DIR / "risk.db"

TIERS = ("GREEN", "YELLOW", "RED")


def _conn() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL DEFAULT (datetime('now')),
            client TEXT NOT NULL,
            period TEXT,
            tier TEXT NOT NULL,
            area TEXT,
            dollars TEXT NOT NULL DEFAULT '0',
            penalty_exposure TEXT NOT NULL DEFAULT '0'
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_decisions_client ON decisions (client)"
    )
    return conn


def _dec(value) -> Decimal:
    """Coerce JSON number/string/None into a non-negative-safe Decimal."""
    if value is None or value == "":
        return Decimal("0")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _money(d: Decimal) -> str:
    return str(d.quantize(Decimal("0.01")))


def _loads(args: str) -> dict:
    if not args:
        return {}
    if isinstance(args, dict):
        return args
    return json.loads(args)


@mcp.tool()
def log_decision(client: str, tier: str, area: str = "", dollars: float = 0,
                 penalty_exposure: float = 0, period: str = "") -> str:
    """Record a single decision's exposure on the risk ledger.

    client (required), tier (GREEN|YELLOW|RED, required), area, dollars ($ at
    stake on this decision), penalty_exposure (worst-case penalty/interest),
    period (optional reporting period e.g. '2026-Q2').
    Returns JSON {id, client, tier, dollars, penalty_exposure}.
    """
    client = (client or "").strip()
    if not client:
        return json.dumps({"error": "client is required"})
    tier = (tier or "").strip().upper()
    if tier not in TIERS:
        return json.dumps({"error": f"tier must be one of {TIERS}"})

    dollars = _dec(dollars)
    penalty = _dec(penalty_exposure)
    area = (area or "").strip()
    period = (period or "").strip()

    conn = _conn()
    try:
        cur = conn.execute(
            "INSERT INTO decisions (client, period, tier, area, dollars, penalty_exposure)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (client, period, tier, area, _money(dollars), _money(penalty)),
        )
        conn.commit()
        rid = cur.lastrowid
    finally:
        conn.close()

    return json.dumps(
        {
            "id": rid,
            "client": client,
            "tier": tier,
            "area": area,
            "dollars": _money(dollars),
            "penalty_exposure": _money(penalty),
        }
    )


@mcp.tool()
def exposure_summary(client: str, period: str = "") -> str:
    """Aggregate a client's logged exposure. Catches many small decisions summing big.

    client (required); period (optional — if given, only decisions tagged with
    that period are aggregated).
    Returns JSON {client, period, count, total_dollars, total_penalty, by_tier}
    where by_tier maps each tier -> {count, dollars, penalty}.
    """
    client = (client or "").strip()
    if not client:
        return json.dumps({"error": "client is required"})
    period = (period or "").strip()

    sql = "SELECT tier, dollars, penalty_exposure FROM decisions WHERE client = ?"
    params: list = [client]
    if period:
        sql += " AND period = ?"
        params.append(period)

    conn = _conn()
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    total_dollars = Decimal("0")
    total_penalty = Decimal("0")
    by_tier = {
        t: {"count": 0, "dollars": Decimal("0"), "penalty": Decimal("0")} for t in TIERS
    }
    for tier, dollars, penalty in rows:
        d = _dec(dollars)
        p = _dec(penalty)
        total_dollars += d
        total_penalty += p
        bucket = by_tier.setdefault(
            tier, {"count": 0, "dollars": Decimal("0"), "penalty": Decimal("0")}
        )
        bucket["count"] += 1
        bucket["dollars"] += d
        bucket["penalty"] += p

    by_tier_out = {
        t: {
            "count": v["count"],
            "dollars": _money(v["dollars"]),
            "penalty": _money(v["penalty"]),
        }
        for t, v in by_tier.items()
    }

    return json.dumps(
        {
            "client": client,
            "period": period or None,
            "count": len(rows),
            "total_dollars": _money(total_dollars),
            "total_penalty": _money(total_penalty),
            "by_tier": by_tier_out,
        }
    )


@mcp.tool()
def threshold_breached(client: str, limit: float, period: str = "", basis: str = "dollars") -> str:
    """Hard tripwire: has a client's total exposure crossed a dollar limit?

    client (required), limit (required), period (optional), basis
    ('dollars'|'penalty', default 'dollars' — which total to test against).
    Returns JSON {breached, total, limit, basis, count}.
    """
    client = (client or "").strip()
    if not client:
        return json.dumps({"error": "client is required"})
    if limit is None or limit == "":
        return json.dumps({"error": "limit is required"})
    limit = _dec(limit)
    period = (period or "").strip()
    basis = (basis or "dollars").strip().lower()
    if basis not in ("dollars", "penalty"):
        basis = "dollars"

    col = "dollars" if basis == "dollars" else "penalty_exposure"
    sql = f"SELECT {col} FROM decisions WHERE client = ?"
    params: list = [client]
    if period:
        sql += " AND period = ?"
        params.append(period)

    conn = _conn()
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    total = Decimal("0")
    for (val,) in rows:
        total += _dec(val)

    return json.dumps(
        {
            "breached": bool(total > limit),
            "total": _money(total),
            "limit": _money(limit),
            "basis": basis,
            "count": len(rows),
        }
    )


if __name__ == "__main__":
    mcp.run()
