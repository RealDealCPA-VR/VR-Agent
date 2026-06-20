"""
VRAGENT vr-ledger MCP server.

Exposes the local VR-Ledger plain-text double-entry engine (vrledger package) as
MCP tools: validate a ledger, and produce balances / balance sheet / income
statement / cash-flow statement as JSON. Pure in-process — no external service.

Registered in config.yaml under mcp_servers.vr-ledger. Runs over stdio.
"""
from __future__ import annotations

import inspect
import json
from datetime import date
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vr-ledger")


def _load(path: str):
    from vrledger.loader import load_file
    return load_file(path)


def _parse_date(s: Optional[str]) -> Optional[date]:
    return date.fromisoformat(s) if s else None


def _resolve(attr):
    """Return attr() if it's a method, else the attribute (handles property vs method)."""
    return attr() if callable(attr) else attr


def _ledger_errors(ledger) -> list[str]:
    errs = getattr(ledger, "errors", None) or []
    out = []
    for e in errs:
        out.append(str(getattr(e, "message", e)))
    return out


def _call_report(fn, ledger, at: Optional[str], start: Optional[str], end: Optional[str]):
    """Call a report fn passing only the date kwargs it actually accepts."""
    params = inspect.signature(fn).parameters
    kwargs = {}
    if "at" in params and at:
        kwargs["at"] = _parse_date(at)
    if "start" in params and start:
        kwargs["start"] = _parse_date(start)
    if "end" in params and end:
        kwargs["end"] = _parse_date(end)
    return fn(ledger, **kwargs)


def _json(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


@mcp.tool()
def validate(path: str) -> str:
    """Parse a ledger file and report any errors. Returns 'valid' or the error list.

    path: path to a ledger file (.beancount/.ledger/.md/.csv — format auto-detected).
    """
    ledger = _load(path)
    errs = _ledger_errors(ledger)
    if not errs:
        n = len(_resolve(ledger.transactions))
        return f"valid — {n} transactions, {len(_resolve(ledger.accounts))} accounts"
    return "errors:\n- " + "\n- ".join(errs)


@mcp.tool()
def balances(path: str, at: Optional[str] = None) -> str:
    """Account balances as JSON. at: optional ISO date (YYYY-MM-DD) cutoff."""
    from vrledger import reports
    return _json(_call_report(reports.balances, _load(path), at, None, None))


@mcp.tool()
def balance_sheet(path: str, at: Optional[str] = None) -> str:
    """Balance sheet (assets/liabilities/equity) as JSON. at: optional ISO date."""
    from vrledger import reports
    return _json(_call_report(reports.balance_sheet, _load(path), at, None, None))


@mcp.tool()
def income_statement(path: str, start: Optional[str] = None, end: Optional[str] = None) -> str:
    """Income statement (revenue/expenses/net) as JSON for an optional ISO date range."""
    from vrledger import reports
    return _json(_call_report(reports.income_statement, _load(path), None, start, end))


@mcp.tool()
def cash_flow_statement(path: str, start: Optional[str] = None, end: Optional[str] = None) -> str:
    """Cash-flow statement as JSON for an optional ISO date range."""
    from vrledger import reports
    return _json(_call_report(reports.cash_flow_statement, _load(path), None, start, end))


@mcp.tool()
def accounts(path: str) -> str:
    """List all account names declared/used in the ledger."""
    return _json(_load(path).accounts())


@mcp.tool()
def balance_of(path: str, account: str) -> str:
    """Balance of a single account (by currency) as JSON."""
    return _json(_load(path).balance_of(account))


if __name__ == "__main__":
    mcp.run()
