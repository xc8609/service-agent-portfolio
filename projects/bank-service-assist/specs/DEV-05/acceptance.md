# DEV-05 acceptance record

20 October 2026 · Inbound deterministic read increment implemented; owner UAT
pending. No full-story Done, model result, bank approval or production release.

| AC | Executed evidence | Result / remaining boundary |
|---|---|---|
| DEV-05-AC01 / T01 | `test_effective_interval_uses_contact_time_not_client_or_upload_order`; excluded edition tests | Effective start inclusive/end exclusive; future/old editions excluded; forged enquiry time rejected. Passed inbound scope. |
| DEV-05-AC02 / T02 | Product/jurisdiction/audience/direct-section denial, role/proof revocation and mixed-account tests | Filter before content; repeat exact-read authorization; metadata cannot widen scope. Passed inbound scope. |
| DEV-05-AC03 / T03 | `test_conflict_suppresses_instructions_and_cannot_be_hidden_by_query`; browser RP-04 | Conflict shown, guidance withheld, lead/policy-owner review requested. Passed deterministic path; generated draft deferred. |
| DEV-05-AC04 / T04 | Missing publication/jurisdiction/unsupported pair and dependency failure tests; browser RP-02/04 | Explicit gap/manual review; timeout/outage is not empty success. Passed deterministic path. |
| DEV-05-AC05 / T05 | Hostile-source privilege test and browser RP-05 | Inert text, no HTML execution, foreign/refund reads denied. Boundary passed; LLM prompt-injection evaluation remains DEV-08. |
| FR-15 / RP-03 | Browser old-response/query/statement/selection/identity tests; API expected-version mismatch | Old evidence/rules are cleared; fresh transaction version required. |

[Runtime contract](runtime-contract.md) · [Execution record](implementation-evidence.md).
Review the simulated decision table, gap/conflict language and next-step wording
with the owner before accepting the story. No financial or referral commands
were implemented by this read increment.
