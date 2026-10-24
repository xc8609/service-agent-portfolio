"""INV-04: scoped drafts through the standalone application, without a model API."""

import json

import pytest
from fastapi.testclient import TestClient
from research_api.app import create_app
from research_api.router import REGISTERED_PASSAGES, REGISTERED_SOURCES

SOURCE_ID = "msft-ar2025"
PACK = json.loads(REGISTERED_SOURCES[SOURCE_ID].read_text())


def request_body(**changes):
    return {
        "source_id": SOURCE_ID,
        "question": "What changed in operating cash flow?",
        "expected_source_hash": PACK["source"]["sha256"],
        **changes,
    }


def test_actual_offline_run_reads_evidence_and_returns_cited_cash_flow_draft():
    with TestClient(create_app()) as client:
        response = client.post("/v1/research/runs", json=request_body())
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "draft"
        assert result["question"] == request_body()["question"]
        assert result["source_id"] == SOURCE_ID
        assert result["source_hash"] == PACK["source"]["sha256"]
        assert result["provider"] == "offline-scripted-v1"
        assert [step["tool"] for step in result["trace"]] == [
            "list_sources",
            "read_facts",
            "compare_periods",
            "read_passages",
        ]
        assert all(step["status"] == "ok" for step in result["trace"])
        assert "14.86" in json.dumps(result["findings"])
        assert any(finding["kind"] == "reported_explanation" for finding in result["findings"])
        for finding in result["findings"]:
            assert finding["citations"]
            for citation in finding["citations"]:
                assert citation["id"] and citation["locator"]
                assert citation["url"] == PACK["source"]["url"]
        assert result["issues"] == []


def test_unknown_source_and_stale_report_do_not_generate_drafts():
    with TestClient(create_app()) as client:
        unknown = client.post("/v1/research/runs", json=request_body(source_id="not-registered"))
        assert unknown.status_code == 404
        stale = client.post("/v1/research/runs", json=request_body(expected_source_hash="0" * 64))
        assert stale.status_code == 409
        assert stale.json()["error"]["code"] == "SOURCE_CHANGED"


@pytest.mark.parametrize(
    "changes",
    [
        {"question": "   "},
        {"question": "x" * 1001},
        {"expected_source_hash": "not-a-source-hash"},
        {"provider": "live-api"},
        {"max_tool_calls": 9999},
    ],
)
def test_invalid_or_runtime_control_fields_are_rejected(changes):
    with TestClient(create_app()) as client:
        assert client.post("/v1/research/runs", json=request_body(**changes)).status_code == 422


def test_missing_registered_passages_leave_questions_without_invented_explanations():
    with TestClient(create_app(passages={})) as client:
        result = client.post("/v1/research/runs", json=request_body()).json()
        assert result["status"] == "draft"
        assert result["open_questions"]
        assert not any(item["kind"] == "reported_explanation" for item in result["findings"])
        assert "14.86" in json.dumps(result["findings"])


def test_unreadable_registered_passage_file_is_recoverable_without_affecting_manual_path(tmp_path):
    path = tmp_path / "passages.json"
    path.write_text("invalid json")
    with TestClient(create_app(passages={SOURCE_ID: path})) as client:
        assert client.post("/v1/research/runs", json=request_body()).status_code == 503
        assert client.get(f"/v1/research/sources/{SOURCE_ID}/comparison").status_code == 200
        path.write_text(REGISTERED_PASSAGES[SOURCE_ID].read_text())
        assert client.post("/v1/research/runs", json=request_body()).json()["status"] == "draft"


def test_provider_failure_returns_incomplete_and_manual_lookup_remains_available():
    class FailedProvider:
        name = "failed-test-provider"

        def next_step(self, question, history):
            raise RuntimeError("internal-provider-detail")

    with TestClient(create_app(provider=FailedProvider())) as client:
        response = client.post("/v1/research/runs", json=request_body())
        assert response.status_code == 200
        assert response.json()["status"] == "incomplete"
        assert response.json()["issues"]
        assert "internal-provider-detail" not in response.text
        assert client.get(f"/v1/research/sources/{SOURCE_ID}/comparison").status_code == 200


def test_wrong_passage_source_hash_does_not_produce_a_mixed_source_brief(tmp_path):
    data = json.loads(REGISTERED_PASSAGES[SOURCE_ID].read_text())
    data["source_sha256"] = "0" * 64
    path = tmp_path / "changed-passages.json"
    path.write_text(json.dumps(data))
    with TestClient(create_app(passages={SOURCE_ID: path})) as client:
        response = client.post(
            "/v1/research/runs", json=request_body(question="  Compare revenue.  ")
        )
        assert response.status_code == 200
        assert response.json()["status"] == "incomplete"
        assert response.json()["question"] == "Compare revenue."
        assert response.json()["source_id"] == SOURCE_ID
        assert response.json()["source_hash"] == PACK["source"]["sha256"]
        assert response.json()["issues"][0]["code"] == "INVALID_EVIDENCE"
        assert not response.json()["findings"]
