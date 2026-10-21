# DEV-06 implementation and verification

20 October 2026. All records are synthetic. Inbound manual note scope; owner UAT,
feedback-assignment integration and model input remain separate gates.

## Delivered

`bank_api/proposals.py` implements draft creation, immutable revision history,
expected-version editing, explicit human approval and scoped operation-status reads.
A draft has no note effect. Approval writes exactly the reviewed payload and
attributed allegations, actor/time, source versions, operation receipt, audit and
outbox atomically. Financial execution is unavailable. Conservative phrase checks
flag unsupported completion claims; they are not a general factual-verification
model. Human review remains necessary.

Every action rechecks verified contact ownership, role and account scope before
receipt replay. New writes compare the source snapshot, including current customer
report. Query changes retain local edits but require deliberate source refresh and
review; old/current source facts are available for comparison. Proposal contact,
kind and case cannot change during edit. A lost response retains the exact request
and operation key; a definite validation rejection allows correction. A same-key
changed request is rejected. No committed note can be updated by the runtime role.

## Executed checks

- Python 3.12.14, PostgreSQL 16.2: 117 API/integration tests passed, including 12 new
  note tests (parameterized instances). No SQLite substitution.
- Chromium: 26 browser tests passed, including 3 new note journeys covering edited
  review, unsupported-claim correction, stale query and lost commit response.
- TypeScript/Vite production build and Ruff passed.
- Full CI on PostgreSQL 17, container smoke and offline checks must be recorded from
  the PR checks; local results do not imply cloud success or owner acceptance.

| AC | Runtime evidence |
|---|---|
| 01 | `test_exact_reviewed_revision_receipt_and_retry`, NOTE-01 |
| 02 | `test_stale_or_unauthorized_commit_retains_draft`, NOTE-02 |
| 03 | `test_concurrent_edits_and_atomic_failure` |
| 04 | exact-receipt test, NOTE-03 real commit then dropped response |
| 05 | changed payload under committed operation key rejected |
| 06 | `test_unsupported_financial_claim_requires_edit`, NOTE-02 |
| 07 | role/foreign-source/replay authorization tests; draft-only assertion |

Injected outbox write denial rolls back note, receipt and proposal status together.
Concurrent draft edits produce one revision and one conflict. Source change and
report change reject new approval; successful old receipts remain replayable while
permission is valid. UI screenshots are generated test artifacts, not committed
customer records. Owner walkthrough remains pending.
