import copy
import json
from pathlib import Path

import pytest
from bank_api.integrations.transactions import SourceContractError, normalize_transactions

EXAMPLES = Path(__file__).resolve().parents[3] / "examples/integrations"
OBSERVED = "2026-10-20T16:00:00Z"


def fixture(name="legacy-export"):
    return json.loads((EXAMPLES / (name + ".json")).read_text())


def normalize(f):
    return normalize_transactions(f["records"], f["mapping"], f["accounts"], OBSERVED)


def test_different_source_shapes_preserve_business_meaning_and_namespace():
    a, b = normalize(fixture())[0], normalize(fixture("api-export"))[0]
    assert a["id"] != b["id"]  # Equal source keys from different sources never collide.
    for field in ("account_id", "amount_minor", "currency", "status", "occurred_at", "posted_at"):
        assert a[field] == b[field]
    assert a["amount_minor"] == 4999
    assert a["occurred_at"] == "2026-10-19T15:00:00+00:00"
    assert normalize(fixture())[0] == a  # Stable IDs and normalized facts on replay.
    f = fixture()
    f["records"][0]["CardNumber"] = "DO_NOT_PROJECT_PRIVATE_SOURCE_FIELDS"
    assert normalize(f)[0] == a


@pytest.mark.parametrize(
    "column,value",
    [
        ("AccountNo", "unknown-account"),
        ("Revision", True),
        ("Revision", 0),
        ("Amount", 49.99),
        ("Amount", "49.991"),
        ("Amount", "49.990000000000000000000000000000001"),
        ("Amount", "NaN"),
        ("Amount", "1e100"),
        ("Currency", "UNKNOWN"),
        ("BookingCode", "UNKNOWN"),
        ("EventTime", "2026-10-19T10:00:00"),
        ("ChangedTime", "2026-10-20T17:00:00Z"),
        ("Descriptor", ""),
    ],
)
def test_ambiguous_source_facts_reject_the_whole_batch(column, value):
    f = fixture()
    invalid = copy.deepcopy(f["records"][0])
    invalid["EntryNo"] = "synthetic-entry-2"
    invalid[column] = value
    f["records"].append(invalid)
    with pytest.raises(SourceContractError, match="^SOURCE_CONTRACT_REJECTED$"):
        normalize(f)


def test_no_silent_dedup_rounding_or_sign_change():
    f = fixture()
    f["records"].append(copy.deepcopy(f["records"][0]))
    with pytest.raises(SourceContractError):
        normalize(f)
    f["records"].pop()
    f["records"][0]["Amount"] = "-49.99"
    assert normalize(f)[0]["amount_minor"] == -4999
    f["mapping"]["currency_exponents"]["CAD"] = 0
    with pytest.raises(SourceContractError):
        normalize(f)
    f["mapping"]["currency_exponents"]["CAD"] = 2
    f["records"][0]["BookingCode"] = "AUTH"
    f["records"][0]["BookingTime"] = None
    assert normalize(f)[0]["posted_at"] is None
