"""
VRAGENT vr-cohort MCP server.

The firm's PRIVATE cross-client benchmark store. Lets RealDeal CPA compare one
client's metrics against the de-identified distribution of every other client in
the same NAICS industry code, without ever storing a client name.

Each observation is keyed by (naics, metric, client_hash) where client_hash is an
opaque, caller-supplied identifier (e.g. a SHA-256 of the client id). A client may
contribute exactly ONE current value per (naics, metric) — re-adding upserts it.

Tools:
  add_observation(naics, metric, value, client_hash) -> upsert one data point
  cohort_stats(naics, metric)         -> {n, mean, stdev, p25, p50, p75}
  score(naics, metric, value)         -> {z, percentile, n}

LOCAL SQLite at home/cohort/cohort.db. Pure stdlib + mcp. Runs over stdio.
"""
from __future__ import annotations

import json
import os
import sqlite3
import statistics
from decimal import Decimal, InvalidOperation

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vr-cohort")

_DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "home",
    "cohort",
)
_DB_PATH = os.path.join(_DB_DIR, "cohort.db")


def _conn() -> sqlite3.Connection:
    os.makedirs(_DB_DIR, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS observations (
            naics       TEXT NOT NULL,
            metric      TEXT NOT NULL,
            client_hash TEXT NOT NULL,
            value       TEXT NOT NULL,
            PRIMARY KEY (naics, metric, client_hash)
        )
        """
    )
    return conn


def _dec(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"value not numeric: {value!r}")


def _values(conn: sqlite3.Connection, naics: str, metric: str) -> list[float]:
    rows = conn.execute(
        "SELECT value FROM observations WHERE naics = ? AND metric = ?",
        (naics, metric),
    ).fetchall()
    return [float(r[0]) for r in rows]


def _percentile(sorted_vals: list[float], q: float) -> float:
    """Linear-interpolation percentile (q in [0,1]) over a sorted list."""
    if not sorted_vals:
        raise ValueError("no data")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = q * (len(sorted_vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * frac


def _json(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


@mcp.tool()
def add_observation(naics: str, metric: str, value: float, client_hash: str) -> str:
    """Upsert ONE de-identified benchmark data point.

    naics: NAICS industry code (string, e.g. "44-45").
    metric: metric name (e.g. "gross_margin_pct").
    value: numeric value for this client.
    client_hash: opaque client identifier (NEVER a client name). One value per
        (naics, metric) per client_hash — re-adding replaces the prior value.

    Returns JSON {ok, naics, metric, n} where n is the cohort size after upsert.
    """
    val = _dec(value)  # validates numeric; stored as canonical string
    conn = _conn()
    try:
        conn.execute(
            """
            INSERT INTO observations (naics, metric, client_hash, value)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (naics, metric, client_hash)
            DO UPDATE SET value = excluded.value
            """,
            (naics, metric, client_hash, str(val)),
        )
        conn.commit()
        n = conn.execute(
            "SELECT COUNT(*) FROM observations WHERE naics = ? AND metric = ?",
            (naics, metric),
        ).fetchone()[0]
    finally:
        conn.close()
    return _json({"ok": True, "naics": naics, "metric": metric, "n": n})


@mcp.tool()
def cohort_stats(naics: str, metric: str) -> str:
    """Distribution stats for a (naics, metric) cohort.

    Returns JSON {n, mean, stdev, p25, p50, p75}. stdev is the sample standard
    deviation (None when n < 2). Returns {n: 0, ...nulls} when no data.
    """
    conn = _conn()
    try:
        vals = _values(conn, naics, metric)
    finally:
        conn.close()
    n = len(vals)
    if n == 0:
        return _json(
            {"n": 0, "mean": None, "stdev": None, "p25": None, "p50": None, "p75": None}
        )
    sv = sorted(vals)
    return _json(
        {
            "n": n,
            "mean": statistics.fmean(vals),
            "stdev": statistics.stdev(vals) if n >= 2 else None,
            "p25": _percentile(sv, 0.25),
            "p50": _percentile(sv, 0.50),
            "p75": _percentile(sv, 0.75),
        }
    )


@mcp.tool()
def score(naics: str, metric: str, value: float) -> str:
    """Score a value against its (naics, metric) cohort.

    Returns JSON {z, percentile, n}:
      z          z-score = (value - mean) / sample_stdev (None when n < 2 or stdev 0).
      percentile fraction of cohort observations <= value, in [0, 1].
      n          cohort size.
    Returns {z: null, percentile: null, n: 0} when the cohort is empty.
    """
    v = float(_dec(value))
    conn = _conn()
    try:
        vals = _values(conn, naics, metric)
    finally:
        conn.close()
    n = len(vals)
    if n == 0:
        return _json({"z": None, "percentile": None, "n": 0})
    mean = statistics.fmean(vals)
    z = None
    if n >= 2:
        sd = statistics.stdev(vals)
        if sd > 0:
            z = (v - mean) / sd
    percentile = sum(1 for x in vals if x <= v) / n
    return _json({"z": z, "percentile": percentile, "n": n})


if __name__ == "__main__":
    mcp.run()
