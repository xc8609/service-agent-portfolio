"""Synthetic edge cases supplement (but do not replace) actual archive checks."""
from pathlib import Path

import pytest

duckdb = pytest.importorskip("duckdb", reason="Install projects/complaint-analytics/requirements.txt for SQL checks")
PROJECT = Path(__file__).resolve().parents[1]
COLUMNS = ["Complaint ID", "Date received", "Date sent to company", "Product",
           "Sub-product", "Issue", "Sub-issue", "Consumer complaint narrative",
           "Company public response", "Company", "State", "Submitted via",
           "Company response to consumer", "Timely response?", "Tags"]


@pytest.mark.parametrize("text,expected", [(None, False), ("   ", False), ("Synthetic test complaint", True)])
def test_staging_preserves_invalid_values_as_visible_nulls(text, expected):
    with duckdb.connect() as con:
        con.execute('CREATE TABLE raw_complaints (' + ','.join('"' + col + '" VARCHAR' for col in COLUMNS) + ')')
        record = {"Complaint ID": "bad-id", "Date received": "bad-date",
                  "Date sent to company": "2026-07-10", "Consumer complaint narrative": text,
                  "Timely response?": "Unknown"}
        con.execute('INSERT INTO raw_complaints VALUES (' + ','.join('?' for _ in COLUMNS) + ')',
                    [record.get(col) for col in COLUMNS])
        con.execute((PROJECT / "sql/02_staging.sql").read_text())
        assert con.execute('SELECT complaint_id, date_received, is_timely, has_narrative FROM stg_complaints').fetchone() == (None, None, None, expected)
