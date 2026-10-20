"""Fetch an immutable publisher snapshot; profile locally without model/API access.

Standard library only, Python 3.9+. Never executes downloaded code.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import tempfile
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]
REPOSITORY = "PolyAI-LDN/task-specific-datasets"
FILES = {
    "train.csv": "banking_data/train.csv",
    "test.csv": "banking_data/test.csv",
    "categories.json": "banking_data/categories.json",
    "LICENSE": "LICENSE",
    "README.md": "README.md",
}
SCOPE = {
    "transaction_charged_twice": "core_duplicate_enquiry",
    "pending_card_payment": "core_transaction_state_clarification",
    "card_payment_not_recognised": "manual_fraud_path",
    "compromised_card": "manual_fraud_path",
    "Refund_not_showing_up": "adjacent_refund_enquiry_not_case_status",
    "request_refund": "adjacent_request_not_permission_to_refund",
    "reverted_card_payment?": "adjacent_transaction_state",
    "extra_charge_on_statement": "adjacent_ambiguous_charge",
    "unable_to_verify_identity": "verification_fallback",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def parse_csv(data, categories):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    if reader.fieldnames != ["text", "category"]:
        raise ValueError("Expected exactly text,category columns")
    rows = list(reader)
    for index, row in enumerate(rows, 1):
        if set(row) != {"text", "category"} or not row["text"] or not row["text"].strip():
            raise ValueError("Malformed or empty text at record %s" % index)
        if row["category"] not in categories:
            raise ValueError("Unknown category at record %s" % index)
    return rows


def profile(train, test, categories):
    groups = defaultdict(list)
    splits = {}
    for split, rows in (("train", train), ("test", test)):
        counts = Counter(row["category"] for row in rows)
        normalized = Counter(normalize(row["text"]) for row in rows)
        splits[split] = {
            "rows": len(rows), "labels_present": len(counts),
            "label_counts": dict(sorted(counts.items())),
            "missing_labels": sorted(set(categories) - set(counts)),
            "exact_duplicate_excess": len(rows) - len({r["text"] for r in rows}),
            "normalized_duplicate_excess": sum(n - 1 for n in normalized.values()),
            "scoped_counts": {label: counts[label] for label in SCOPE},
        }
        for index, row in enumerate(rows, 1):
            groups[normalize(row["text"])].append(
                {"split": split, "record": index, "category": row["category"]}
            )
    overlap = [refs for refs in groups.values() if len({r["split"] for r in refs}) > 1]
    conflicts = [refs for refs in groups.values() if len({r["category"] for r in refs}) > 1]
    return {
        "splits": splits, "declared_categories": len(categories),
        "cross_split_normalized_groups": len(overlap),
        "cross_split_references": overlap,
        "conflicting_label_groups": len(conflicts),
        "conflicting_label_references": conflicts,
        "normalization": "Unicode NFKC, casefold, collapse whitespace; not semantic deduplication",
        "scope": SCOPE,
    }


def read_snapshot(folder):
    manifest = json.loads((folder / "manifest.json").read_text())
    blobs = {}
    for name in FILES:
        data = (folder / name).read_bytes()
        record = manifest["files"][name]
        if digest(data) != record["sha256"] or len(data) != record["bytes"]:
            raise ValueError("Snapshot integrity mismatch: " + name)
        blobs[name] = data
    categories = json.loads(blobs["categories.json"])
    if not isinstance(categories, list) or not all(isinstance(x, str) for x in categories):
        raise ValueError("Category list must contain strings")
    if len(categories) != len(set(categories)):
        raise ValueError("Duplicate category definitions")
    train = parse_csv(blobs["train.csv"], set(categories))
    test = parse_csv(blobs["test.csv"], set(categories))
    if (len(train), len(test), len(categories)) != (10003, 3080, 77):
        raise ValueError("Publisher counts changed; inspect before updating the data contract")
    return manifest, categories, train, test


def fetch(url):
    request = Request(url, headers={"User-Agent": "bank-service-portfolio-data-audit"})
    with urlopen(request, timeout=30) as response:
        data = response.read(5_000_001)
    if len(data) > 5_000_000:
        raise ValueError("Unexpected response size: " + url)
    return data


def download(revision):
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        if revision != "master":
            raise ValueError("Use master for first discovery or an exact 40-character commit SHA")
        metadata = json.loads(fetch("https://api.github.com/repos/" + REPOSITORY + "/commits/master"))
        revision = metadata["sha"]
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ValueError("Invalid publisher commit")
    base = PROJECT / "data/raw/banking77"
    base.mkdir(parents=True, exist_ok=True)
    target = base / revision
    if target.exists():
        read_snapshot(target)
        return target
    manifest = {
        "repository": "https://github.com/" + REPOSITORY,
        "revision": revision, "license": "CC-BY-4.0",
        "files": {}, "data_kind": "publisher_online_banking_queries_with_intent_labels",
    }
    with tempfile.TemporaryDirectory(prefix=".partial-", dir=str(base)) as temporary:
        staging = Path(temporary)
        for name, source_path in FILES.items():
            url = "https://raw.githubusercontent.com/%s/%s/%s" % (REPOSITORY, revision, source_path)
            data = fetch(url)
            (staging / name).write_bytes(data)
            manifest["files"][name] = {
                "url": url, "sha256": digest(data), "bytes": len(data),
                "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            }
        (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        read_snapshot(staging)
        staging.rename(target)
    return target


def write_profile(folder):
    manifest, categories, train, test = read_snapshot(folder)
    report = profile(train, test, categories)
    report["source_revision"] = manifest["revision"]
    output = PROJECT / "data/processed/banking77" / manifest["revision"]
    output.mkdir(parents=True, exist_ok=True)
    (output / "profile.json").write_text(json.dumps(report, indent=2) + "\n")
    # Training examples only. Do not expose upstream test text during discovery.
    samples = []
    for label in SCOPE:
        candidates = [(i, row) for i, row in enumerate(train, 1) if row["category"] == label]
        candidates.sort(key=lambda pair: (digest(pair[1]["text"].encode()), pair[0]))
        for i, row in candidates[:3]:
            samples.append({"record": i, "split": "train", **row, "proposed_use": SCOPE[label]})
    (output / "training_review_samples.json").write_text(json.dumps(samples, indent=2) + "\n")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    get = sub.add_parser("download")
    get.add_argument("--revision", default="master")
    inspect = sub.add_parser("profile")
    inspect.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    if args.command == "download":
        print(download(args.revision))
    else:
        print(write_profile(args.snapshot))


if __name__ == "__main__":
    main()
