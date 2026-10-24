"""INV-01/02/03: public evidence is independent of bank sessions and databases."""

import copy
import json

import pytest
from fastapi.testclient import TestClient
from research_api.app import create_app
from research_api.router import REGISTERED_SOURCES
from research_brief import compare

SOURCE_ID = "msft-ar2025"
SOURCE_PATH = REGISTERED_SOURCES[SOURCE_ID]
COMPARISON_URL = f"/v1/research/sources/{SOURCE_ID}/comparison"


@pytest.fixture
def packet():
    return json.loads(SOURCE_PATH.read_text())


def test_independent_app_exposes_public_report_without_session_or_database(packet):
    with TestClient(create_app()) as client:
        assert client.get("/health/live").json() == {"status": "alive"}
        catalog = client.get("/v1/research/sources")
        assert catalog.status_code == 200
        assert catalog.json() == {
            "sources": [
                {
                    "id": SOURCE_ID,
                    "issuer": packet["issuer"],
                    "title": packet["source"]["title"],
                    "url": packet["source"]["url"],
                    "periods": packet["periods"],
                }
            ]
        }
        response = client.get(COMPARISON_URL)
        assert response.status_code == 200
        result = response.json()
        assert result == compare(packet)
        assert result["metrics"]["revenue"]["growth_pct"]["value"] == "14.93"
        assert result["metrics"]["operating_income"]["growth_pct"]["value"] == "17.45"
        assert result["metrics"]["operating_cash_flow"]["growth_pct"]["value"] == "14.86"
        assert result["operating_margin_change_pp"]["value"] == "0.98"
        assert result["facts"] == packet["facts"]
        assert result["source"]["sha256"] == packet["source"]["sha256"]


def test_missing_fact_remains_a_successful_comparison_with_specific_gaps(tmp_path, packet):
    packet["facts"] = [
        fact for fact in packet["facts"] if fact["id"] != "operating_cash_flow-fy2025"
    ]
    path = tmp_path / "partial.json"
    path.write_text(json.dumps(packet))
    with TestClient(create_app({SOURCE_ID: path})) as client:
        response = client.get(COMPARISON_URL)
        assert response.status_code == 200
        result = response.json()
        assert result["metrics"]["operating_cash_flow"]["actuals"]["FY2025"] is None
        assert result["metrics"]["operating_cash_flow"]["growth_pct"]["value"] is None
        assert result["gaps"] == [
            {"metric": "operating_cash_flow", "period_id": "FY2025", "reason": "missing_fact"}
        ]
        assert result["metrics"]["revenue"]["growth_pct"]["value"] == "14.93"
        assert client.get("/v1/research/sources").status_code == 200


@pytest.mark.parametrize("failure", ["missing", "json", "encoding", "unit", "period", "identity"])
def test_registered_source_failure_is_safe_and_distinct_from_missing_facts(
    tmp_path, packet, failure
):
    path = tmp_path / "private-internal-file.json"
    if failure == "json":
        path.write_text("not json: confidential internal detail")
    elif failure == "encoding":
        path.write_bytes(b"\xff\xfe\x80")
    elif failure != "missing":
        broken = copy.deepcopy(packet)
        if failure == "unit":
            broken["facts"][0]["unit"] = "billion"
        elif failure == "period":
            broken["periods"][0]["end"] = "2024-05-31"
        elif failure == "identity":
            broken["source"]["id"] = "different-report"
            for fact in broken["facts"]:
                fact["source_id"] = "different-report"
        path.write_text(json.dumps(broken))
    with TestClient(create_app({SOURCE_ID: path})) as client:
        for url in (COMPARISON_URL, "/v1/research/sources"):
            response = client.get(url)
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "SOURCE_UNAVAILABLE"
            assert "Retry" in response.json()["error"]["safe_message"]
            assert "private-internal-file" not in response.text
            assert "confidential" not in response.text
            assert "Traceback" not in response.text


def test_unknown_source_cannot_open_an_unregistered_file(tmp_path, packet):
    (tmp_path / "not-registered.json").write_text(json.dumps(packet))
    with TestClient(create_app({})) as client:
        assert client.get("/v1/research/sources").json() == {"sources": []}
        response = client.get("/v1/research/sources/not-registered/comparison")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "SOURCE_NOT_FOUND"


def test_retry_reads_repaired_source_without_restarting(tmp_path, packet):
    path = tmp_path / "pack.json"
    with TestClient(create_app({SOURCE_ID: path})) as client:
        assert client.get(COMPARISON_URL).status_code == 503
        path.write_text(json.dumps(packet))
        assert client.get(COMPARISON_URL).json() == compare(packet)


def test_api_paths_never_fall_through_to_static_frontend(tmp_path):
    (tmp_path / "index.html").write_text("<h1>Research workspace</h1>")
    with TestClient(create_app(static_dir=tmp_path)) as client:
        assert "Research workspace" in client.get("/").text
        response = client.get("/v1/research/not-a-route")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"
        assert client.post(COMPARISON_URL, json={"value": "0"}).status_code == 404
