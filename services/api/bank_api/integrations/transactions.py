"""Normalize bank-specific export/API rows before approving a canonical read-model feed.

This module has no network, database writes, identity provisioning or model dependency.
The caller supplies an approved account mapping and a trusted observation timestamp.
"""

import argparse
import json
import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID, uuid5

FIELDS = {
    "id",
    "account_id",
    "version",
    "amount",
    "currency",
    "status",
    "merchant_description",
    "occurred_at",
    "posted_at",
    "updated_at",
}


class SourceContractError(ValueError):
    pass


def instant(value):
    if not isinstance(value, str):
        raise ValueError()
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError()
    return parsed.astimezone(UTC).isoformat()


def normalize_transactions(records, mapping, accounts, observed_at):
    """All-or-nothing validation; never infer ownership, duplicate charges or FX.

    `accounts` maps external account keys to pre-reviewed canonical account UUIDs.
    Per-source namespaces prevent collisions; source versions must be monotonic at
    ingestion (comparison with stored versions belongs to the future sync adapter).
    """
    try:
        namespace = UUID(mapping["namespace"])
        if set(mapping) != {
            "namespace",
            "source",
            "fields",
            "statuses",
            "amount_unit",
            "currency_exponents",
        }:
            raise ValueError()
        if not isinstance(mapping["source"], str) or not re.fullmatch(
            r"[a-z0-9_-]{1,64}", mapping["source"]
        ):
            raise ValueError()
        fields = mapping["fields"]
        if set(fields) != FIELDS or len(set(fields.values())) != len(FIELDS):
            raise ValueError()
        if mapping["amount_unit"] not in ("major_decimal", "minor_integer"):
            raise ValueError()
        observed_at = instant(observed_at)
        if not isinstance(records, list) or len(records) > 1000:
            raise ValueError()
        normalized, seen = [], set()
        for row in records:
            # Positive field mapping: extra source columns never pass through.
            r = {key: row[source] for key, source in fields.items()}
            if not isinstance(r["id"], str) or not r["id"] or len(r["id"]) > 200:
                raise ValueError()
            ident = str(uuid5(namespace, mapping["source"] + ":" + r["id"]))
            if ident in seen:
                raise ValueError()
            seen.add(ident)
            account = str(UUID(accounts[r["account_id"]]))
            if type(r["version"]) is not int or not 1 <= r["version"] <= 9223372036854775807:
                raise ValueError()
            if not isinstance(r["currency"], str) or not re.fullmatch(r"[A-Z]{3}", r["currency"]):
                raise ValueError()
            exponent = mapping["currency_exponents"][r["currency"]]
            if type(exponent) is not int or exponent not in (0, 1, 2, 3):
                raise ValueError()
            if mapping["amount_unit"] == "minor_integer":
                if type(r["amount"]) is not int:
                    raise ValueError()
                amount = r["amount"]
            else:
                # Floating-point monetary values are ambiguous; use decimal strings.
                if not isinstance(r["amount"], str) or not re.fullmatch(
                    r"-?(?:0|[1-9][0-9]{0,18})(?:\.[0-9]{1,3})?", r["amount"]
                ):
                    raise ValueError()
                scaled = Decimal(r["amount"]) * (10**exponent)
                if (
                    not scaled.is_finite()
                    or abs(scaled) > 9223372036854775807
                    or scaled != scaled.to_integral_value()
                ):
                    raise ValueError()
                amount = int(scaled)
            if abs(amount) > 9223372036854775807:
                raise ValueError()
            status = mapping["statuses"][r["status"]]
            if status not in ("pending", "posted", "reversed"):
                raise ValueError()
            if (
                not isinstance(r["merchant_description"], str)
                or not 1 <= len(r["merchant_description"]) <= 200
            ):
                raise ValueError()
            updated = instant(r["updated_at"])
            if updated > observed_at:
                raise ValueError()
            normalized.append(
                {
                    "id": ident,
                    "account_id": account,
                    "version": r["version"],
                    "amount_minor": amount,
                    "currency": r["currency"],
                    "status": status,
                    "merchant_description": r["merchant_description"],
                    "occurred_at": instant(r["occurred_at"]),
                    "posted_at": instant(r["posted_at"]) if r["posted_at"] is not None else None,
                    "source": mapping["source"],
                    "source_updated_at": updated,
                    "observed_at": observed_at,
                }
            )
        return normalized
    except (KeyError, TypeError, ValueError, InvalidOperation, OverflowError, AttributeError):
        raise SourceContractError("SOURCE_CONTRACT_REJECTED") from None


def main():
    parser = argparse.ArgumentParser(
        description="Offline source mapping preview; no database writes"
    )
    parser.add_argument(
        "--fixture", required=True, help="JSON containing mapping, accounts and records"
    )
    parser.add_argument(
        "--observed-at", required=True, help="Trusted batch observation time with offset"
    )
    args = parser.parse_args()
    try:
        with open(args.fixture) as source:
            fixture = json.load(source)
        rows = normalize_transactions(
            fixture["records"], fixture["mapping"], fixture["accounts"], args.observed_at
        )
        print(
            json.dumps(
                {
                    "status": "validated_preview_only",
                    "rows": len(rows),
                    "source": fixture["mapping"]["source"],
                    "database_written": False,
                }
            )
        )
    except (OSError, ValueError, KeyError, TypeError):
        parser.exit(
            1,
            "SOURCE_CONTRACT_REJECTED; inspect the local mapping without publishing source records.\n",
        )


if __name__ == "__main__":
    main()
