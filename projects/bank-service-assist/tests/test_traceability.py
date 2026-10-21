"""Requirement traceability stays current and only cites tests that exist."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/build_traceability.py"
spec = importlib.util.spec_from_file_location("build_traceability", SCRIPT)
traceability = importlib.util.module_from_spec(spec)
spec.loader.exec_module(traceability)


def test_every_referenced_test_exists_and_matrix_is_current():
    text, missing = traceability.build()
    assert missing == []
    assert traceability.OUTPUT.read_text() == text


def test_every_requirement_is_listed_with_status():
    text, _ = traceability.build()
    import json

    reqs = json.loads(
        (traceability.PROJECT / "docs/sprint-01/requirements.json").read_text()
    )["requirements"]
    for req in reqs:
        assert "| {} |".format(req["id"]) in text
