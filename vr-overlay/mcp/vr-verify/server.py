"""
VRAGENT vr-verify MCP server.

Deterministic verification primitives for financial work — NO LLM, pure Decimal
arithmetic. Every tool is a recompute-from-scratch check the agent can trust:
balance a journal entry, tie report numbers, foot a column, re-derive
depreciation / loan amortization / the retained-earnings roll. Same inputs ->
same answer, to the cent. Pure in-process — no external service.

Registered in config.yaml under mcp_servers.vr-verify. Runs over stdio.
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vr-verify")

CENT = Decimal("0.01")


def _D(x) -> Decimal:
    """Coerce anything (int/float/str/None) to Decimal without binary-float drift."""
    if x is None or x == "":
        return Decimal("0")
    if isinstance(x, Decimal):
        return x
    try:
        return Decimal(str(x))
    except (InvalidOperation, ValueError):
        raise ValueError(f"not a number: {x!r}")


def _money(d: Decimal) -> str:
    """Round half-up to the cent and render as a plain string (JSON-safe)."""
    return str(d.quantize(CENT, rounding=ROUND_HALF_UP))


def _json(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


def _loads(s: str, what: str):
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(f"{what} must be a JSON string: {e}")


@mcp.tool()
def check_balanced(je_json: str) -> str:
    """Check a journal entry balances (debits == credits).

    je_json: JSON array of lines, each {account, debit, credit}; omitted/blank
    debit or credit counts as 0. Returns balanced (bool), total_debits,
    total_credits, and variance (debits - credits) to the cent.
    """
    lines = _loads(je_json, "je_json")
    if not isinstance(lines, list):
        raise ValueError("je_json must be a JSON array of lines")
    tot_dr = Decimal("0")
    tot_cr = Decimal("0")
    for i, ln in enumerate(lines):
        if not isinstance(ln, dict):
            raise ValueError(f"line {i} is not an object")
        tot_dr += _D(ln.get("debit"))
        tot_cr += _D(ln.get("credit"))
    variance = (tot_dr - tot_cr).quantize(CENT, rounding=ROUND_HALF_UP)
    return _json({
        "balanced": variance == Decimal("0.00"),
        "total_debits": _money(tot_dr),
        "total_credits": _money(tot_cr),
        "variance": _money(variance),
        "lines": len(lines),
    })


@mcp.tool()
def check_ties(spec_json: str) -> str:
    """Tie out expected vs actual figures.

    spec_json: JSON array of {name, expected, actual}. Returns per-tie pass
    (bool) + variance (expected - actual) to the cent, and overall ok (bool).
    """
    spec = _loads(spec_json, "spec_json")
    if not isinstance(spec, list):
        raise ValueError("spec_json must be a JSON array")
    results = []
    overall = True
    for i, t in enumerate(spec):
        if not isinstance(t, dict):
            raise ValueError(f"tie {i} is not an object")
        exp = _D(t.get("expected"))
        act = _D(t.get("actual"))
        var = (exp - act).quantize(CENT, rounding=ROUND_HALF_UP)
        passed = var == Decimal("0.00")
        overall = overall and passed
        results.append({
            "name": t.get("name", f"tie_{i}"),
            "expected": _money(exp),
            "actual": _money(act),
            "variance": _money(var),
            "pass": passed,
        })
    return _json({"ok": overall, "ties": results})


@mcp.tool()
def foot(rows_json: str) -> str:
    """Foot (sum) a column of numbers.

    rows_json: JSON array of numbers (ints/floats/numeric strings). Returns the
    Decimal sum to the cent and the count of rows.
    """
    rows = _loads(rows_json, "rows_json")
    if not isinstance(rows, list):
        raise ValueError("rows_json must be a JSON array of numbers")
    total = Decimal("0")
    for i, r in enumerate(rows):
        try:
            total += _D(r)
        except ValueError:
            raise ValueError(f"row {i} is not a number: {r!r}")
    return _json({"sum": _money(total), "rows": len(rows)})


@mcp.tool()
def recompute_depreciation(
    method: str,
    basis: str,
    life_years: int,
    salvage: str = "0",
    period: int = 1,
) -> str:
    """Recompute a period's depreciation expense and accumulated to-date.

    method: 'SL' (straight-line) or 'DDB' (double-declining-balance).
    basis: depreciable asset cost. salvage: residual value (floor; not depreciated
    below). life_years: useful life. period: 1-based period to report.
    DDB switches to straight-line on the remaining balance when that yields a
    larger deduction (standard convention) and never depreciates below salvage.
    """
    m = method.strip().upper()
    if m not in {"SL", "DDB"}:
        raise ValueError("method must be 'SL' or 'DDB'")
    cost = _D(basis)
    salv = _D(salvage)
    if life_years <= 0:
        raise ValueError("life_years must be > 0")
    if period < 1:
        raise ValueError("period must be >= 1")
    depreciable = cost - salv

    if m == "SL":
        annual = depreciable / Decimal(life_years)
        expense = annual if period <= life_years else Decimal("0")
        accum = annual * Decimal(min(period, life_years))
        # Clamp accumulated to the depreciable base.
        if accum > depreciable:
            accum = depreciable
    else:  # DDB
        rate = Decimal("2") / Decimal(life_years)
        book = cost
        accum = Decimal("0")
        expense = Decimal("0")
        for p in range(1, period + 1):
            remaining_life = life_years - (p - 1)
            ddb_amt = book * rate
            sl_amt = (book - salv) / Decimal(remaining_life) if remaining_life > 0 else Decimal("0")
            amt = max(ddb_amt, sl_amt)
            # never depreciate below salvage
            if book - amt < salv:
                amt = book - salv
            if amt < 0:
                amt = Decimal("0")
            book -= amt
            accum += amt
            if p == period:
                expense = amt

    return _json({
        "method": m,
        "period": period,
        "depreciation_expense": _money(expense),
        "accumulated_to_date": _money(accum),
        "book_value_end": _money(cost - accum),
    })


@mcp.tool()
def recompute_loan_payment(
    principal: str,
    annual_rate: str,
    term_months: int,
    payment_no: int,
) -> str:
    """Recompute a single amortized loan payment's principal/interest split.

    Standard fixed-payment (level) amortization. principal: original balance.
    annual_rate: nominal annual rate as a decimal (0.06 = 6%) OR percent (6 ->
    treated as 6%); monthly rate = annual/12. term_months: total payments.
    payment_no: 1-based payment to report. Returns payment, interest, principal,
    and remaining balance after that payment.
    """
    bal = _D(principal)
    rate = _D(annual_rate)
    if rate >= 1:  # caller passed a percent like 6 instead of 0.06
        rate = rate / Decimal("100")
    if term_months <= 0:
        raise ValueError("term_months must be > 0")
    if not (1 <= payment_no <= term_months):
        raise ValueError("payment_no must be in 1..term_months")

    i = rate / Decimal("12")
    if i == 0:
        payment = bal / Decimal(term_months)
    else:
        factor = (Decimal("1") + i) ** term_months
        payment = bal * (i * factor) / (factor - Decimal("1"))

    int_part = Decimal("0")
    prin_part = Decimal("0")
    for p in range(1, payment_no + 1):
        int_part = (bal * i).quantize(CENT, rounding=ROUND_HALF_UP)
        prin_part = payment.quantize(CENT, rounding=ROUND_HALF_UP) - int_part
        # final payment soaks up rounding to clear the balance
        if p == term_months or prin_part > bal:
            prin_part = bal
        bal = bal - prin_part

    pay_total = (int_part + prin_part)
    return _json({
        "payment_no": payment_no,
        "scheduled_payment": _money(payment),
        "payment_applied": _money(pay_total),
        "interest": _money(int_part),
        "principal": _money(prin_part),
        "remaining_balance": _money(bal),
    })


@mcp.tool()
def reroll_retained_earnings(
    beginning: str,
    net_income: str,
    distributions: str = "0",
    other: str = "0",
) -> str:
    """Re-roll retained earnings: beginning + net_income - distributions + other.

    distributions is subtracted (dividends/draws). other is added (e.g. prior-
    period adjustments; pass a negative for a reduction). Returns ending RE and
    the full roll-forward.
    """
    beg = _D(beginning)
    ni = _D(net_income)
    dist = _D(distributions)
    oth = _D(other)
    ending = beg + ni - dist + oth
    return _json({
        "beginning": _money(beg),
        "net_income": _money(ni),
        "distributions": _money(dist),
        "other": _money(oth),
        "ending": _money(ending),
        "roll": f"{_money(beg)} + {_money(ni)} - {_money(dist)} + {_money(oth)} = {_money(ending)}",
    })


if __name__ == "__main__":
    mcp.run()
