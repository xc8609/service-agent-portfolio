# DEV-05 inbound runtime contract

20 October 2026 · B0 read increment · supplements shared v0.4 contracts.
Owner experience: customer-service desktop information/rule lookup. Target role
requirements: scoped APIs, BA rule analysis, testable acceptance and traceability.
No bank policy, legal advice, production approval or measured benefit is claimed.

## Business decision table

| Verified source context | Applicable simulated procedure | Representative next step |
|---|---|---|
| Two posted entries, same permitted credit-card account, CA | `demo-posted`, section `handling`, version 1 | Confirm recognition/statement; inspect existing work; if unresolved, prepare paired evidence for human-reviewed specialist investigation. Equal amounts do not prove duplication. |
| One pending and one posted, same scope | `demo-pending`, section `handling`, version 1 | Inspect recorded authorization linkage; absent linkage remains unknown; clarify the customer's concern and seek specialist review if unresolved. No refund/release-date promise. |
| Unknown jurisdiction, unsupported pair or no published effective rule | Gap | Keep concern open and seek manual policy review through the service lead. |
| Multiple eligible sections share decision key and transaction pattern | Conflict | Show conflicting citations/conditions and source text for comparison, suppress suggested steps. Lead obtains policy-owner clarification. No latest-upload priority. |

D-23/24/25 remain intact: unresolved recognition can stay grouped; material and
contact gaps do not prohibit preparing an enquiry, reset deadlines or close
undelivered feedback. Existing DEV-04 case review remains required. This read
increment does not create/refund/close a case or establish a completion commitment.
Policy fixture authorship belongs to this portfolio; service lead/policy owner are
simulated responsibility labels, not claimed stakeholder approvals.

## Endpoints and authorization

- `POST /v1/workspace/get_handling_rules`: exact object with `contact_id`, two
  unique UUID `transaction_ids`, and `expected_versions` keyed by exactly those
  IDs. Server reloads permitted records and compares versions. Changed evidence
  returns `EVIDENCE_CHANGED` (409) with no guidance; mixed/foreign scope denies
  the entire read (404). No client-supplied role, product or jurisdiction.
- `search_policy` and `get_policy_section` implement existing v0.4 read schemas.
  Search is literal case-insensitive title/body substring (1–200 characters), not
  semantic ranking. Product/jurisdiction must match an authorized account;
  `as_of` must equal the contact's recorded `opened_at`. Status is only a search
  narrowing hint, not verified transaction evidence. Search results are candidate
  metadata; use the workspace endpoint for verified pair applicability.
- Exact section requires the correct ID/version/section, and rechecks all filters;
  IDs cannot bypass audience, product, jurisdiction, publication or effective time.
  Missing and disallowed sections use the same safe 404. Conflicting applicable
  editions return `POLICY_CONFLICT` (409). Search detects conflicts before text
  filtering and returns an explicit gap warning even when the query narrows hits.
- Fresh active principal, active inbound membership/queue, own open inbound contact,
  trusted unexpired customer proof and account scope on every call. Unclaimed
  feedback, lead and undelegated Agent contexts remain unsupported and denied.
  Future assigned feedback/Agent reads need their own scoped implementation.
- Runtime database role has SELECT only on policies/sections; business writes are
  unchanged. Audit holds action/outcome/request ID, never policy text, queries or
  customer narrative. DB outage/timeout returns typed 503, not an empty success.

## Rule model and provenance

Migration 005 adds nullable account jurisdiction (never inferred from CAD),
publication state (default false), and sections with decision key, pair pattern,
conditions and next steps. This narrow demo uses one exact body per edition and
one `handling` section; multi-section ingestion/search is deferred.

Effective interval is `[effective_from, effective_to)`, evaluated at recorded
contact start; missing end means open-ended, not proof of perpetual validity.
Refresh uses a fresh database snapshot. Newer/future/expired/unpublished editions
never outrank an applicable one. Overlap is deliberately conservative: same
product/jurisdiction/decision/pattern is treated as conflicting, even if wording
looks similar. No automated policy authoring, approval or mutation endpoint.

Each UI rule includes exact source text, ID/version/section, source label,
simulated flag, conditions and suggested steps. Response separates contact-time
applicability from retrieval time and carries selected transaction versions.
No knowledge confidence score or invented rationale. Customer recognition remains
an explicit representative check, not inferred from a rule match.

## UI and evidence freshness

- Automatically retrieve after inspecting exactly two entries; manual refresh is
  available without a model. Non-pair selections show a scope prompt.
- Loading clears old advice. Gap/conflict/denial/failure are distinct; conflict
  renders no next-step list. Do not interpret a failed read as no policy.
- Query, selection, statement/history and identity changes unmount the panel;
  late responses cannot restore guidance for a previous context.
- Source text is rendered as inert React text, not HTML or instructions to tools.
  This proves UI/backend boundaries only. LLM prompt-injection resistance and
  bounded orchestration remain DEV-08 evaluation work.

## Acceptance trace

| Runtime check | Story AC | Automated evidence |
|---|---|---|
| RP-01 scoped effective rule and exact citation, posted vs pending | AC01/02 | `test_policy.py`, browser RP-01, HTTP smoke |
| RP-02 safe denial/outage/version mismatch | AC02/04 | API scope/version/revocation tests, browser RP-02 |
| RP-03 invalidate old context and in-flight result | FR-15 | browser RP-03 |
| RP-04 overlap/gap never becomes authoritative advice | AC03/04 | API conflict/interval/gap tests, browser RP-04 |
| RP-05 untrusted narrative cannot execute HTML or expand authority | AC05 boundary | API privilege/hostile text test, browser RP-05; model evaluation pending |

Acceptance requires owner walkthrough; technical verification is not owner UAT.
