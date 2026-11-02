"""Compute improvement baselines from the published results; no request records needed."""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMER = {6, 7, 8}
REFERENCE_SUMMERS = (2023, 2024)
CREW_DAMAGED_CARTS = "Carts Damaged By Collection Crews"


def read(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def share(part, whole):
    return round(100 * part / whole, 1)


def collection_failure(monthly, demand_type):
    """Cases reporting that a collection went wrong, by year (January-September)."""
    by_year = defaultdict(lambda: {"cases": 0, "collection_failure": 0, "crew_damaged_carts": 0})
    total = failures = 0
    for row in monthly:
        cases = int(row["cases"])
        failed = demand_type[row["request_type"]] == "Collection failure"
        total += cases
        failures += cases if failed else 0
        year, month = int(row["month"][:4]), int(row["month"][5:7])
        if month <= 9:
            bucket = by_year[year]
            bucket["cases"] += cases
            bucket["collection_failure"] += cases if failed else 0
            if row["request_type"].startswith(CREW_DAMAGED_CARTS):
                bucket["crew_damaged_carts"] += cases
    crew_damaged = sum(
        int(r["cases"]) for r in monthly if r["request_type"].startswith(CREW_DAMAGED_CARTS)
    )
    return {
        "cases": total,
        "collection_failure_cases": failures,
        "collection_failure_share": share(failures, total),
        "crew_damaged_cart_cases": crew_damaged,
        "january_september": {
            str(year): {**values, "share": share(values["collection_failure"], values["cases"])}
            for year, values in sorted(by_year.items())
        },
    }


def summer_missed_collections(monthly):
    """Missed-collection cases not closed within seven days, June-August against other months."""
    years = defaultdict(lambda: defaultdict(int))
    for row in monthly:
        if row["analysis_group"] != "Missed collection":
            continue
        year, month = int(row["month"][:4]), int(row["month"][5:7])
        season = "summer" if month in SUMMER else "other"
        years[year][season + "_cases"] += int(row["cases"])
        years[year][season + "_within_7"] += int(row["closed_within_7_days"])
    result = {}
    for year, values in sorted(years.items()):
        result[str(year)] = {
            "summer_cases": values["summer_cases"],
            "summer_over_7_days": values["summer_cases"] - values["summer_within_7"],
            "summer_within_7_share": share(values["summer_within_7"], values["summer_cases"]),
            "other_months_within_7_share": share(values["other_within_7"], values["other_cases"]),
        }
    reference_cases = sum(result[str(y)]["summer_cases"] for y in REFERENCE_SUMMERS)
    reference_over = sum(result[str(y)]["summer_over_7_days"] for y in REFERENCE_SUMMERS)
    latest = result[max(result)]
    at_reference_rate = round(latest["summer_cases"] * reference_over / reference_cases)
    return {
        "by_year": result,
        "reference_summers": list(REFERENCE_SUMMERS),
        "reference_over_7_days_rate": share(reference_over, reference_cases),
        "illustration": {
            "year": int(max(result)),
            "over_7_days_at_reference_rate": at_reference_rate,
            "fewer_cases_over_7_days": latest["summer_over_7_days"] - at_reference_rate,
        },
    }


def open_records(ageing):
    groups = defaultdict(lambda: defaultdict(int))
    for row in ageing:
        cases = int(row["open_cases"])
        band = int(row["age_band"][0])
        values = groups[row["analysis_group"]]
        values["open"] += cases
        values["open_90_days_or_more"] += cases if band >= 4 else 0
        values["open_365_days_or_more"] += cases if band >= 5 else 0
    total = sum(v["open"] for v in groups.values())
    year_or_more = sum(v["open_365_days_or_more"] for v in groups.values())
    return {
        "open": total,
        "open_365_days_or_more": year_or_more,
        "open_365_share": share(year_or_more, total),
        "by_group": {g: dict(v) for g, v in sorted(groups.items(), key=lambda i: -i[1]["open"])},
    }


def follow_ups(rows):
    years = defaultdict(lambda: defaultdict(int))
    for row in rows:
        year, month = int(row["month"][:4]), int(row["month"][5:7])
        values = years[year]
        values["calls"] += int(row["follow_up_calls"])
        values["breached"] += int(row["breached_calls"])
        if month in SUMMER:
            values["summer_calls"] += int(row["follow_up_calls"])
    return {
        str(year): {**values, "breached_share": share(values["breached"], values["calls"])}
        for year, values in sorted(years.items())
    }


def build():
    results = ROOT / "results"
    monthly = read(results / "monthly_requests.csv")
    demand_type = {
        r["request_type"]: r["demand_type"] for r in read(ROOT / "reference/demand_type_map.csv")
    }
    return {
        "source": "Published results in this folder; months use the open date",
        "collection_failure": collection_failure(monthly, demand_type),
        "summer_missed_collections": summer_missed_collections(monthly),
        "open_records": open_records(read(results / "open_ageing.csv")),
        "city_follow_up_calls": follow_ups(read(results / "follow_up_monthly.csv")),
    }


def main():
    path = ROOT / "results/improvement_baselines.json"
    path.write_text(json.dumps(build(), indent=2) + "\n")
    print("Wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
