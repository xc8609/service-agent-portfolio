"""Authored simulated procedures, not bank policy or legal guidance."""


def seed_policies(conn):
    from .fixtures import insert, uid

    for name, version, product, jurisdiction, audience, start, end, published, pattern in [
        (
            "posted",
            "1",
            "credit_card",
            "CA",
            "inbound_representative",
            "2026-01-01",
            None,
            True,
            "two_posted",
        ),
        (
            "pending",
            "1",
            "credit_card",
            "CA",
            "inbound_representative",
            "2026-01-01",
            None,
            True,
            "pending_posted",
        ),
        (
            "posted_old",
            "0",
            "credit_card",
            "CA",
            "inbound_representative",
            "2025-01-01",
            "2026-01-01",
            True,
            "two_posted",
        ),
        (
            "posted_future",
            "2",
            "credit_card",
            "CA",
            "inbound_representative",
            "2099-01-01",
            None,
            True,
            "two_posted",
        ),
        (
            "restricted",
            "1",
            "credit_card",
            "CA",
            "specialist",
            "2026-01-01",
            None,
            True,
            "two_posted",
        ),
        (
            "other_product",
            "1",
            "loan",
            "CA",
            "inbound_representative",
            "2026-01-01",
            None,
            True,
            "two_posted",
        ),
        (
            "other_country",
            "1",
            "credit_card",
            "US",
            "inbound_representative",
            "2026-01-01",
            None,
            True,
            "two_posted",
        ),
        (
            "draft",
            "1",
            "credit_card",
            "CA",
            "inbound_representative",
            "2026-01-01",
            None,
            False,
            "two_posted",
        ),
    ]:
        active = name in ("posted", "pending")
        body = (
            "Two posted entries are not proof of duplicate charging. Confirm whether the customer recognizes one purchase, one specified entry, both entries or neither. If one purchase is recognized but the entry is unclear, keep both entries grouped for specialist verification. Review existing related work before preparing a new enquiry. Supporting documents and contact details may follow: record gaps, retain customer-service ownership and original deadlines; undelivered feedback does not close the case."
            if name == "posted"
            else "A pending authorization and a posted entry may relate to one purchase. Explain a link only when the transaction source records it. No link means the relationship is unknown. Do not promise a reversal, refund or release date. Record the concern and seek specialist clarification if unresolved."
            if name == "pending"
            else "Excluded synthetic edition: " + name
        )
        insert(
            conn,
            "policy_versions",
            {
                "id": uid("policy_" + name),
                "policy_key": "demo-posted" if name.startswith("posted") else "demo-" + name,
                "version": version,
                "product": product,
                "jurisdiction": jurisdiction,
                "audience": audience,
                "effective_from": start,
                "effective_to": end,
                "body": body,
                "source_label": "Authored synthetic procedure / DEV-05 / 2026-10-20",
                "published": published,
            },
        )
        insert(
            conn,
            "policy_sections",
            {
                "policy_version_id": uid("policy_" + name),
                "section": "handling",
                "title": "Two posted entries: investigate before concluding"
                if pattern == "two_posted"
                else "Pending and posted: verify the source relationship",
                "decision_key": "charge-enquiry",
                "transaction_pattern": pattern,
                "conditions": [
                    "Verified inbound contact; permitted credit-card account in CA.",
                    "Exactly two selected entries from the same account.",
                    "Both entries are posted."
                    if pattern == "two_posted"
                    else "One entry is pending and one is posted.",
                    "Customer recognition is reported evidence, not proof of a duplicate.",
                ],
                "next_steps": (
                    [
                        "Confirm and record the customer statement and recognition scope; do not force an entry choice.",
                        "Review the related-case panel. Continue existing matching work before considering a new enquiry.",
                        "If unresolved, prepare both entries for human-reviewed specialist verification. Record missing documents/contact details and customer-service follow-up ownership; do not reset deadlines or auto-close.",
                    ]
                    if name == "posted"
                    else [
                        "Read the recorded authorization relationship; if absent, explain that the relationship is unknown.",
                        "Confirm customer recognition and review existing work. Seek specialist clarification if unresolved; do not promise a release date or refund.",
                    ]
                )
                if active
                else ["Excluded synthetic instruction."],
            },
        )
