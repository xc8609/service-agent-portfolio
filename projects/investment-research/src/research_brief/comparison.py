"""Validate cited annual facts and compute reproducible, source-linked changes."""

import re
from copy import deepcopy
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, localcontext
from urllib.parse import urlparse

METRICS = ("revenue", "operating_income", "operating_cash_flow")
DECIMAL_STRING = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z")


class ComparisonError(ValueError):
    """The evidence packet cannot support a coherent annual comparison."""


def _object(value, label):
    if not isinstance(value, dict):
        raise ComparisonError("{} must be an object".format(label))
    return value


def _text(record, key):
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ComparisonError("{} must be a non-empty string".format(key))
    return value


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ComparisonError("period dates must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ComparisonError("invalid period date: {}".format(value)) from exc


def _periods(packet):
    periods = packet.get("periods")
    if not isinstance(periods, list) or len(periods) != 2:
        raise ComparisonError("exactly two annual periods are required")
    identifiers = set()
    parsed = []
    for raw in periods:
        period = _object(raw, "period")
        identifier = _text(period, "id")
        if identifier in identifiers:
            raise ComparisonError("duplicate period id: {}".format(identifier))
        identifiers.add(identifier)
        start, end = _date(period.get("start")), _date(period.get("end"))
        try:
            anniversary = start.replace(year=start.year + 1)
        except ValueError as exc:
            raise ComparisonError("annual start must have a next-year anniversary") from exc
        if end != anniversary - timedelta(days=1):
            raise ComparisonError("period must cover one complete calendar year (inclusive)")
        parsed.append((start, end, period))
    parsed.sort(key=lambda item: item[0])
    if parsed[1][0] != parsed[0][1] + timedelta(days=1):
        raise ComparisonError("annual periods must be consecutive and non-overlapping")
    return [item[2] for item in parsed]


def _validate(packet):
    _object(packet, "packet")
    if type(packet.get("schema_version")) is not int or packet["schema_version"] != 1:
        raise ComparisonError("schema_version must be 1")
    issuer = _object(packet.get("issuer"), "issuer")
    for key in ("id", "name", "cik"):
        _text(issuer, key)
    source = _object(packet.get("source"), "source")
    for key in ("id", "title", "url", "retrieved_at", "sha256"):
        _text(source, key)
    url = urlparse(source["url"])
    if url.scheme != "https" or not url.netloc:
        raise ComparisonError("source url must be an HTTPS URL")
    if not re.fullmatch(r"[a-fA-F0-9]{64}", source["sha256"]):
        raise ComparisonError("source sha256 must contain 64 hexadecimal characters")
    try:
        retrieved = datetime.fromisoformat(source["retrieved_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ComparisonError("retrieved_at must be an ISO timestamp") from exc
    if retrieved.tzinfo is None:
        raise ComparisonError("retrieved_at must include a timezone")
    periods = _periods(packet)
    period_ids = {period["id"] for period in periods}
    facts = packet.get("facts")
    if not isinstance(facts, list):
        raise ComparisonError("facts must be a list")
    seen_ids, indexed, basis = set(), {}, None
    for raw in facts:
        fact = _object(raw, "fact")
        for key in (
            "id",
            "metric",
            "period_id",
            "value",
            "currency",
            "unit",
            "source_id",
            "locator",
        ):
            _text(fact, key)
        identifier = fact["id"]
        if identifier in seen_ids:
            raise ComparisonError("duplicate fact id: {}".format(identifier))
        seen_ids.add(identifier)
        if fact["source_id"] != source["id"]:
            raise ComparisonError("unknown source_id: {}".format(fact["source_id"]))
        if fact["period_id"] not in period_ids:
            raise ComparisonError("unknown period_id: {}".format(fact["period_id"]))
        if fact["metric"] not in METRICS:
            raise ComparisonError("unsupported metric: {}".format(fact["metric"]))
        key = (fact["metric"], fact["period_id"])
        if key in indexed:
            raise ComparisonError("duplicate metric-period: {} / {}".format(*key))
        if not DECIMAL_STRING.fullmatch(fact["value"]):
            raise ComparisonError("fact value must be a finite plain decimal string")
        fact_basis = (fact["currency"], fact["unit"])
        if basis is not None and basis != fact_basis:
            raise ComparisonError("facts must use matching currency and unit")
        basis = fact_basis
        indexed[key] = fact
    return periods, indexed, basis


def _rounded(value):
    rounded = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(rounded.copy_abs() if rounded == 0 else rounded, "f")


def _derived(value, facts, reason=None):
    return {
        "value": None if value is None else _rounded(value),
        "input_fact_ids": [fact["id"] for fact in facts if fact is not None],
        "reason": reason,
    }


def compare(packet):
    """Return facts, derived values and explicit gaps without filling missing data."""
    periods, indexed, basis = _validate(packet)
    prior, current = (period["id"] for period in periods)
    result = {
        "schema_version": 1,
        "issuer": deepcopy(packet["issuer"]),
        "source": deepcopy(packet["source"]),
        "periods": deepcopy(periods),
        "facts": deepcopy(packet["facts"]),
        "currency": basis[0] if basis else None,
        "unit": basis[1] if basis else None,
        "metrics": {},
        "operating_margin_pct": {},
        "gaps": [],
    }
    with localcontext() as context:
        context.prec = max([28] + [len(fact["value"]) * 2 + 12 for fact in indexed.values()])
        for metric in METRICS:
            pair = [indexed.get((metric, period)) for period in (prior, current)]
            actuals = {}
            for period, fact in zip((prior, current), pair):
                actuals[period] = (
                    None
                    if fact is None
                    else {"value": _rounded(Decimal(fact["value"])), "fact_id": fact["id"]}
                )
                if fact is None:
                    result["gaps"].append(
                        {"metric": metric, "period_id": period, "reason": "missing_fact"}
                    )
            delta = growth = None
            delta_reason = growth_reason = "missing_fact"
            if all(fact is not None for fact in pair):
                before, after = (Decimal(fact["value"]) for fact in pair)
                delta = after - before
                delta_reason = None
                growth_reason = "non_positive_prior" if before <= 0 else None
                if before > 0:
                    growth = delta / before * 100
            result["metrics"][metric] = {
                "actuals": actuals,
                "delta": _derived(delta, pair, delta_reason),
                "growth_pct": _derived(growth, pair, growth_reason),
            }
        margins = []
        margin_facts = []
        for period in (prior, current):
            revenue = indexed.get(("revenue", period))
            income = indexed.get(("operating_income", period))
            pair = [revenue, income]
            margin_facts.extend(pair)
            value, reason = None, "missing_fact"
            if revenue is not None and income is not None:
                denominator = Decimal(revenue["value"])
                reason = "non_positive_revenue" if denominator <= 0 else None
                if denominator > 0:
                    value = Decimal(income["value"]) / denominator * 100
            margins.append(value)
            result["operating_margin_pct"][period] = _derived(value, pair, reason)
        available = all(value is not None for value in margins)
        result["operating_margin_change_pp"] = _derived(
            margins[1] - margins[0] if available else None,
            margin_facts,
            None if available else "unavailable_operating_margin",
        )
    return result
