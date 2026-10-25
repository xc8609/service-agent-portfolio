"""Download the attributed source and extract it without changing the workbook."""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
URL = "https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip"
HEADERS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]
COLUMNS = [
    "invoice",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "price",
    "customer_id",
    "country",
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    raw = ROOT / "data/raw"
    processed = ROOT / "data/processed"
    raw.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    archive = raw / "online-retail-ii.zip"
    manifest_path = ROOT / "data/source-manifest.json"
    expected = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    if not archive.exists():
        with urlopen(URL, timeout=120) as response:
            archive.write_bytes(response.read())
    archive_hash = digest(archive)
    if expected and expected["archive_sha256"] != archive_hash:
        raise ValueError("Source archive changed; inspect before replacing the recorded snapshot.")
    workbook_path = raw / "online_retail_II.xlsx"
    with ZipFile(archive) as archive_file:
        workbook_path.write_bytes(archive_file.read("online_retail_II.xlsx"))
    workbook = openpyxl.load_workbook(workbook_path, read_only=True, data_only=True)
    sheets = []
    destination = processed / "lines.csv"
    temporary = destination.with_suffix(".tmp")
    try:
        with temporary.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["source_sheet", "source_row"] + COLUMNS)
            for sheet in workbook:
                values = iter(sheet.values)
                if list(next(values)) != HEADERS:
                    raise ValueError("Unexpected source headers in " + sheet.title)
                count = 0
                for row_number, row in enumerate(values, start=2):
                    row = [
                        value.isoformat(sep=" ") if isinstance(value, datetime) else value
                        for value in row
                    ]
                    writer.writerow([sheet.title, row_number] + row)
                    count += 1
                sheets.append({"sheet": sheet.title, "rows": count})
    finally:
        workbook.close()
    temporary.replace(destination)
    manifest = {
        "dataset": "Online Retail II",
        "publisher": "UCI Machine Learning Repository",
        "creator": "Daqing Chen",
        "doi": "10.24432/C5CG6D",
        "license": "CC BY 4.0",
        "source_page": "https://archive.ics.uci.edu/dataset/502/online+retail+ii",
        "download_url": URL,
        "downloaded_at_utc": expected["downloaded_at_utc"]
        if expected
        else datetime.fromtimestamp(archive.stat().st_mtime, timezone.utc).isoformat(),
        "archive_sha256": archive_hash,
        "workbook_sha256": digest(workbook_path),
        "archive_bytes": archive.stat().st_size,
        "sheets": sheets,
        "rows": sum(sheet["rows"] for sheet in sheets),
        "headers": HEADERS,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"rows": manifest["rows"], "sheets": sheets, "source_sha256": archive_hash}))


if __name__ == "__main__":
    main()
