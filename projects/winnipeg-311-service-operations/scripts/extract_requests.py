"""Extract Water and Waste 311 service requests and API control counts; keep records local."""

import csv
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DATASET = "u7f6-5326"
SOURCE_PAGE = "https://data.winnipeg.ca/Contact-Centre-311/311-Requests/" + DATASET
API = "https://data.winnipeg.ca/resource/" + DATASET
WINDOW_START = "2023-01-01T00:00:00"
SNAPSHOT_CUTOFF = "2026-11-01T00:00:00"
COLUMNS = [
    "case_id",
    "interaction_id",
    "channel_type",
    "subject",
    "reason",
    "type",
    "open_date",
    "closed_date",
    "case_status",
    "neighbourhood",
    "ward",
]
SCOPE = (
    "subject='Service Request' AND reason='Water and Waste' "
    f"AND open_date >= '{WINDOW_START}' AND open_date < '{SNAPSHOT_CUTOFF}'"
)
FOLLOW_UP = (
    "type in ('Follow Up Call- SLA not breached', 'Follow up- SLA breached') "
    f"AND open_date >= '{WINDOW_START}' AND open_date < '{SNAPSHOT_CUTOFF}'"
)
PAGE = 50000


def fetch(endpoint, params, attempts=4):
    url = endpoint + "?" + urlencode(params)
    for attempt in range(attempts):
        try:
            with urlopen(url, timeout=300) as response:
                return response.read().decode("utf-8")
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(5 * (attempt + 1))


def query_json(soql):
    return json.loads(fetch(API + ".json", {"$query": soql}))


def main():
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()
    controls = query_json(
        f"SELECT type, count(*) AS rows WHERE {SCOPE} GROUP BY type ORDER BY type LIMIT 1000"
    )
    expected = sum(int(item["rows"]) for item in controls)

    destination = raw / "water_waste_service_requests.csv"
    temporary = destination.with_suffix(".tmp")
    written = 0
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(COLUMNS)
        offset = 0
        while True:
            text = fetch(
                API + ".csv",
                {
                    "$select": ",".join(COLUMNS),
                    "$where": SCOPE,
                    "$order": ":id",
                    "$limit": PAGE,
                    "$offset": offset,
                },
            )
            reader = csv.reader(io.StringIO(text))
            if next(reader) != COLUMNS:
                raise ValueError("Unexpected CSV columns from the API")
            batch = list(reader)
            writer.writerows(batch)
            written += len(batch)
            print(f"rows {written:,} / {expected:,}", flush=True)
            if len(batch) < PAGE:
                break
            offset += PAGE
    if written != expected:
        temporary.unlink()
        raise ValueError(f"Extract has {written} rows; API control count is {expected}")
    temporary.replace(destination)

    follow_ups = query_json(
        "SELECT date_trunc_ym(open_date) AS month, type, count(*) AS rows "
        f"WHERE {FOLLOW_UP} GROUP BY month, type ORDER BY month, type LIMIT 1000"
    )
    (raw / "follow_up_calls_monthly.json").write_text(json.dumps(follow_ups, indent=2) + "\n")
    older_open = query_json(
        "SELECT count(*) AS rows WHERE subject='Service Request' AND reason='Water and Waste' "
        f"AND case_status='Open' AND open_date < '{WINDOW_START}'"
    )[0]["rows"]
    metadata = json.loads(fetch("https://data.winnipeg.ca/api/views/" + DATASET + ".json", {}))

    manifest = {
        "dataset": metadata["name"],
        "dataset_id": DATASET,
        "publisher": "City of Winnipeg",
        "source_page": SOURCE_PAGE,
        "licence_portal_field": metadata["metadata"]["custom_fields"]["Licence"]["Licence"],
        "licence_api_id": metadata.get("licenseId"),
        "rows_updated_at_utc": datetime.fromtimestamp(
            metadata["rowsUpdatedAt"], timezone.utc
        ).isoformat(),
        "retrieved_at_utc": retrieved_at,
        "scope_where": SCOPE,
        "snapshot_cutoff_local": SNAPSHOT_CUTOFF,
        "columns": COLUMNS,
        "rows": written,
        "csv_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "api_rows_by_type": {item["type"]: int(item["rows"]) for item in controls},
        "follow_up_rows": sum(int(item["rows"]) for item in follow_ups),
        "open_service_requests_opened_before_window": int(older_open),
    }
    (ROOT / "data/source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({key: manifest[key] for key in ("rows", "csv_sha256", "follow_up_rows")}))


if __name__ == "__main__":
    main()
