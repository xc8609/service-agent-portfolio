"""Download and verify one official historical snapshot; no third-party dependencies."""
import csv
import hashlib
import json
import shutil
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
NAME = "CCDB_Export_20_July_2026"
URL = "https://files.consumerfinance.gov/f/documents/" + NAME + ".zip"
EXPECTED_SHA256 = "aafebbaaf0962c3d29532411ac2133c01bae830b7ea6ed1931a6e42278437d18"
ARCHIVE_PAGE = "https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    raw = PROJECT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    archive = raw / (NAME + ".zip")
    manifest_path = raw / "source-manifest.json"
    if not archive.exists():
        partial = archive.with_suffix(".zip.part")
        try:
            with urllib.request.urlopen(URL, timeout=60) as source, partial.open("wb") as target:
                size = 0
                while True:
                    block = source.read(1024 * 1024)
                    if not block:
                        break
                    size += len(block)
                    if size > 128 * 1024 * 1024:
                        raise ValueError("Archive exceeds the 128 MiB download limit")
                    target.write(block)
            partial.replace(archive)
        finally:
            partial.unlink(missing_ok=True)
    digest = sha256(archive)
    if digest != EXPECTED_SHA256:
        raise ValueError("Archive differs from the verified July snapshot; investigate source changes")
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text())
        if old["archive_sha256"] != digest:
            raise ValueError("Archive differs from the recorded snapshot; investigate before reuse")
    csv_path = raw / (NAME + ".csv")
    partial_csv = csv_path.with_suffix(".csv.part")
    try:
        with zipfile.ZipFile(archive) as source:
            members = source.infolist()
            if len(members) != 1 or members[0].filename != NAME + ".csv":
                raise ValueError("Unexpected ZIP contents")
            if members[0].file_size > 512 * 1024 * 1024:
                raise ValueError("CSV exceeds the 512 MiB extraction limit")
            with source.open(members[0]) as data, partial_csv.open("wb") as target:
                shutil.copyfileobj(data, target)
        partial_csv.replace(csv_path)
    finally:
        partial_csv.unlink(missing_ok=True)
    with csv_path.open(newline="", encoding="utf-8-sig") as stream:
        header = next(csv.reader(stream))
    manifest = {
        "source_page": ARCHIVE_PAGE, "url": URL,
        "retrieved_at_utc": datetime.fromtimestamp(archive.stat().st_mtime, timezone.utc).isoformat(),
        "retrieval_time_basis": "Local archive file modification time at initial download",
        "archive_bytes": archive.stat().st_size, "archive_sha256": digest,
        "csv_file": csv_path.name, "csv_bytes": csv_path.stat().st_size,
        "csv_sha256": sha256(csv_path), "header": header,
        "selection": "Entire official July 2026 archive member, no row filter",
        "terms_url": "https://www.consumerfinance.gov/privacy/website-privacy-policy/",
        "use_statement_url": "https://www.consumerfinance.gov/data-research/consumer-complaints/",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
