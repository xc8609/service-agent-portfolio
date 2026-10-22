# DEV-08 merchant descriptor evidence — 21 October 2026

## Requirement and owner decision

Trace: BR-01 information lookup pain; DEV-03 customer recognition; DEV-08-AC01/03/05;
[QA-02 R2 review](../QA-02/owner-review.md). The owner explicitly approved adding the
original transaction merchant description as controlled read-only evidence. This
supports the owner's prior service-desk work and demonstrates BA requirement-to-test
traceability plus developer authorization/data-boundary skills. No measured benefit
is claimed.

As an authorized representative, I want the assistant to see the same original
transaction descriptor needed for this enquiry, so its draft can help me clarify an
unfamiliar name without switching to invented merchant identities or recognition.

## Design and scope

- Add only `merchant_description` to the positive transaction DTO projection, alongside
  its existing ID/version/status/amount/currency. No new database field, API, tool or
  integration. Existing inbound verification and assigned-work scope precede reads
  and every provider/tool step. Staff visibility is not customer disclosure authority.
- Preserve the source string in the JSON tool result. It is untrusted descriptive
  data, never system instructions, verified merchant identity, or proof of authorization.
  A missing field stays missing; an unavailable descriptor stays an information gap.
- The system instruction requires clarification for uncertain recognition, transaction
  source citation and no invented merchant mapping. Existing staff-reviewed writes
  remain the only path to changing recognition. The scripted demo is still scripted.
- Existing context hashing covers source text; rereads detect drift. Source references
  retain transaction ID/version. Sanitized step traces do not copy the descriptor.
- Personal identifiers, full PAN, contact data, credentials and specialist private
  notes remain excluded. No external lookup, merchant enrichment or fraud adjudication.
- Prompt and DTO changed: old runtime recordings must not silently match the new
  requests. Route fingerprint alone does not identify this application change; any
  future live qualification must bind the code/prompt/projection as well as the route.
  Live provider enable flags remain unchanged and unqualified. Frozen pilot-v1 stays
  historical; it does not validate this new projection.

## Acceptance and verification

| ID | Scenario | Required result / regression |
|---|---|---|
| MD-01 | Authorized selected pair contains a descriptor | Provider sees the exact source string and ID/version, only the selected transactions; draft remains uncommitted (`test_agent_merchant`, draft) |
| MD-02 | Descriptor contains JSON-like system/refund instructions | It remains JSON tool data; attempted forbidden refund tool is rejected with no new proposal/business write (`test_agent_merchant`, refund) |
| MD-03 | Unverified caller or another customer's selected transactions | Failure before provider invocation; no new business effects (`test_agent_merchant`, authorization cases) |
| MD-04 | Source descriptor drifts mid-run, even without version increment | Stop with STALE_EVIDENCE; no draft (`test_agent_merchant`, source_drift) |
| MD-05 | No descriptor exists, or unrelated sensitive fields are present | Do not infer an alias; retain only approved fields (`test_providers` projection cases) |

These probes test deterministic runtime boundaries and data delivery. They do not
prove that a live model always interprets hostile text correctly or asks a good
clarifying question. Semantic R2 scoring, independent hold-out, human review and live
prompt-injection qualification remain pending. No new owner UAT acceptance is implied.

## Task status

- [x] Record owner decision and narrow field boundary.
- [x] Implement positive projection and explicit untrusted-descriptor guidance.
- [x] Add scoped runtime, unauthorized invocation, source-drift and projection regressions.
- [x] Record executed local suite; PR CI is a separate check on the submitted head.
- [ ] Evaluate semantic recognition/clarification on the independently reviewed R2 set.

## Executed evidence — 21 October 2026

- Full API suite: **252 passed** on Python 3.12 / isolated PostgreSQL 16.2, including
  six new descriptor-boundary test instances. The initial probe incorrectly expected
  a string transaction version; corrected to the existing numeric DTO contract before
  the passing rerun. Production version handling was not changed.
- Ruff lint/format, workflow validator, publication/link checks and whitespace checks
  passed. Local offline suite: 15 passed, two SQL test modules skipped because this
  application environment lacks DuckDB. PR CI installs the full offline dependencies.
- Review PR: [#23](https://github.com/xc8609/service-agent-portfolio/pull/23).
  CI must pass on the final submitted commit; prior head results are not carried forward.
