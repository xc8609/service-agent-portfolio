"""Small synthetic accounting examples exercise the evidence contract and arithmetic."""

import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from research_brief import ComparisonError, compare


@pytest.fixture
def packet():
    values = {
        "revenue": ("200", "250"),
        "operating_income": ("30", "50"),
        "operating_cash_flow": ("40", "60"),
    }
    return {
        "schema_version": 1,
        "issuer": {"id": "demo", "name": "Synthetic issuer", "cik": "0000000001"},
        "source": {
            "id": "filing-1",
            "title": "Synthetic annual comparison",
            "url": "https://example.com/annual-report",
            "retrieved_at": "2026-10-24T12:00:00Z",
            "sha256": "a" * 64,
        },
        "periods": [
            {"id": "FY24", "start": "2024-01-01", "end": "2024-12-31"},
            {"id": "FY25", "start": "2025-01-01", "end": "2025-12-31"},
        ],
        "facts": [
            {
                "id": "{}-{}".format(metric, period),
                "metric": metric,
                "period_id": period,
                "value": value,
                "currency": "USD",
                "unit": "millions",
                "source_id": "filing-1",
                "locator": "Synthetic table: {} / {}".format(metric, period),
            }
            for metric, pair in values.items()
            for period, value in zip(("FY24", "FY25"), pair)
        ],
    }


def test_calculations_and_provenance_without_mutating_input(packet):
    original = deepcopy(packet)
    result = compare(packet)
    assert packet == original
    assert result["issuer"] == packet["issuer"]
    assert result["source"] == packet["source"]
    assert result["facts"] == packet["facts"]
    revenue = result["metrics"]["revenue"]
    assert revenue["actuals"]["FY25"] == {"value": "250.00", "fact_id": "revenue-FY25"}
    assert revenue["delta"] == {
        "value": "50.00",
        "input_fact_ids": ["revenue-FY24", "revenue-FY25"],
        "reason": None,
    }
    assert revenue["growth_pct"]["value"] == "25.00"
    assert result["metrics"]["operating_income"]["growth_pct"]["value"] == "66.67"
    assert result["metrics"]["operating_cash_flow"]["delta"]["value"] == "20.00"
    assert result["operating_margin_pct"]["FY24"]["value"] == "15.00"
    assert result["operating_margin_pct"]["FY25"]["value"] == "20.00"
    assert result["operating_margin_change_pp"]["value"] == "5.00"
    assert result["operating_margin_change_pp"]["input_fact_ids"] == [
        "revenue-FY24",
        "operating_income-FY24",
        "revenue-FY25",
        "operating_income-FY25",
    ]
    assert result["gaps"] == []
    result["facts"][0]["value"] = "999"
    assert packet == original


def test_half_up_rounding_uses_original_precision(packet):
    packet["facts"][1]["value"] = "250.005"
    result = compare(packet)
    assert result["metrics"]["revenue"]["actuals"]["FY25"]["value"] == "250.01"
    assert result["metrics"]["revenue"]["delta"]["value"] == "50.01"
    assert result["metrics"]["revenue"]["growth_pct"]["value"] == "25.00"


def test_reverse_period_and_fact_order_preserves_meaning(packet):
    expected = compare(packet)
    packet["periods"].reverse()
    packet["facts"].reverse()
    result = compare(packet)
    for key in ("periods", "metrics", "operating_margin_pct", "operating_margin_change_pp"):
        assert result[key] == expected[key]


def test_fiscal_year_start_is_allowed(packet):
    packet["periods"] = [
        {"id": "FY24", "start": "2023-07-01", "end": "2024-06-30"},
        {"id": "FY25", "start": "2024-07-01", "end": "2025-06-30"},
    ]
    assert compare(packet)["metrics"]["revenue"]["growth_pct"]["value"] == "25.00"


def test_missing_fact_keeps_known_actual_and_marks_derived_unavailable(packet):
    packet["facts"] = [fact for fact in packet["facts"] if fact["id"] != "revenue-FY24"]
    result = compare(packet)
    revenue = result["metrics"]["revenue"]
    assert revenue["actuals"]["FY24"] is None
    assert revenue["actuals"]["FY25"]["value"] == "250.00"
    assert revenue["delta"]["value"] is None
    assert revenue["growth_pct"]["reason"] == "missing_fact"
    assert result["gaps"] == [{"metric": "revenue", "period_id": "FY24", "reason": "missing_fact"}]
    assert result["operating_margin_pct"]["FY25"]["value"] == "20.00"
    assert result["operating_margin_change_pp"]["value"] is None


@pytest.mark.parametrize("prior", ["0", "-10"])
def test_non_positive_prior_is_not_a_growth_percentage(packet, prior):
    packet["facts"][2]["value"] = prior
    result = compare(packet)
    income = result["metrics"]["operating_income"]
    assert income["actuals"]["FY24"]["value"] == "{}.00".format(prior)
    assert income["delta"]["value"] == ("50.00" if prior == "0" else "60.00")
    assert income["growth_pct"]["value"] is None
    assert income["growth_pct"]["reason"] == "non_positive_prior"
    assert result["operating_margin_pct"]["FY24"]["value"] == ("0.00" if prior == "0" else "-5.00")


@pytest.mark.parametrize("revenue", ["0", "-200"])
def test_non_positive_revenue_cannot_supply_operating_margin(packet, revenue):
    packet["facts"][0]["value"] = revenue
    result = compare(packet)
    assert result["operating_margin_pct"]["FY24"]["reason"] == "non_positive_revenue"
    assert result["operating_margin_change_pp"]["value"] is None


@pytest.mark.parametrize("field,value", [("currency", "CAD"), ("unit", "thousands")])
def test_mismatched_currency_or_scale_rejected(packet, field, value):
    packet["facts"][1][field] = value
    with pytest.raises(ComparisonError, match="matching currency and unit"):
        compare(packet)


@pytest.mark.parametrize("same_id", [True, False])
def test_duplicate_fact_and_metric_period_rejected(packet, same_id):
    duplicate = dict(packet["facts"][0])
    if not same_id:
        duplicate["id"] = "another-id"
    packet["facts"].append(duplicate)
    with pytest.raises(ComparisonError, match="duplicate fact id|duplicate metric-period"):
        compare(packet)


@pytest.mark.parametrize(
    "value", ["NaN", "Infinity", "-Infinity", "1e3", "1_000", " 12", "12 ", "", 12.5, True]
)
def test_malformed_values_rejected(packet, value):
    packet["facts"][0]["value"] = value
    with pytest.raises(ComparisonError):
        compare(packet)


@pytest.mark.parametrize(
    "field,value", [("source_id", "unknown"), ("period_id", "FY99"), ("metric", "ebitda")]
)
def test_unknown_fact_references_rejected(packet, field, value):
    packet["facts"][0][field] = value
    with pytest.raises(ComparisonError, match="unknown|unsupported"):
        compare(packet)


@pytest.mark.parametrize(
    "change", ["quarter", "gap", "overlap", "duplicate", "invalid_date", "short_year"]
)
def test_incompatible_periods_rejected(packet, change):
    if change == "quarter":
        packet["periods"][0]["end"] = "2024-03-31"
    elif change == "gap":
        packet["periods"][1].update(start="2026-01-01", end="2026-12-31")
    elif change == "overlap":
        packet["periods"][1].update(start="2024-07-01", end="2025-06-30")
    elif change == "duplicate":
        packet["periods"][1]["id"] = "FY24"
    elif change == "invalid_date":
        packet["periods"][0]["start"] = "2024-13-01"
    else:
        packet["periods"][0]["end"] = "2024-12-30"
    with pytest.raises(ComparisonError):
        compare(packet)


@pytest.mark.parametrize(
    "key,value",
    [
        ("url", "not-a-url"),
        ("url", "http://example.com/annual-report"),
        ("sha256", "abc"),
        ("retrieved_at", "2026-10-24"),
    ],
)
def test_malformed_source_metadata_rejected(packet, key, value):
    packet["source"][key] = value
    with pytest.raises(ComparisonError):
        compare(packet)


def test_empty_evidence_reports_gaps(packet):
    packet["facts"] = []
    result = compare(packet)
    assert len(result["gaps"]) == 6
    assert result["unit"] is None
    assert result["metrics"]["revenue"]["actuals"] == {"FY24": None, "FY25": None}


def test_reviewed_microsoft_annual_example_matches_expected_comparison():
    path = Path(__file__).resolve().parents[1] / "examples" / "msft-fy2025.json"
    packet = json.loads(path.read_text(encoding="utf-8"))
    result = compare(packet)
    for metric, expected in (
        ("revenue", "14.93"),
        ("operating_income", "17.45"),
        ("operating_cash_flow", "14.86"),
    ):
        growth = result["metrics"][metric]["growth_pct"]
        assert growth["value"] == expected
        assert growth["input_fact_ids"] == [metric + "-fy2024", metric + "-fy2025"]
    assert result["operating_margin_pct"]["FY2024"]["value"] == "44.64"
    assert result["operating_margin_pct"]["FY2025"]["value"] == "45.62"
    assert result["operating_margin_change_pp"] == {
        "value": "0.98",
        "input_fact_ids": [
            "revenue-fy2024",
            "operating_income-fy2024",
            "revenue-fy2025",
            "operating_income-fy2025",
        ],
        "reason": None,
    }
    assert result["source"] == packet["source"]
    assert result["source"]["url"] == "https://www.microsoft.com/investor/reports/ar25/index.html"
    assert all(fact["source_id"] == "msft-ar2025" and fact["locator"] for fact in result["facts"])
    assert result["gaps"] == []


def run_cli(path):
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
    return subprocess.run(
        [sys.executable, "-m", "research_brief", str(path)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_outputs_json(packet, tmp_path):
    path = tmp_path / "packet.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    result = run_cli(path)
    assert result.returncode == 0
    assert json.loads(result.stdout)["metrics"]["revenue"]["growth_pct"]["value"] == "25.00"
    assert result.stderr == ""


@pytest.mark.parametrize("content", ["not-json", "[]", '{"schema_version": 1}'])
def test_cli_invalid_input_has_clear_error_without_traceback(tmp_path, content):
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    result = run_cli(path)
    assert result.returncode == 2
    assert result.stderr.startswith("research_brief: ")
    assert "Traceback" not in result.stderr
    assert result.stdout == ""


def test_cli_missing_file_has_clear_error(tmp_path):
    result = run_cli(tmp_path / "missing.json")
    assert result.returncode == 2
    assert "research_brief: " in result.stderr
    assert "Traceback" not in result.stderr
