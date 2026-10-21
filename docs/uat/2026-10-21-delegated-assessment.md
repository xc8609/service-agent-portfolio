# Bank core — delegated acceptance assessment

21 October 2026. Assessor: Codex, executing the owner's request to assess the
running application against industry practice. This is observed acceptance evidence,
not the owner's personal sign-off, a bank certification or production approval.

**Decision: changes required before accepting the bank core.** The principal workflow
works, but an unapproved progress statement becomes visible in the customer-safe
projection after supersession (UAT-01), and the specialist UI omits the submitted
intake context (UAT-02). Do not expand into voice or retail before retesting these.

## Baseline and method

- Application commit: `78febb83be1a388ee08705cb959b4395365bfbb2`, PR #21,
  `codex/qa02-review-fixes`; no runtime code was changed during this assessment.
- Local browser: `http://127.0.0.1:5173/`; fresh disposable synthetic database,
  schema `013_complaint_receipts.sql`, fixture `bank-policy-synthetic-v3`.
- Worker enabled. All contact verification, phone outcomes, receipts and findings
  were explicitly simulated; no actual phone call, complaint transmission or refund.
- Offline assistant route `offline-scripted-v1`; live Agent disabled. This assesses
  workflow controls, not live model reasoning quality or financial benefits.
- Walked the UI as inbound staff, specialist, two feedback representatives and
  complaint coordinator. Used the existing DEMO STORE pair and DEMO-CASE-001.
  Existing seed history is test setup, not evidence of prior customer activity.
- Separately reran the complete API suite on disposable PostgreSQL 16.2 / Python
  3.12: **225 passed in 17.38s**, one existing Starlette deprecation warning.
  Command: `PYTHONPATH=services/api .venv-app/bin/python services/api/local_postgres.py test`.
  The first sandboxed invocation could not acquire pgserver's cache lock; the
  approved invocation completed. It did not reset the interactive UAT database.
- The previous 40 browser and 20 offline/SQL passes belong to the REV-01 checks;
  they were not rerun or counted as new interactive observations here.

## Reference practices and application

Sources checked on 21 October 2026. These inform the assessment, not a claim that
this portfolio implements every practice or an institution's internal policies.

| Primary source | Applied criterion | Evidence / limit |
|---|---|---|
| [ISTQB Acceptance Testing](https://istqb.org/certifications/certified-tester-acceptance-testing/) and [definition](https://glossary.istqb.org/en_US/term/acceptance-testing/1) | Derive acceptance from business needs, rules and processes; make the acceptance decision traceable | Scenario table below links the existing UAT pack to observations and defects. Passing unit tests alone is insufficient |
| [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | Least privilege, deny by default, permission checks on every request | Unverified inbound and unclaimed work denied; approved wording alone does not authorize customer disclosure. UAT-01 shows that data projection also needs lifecycle regression coverage |
| [NIST AI RMF Playbook — Measure](https://airc.nist.gov/airmf-resources/playbook/measure/) | Evaluate purpose-specific risks with documented evidence and limits | Checked cited drafts, human approval, abstention from duplicate/refund conclusions and manual fallback. Independent live-model hold-out, effort savings and operational monitoring remain separate gates |

## Results against the existing UAT pack

PASS means the listed interactive behaviour was observed, not whole-story acceptance.
AUTOMATED ONLY means the relevant time/state behaviour was tested in the separate
API suite but not exercised interactively in this session. PARTIAL identifies a limit.

| Scenario / requirement | Result | Observed evidence |
|---|---|---|
| U1 / FR-01, NFR-01 | PASS | Unverified contact returned AUTH_REQUIRED; no transactions, search disabled |
| U2 / FR-03 | PASS, posted-pair branch | Two posted DEMO STORE entries of 85.00; source relationship absent; no duplicate or refund inferred. Pending/posted variants supported by API regression, not repeated in UI |
| U3 / FR-02, FR-23 | PASS | Customer report revision 1 saved with one-purchase/unresolved mapping; both entries retained |
| U4 / FR-04, FR-05 | FAIL after lifecycle change | Versioned applicable policy and existing ownership/deadlines shown initially. After publishing a finding, never-approved progress leaked into the customer-safe section: UAT-01 |
| U5 / FR-06, FR-26 | PASS | Offline run produced cited uncommitted draft; human returned it with a reason; approval disabled afterward |
| U6 / FR-08 | PASS | Manually authored note committed with receipt. Explicit history refresh showed the Agent draft as rejected and the manually authored draft as committed |
| U7 / FR-16, FR-24, FR-25 | PASS, link-existing branch | Submitted missing receipt and unusable contact; linked existing investigation without duplicate; customer-feedback contact-resolution task created with unchanged original investigation due time |
| U8 / FR-24 | PASS | Specialist requested material; another feedback representative claimed it and recorded customer declined; specialist returned to investigating; answer visible and original due time unchanged |
| U9 / FR-17 | PARTIAL | Further-action-required finding published. Private marker UAT-PRIVATE-20261021 absent from feedback view; pending action preserved. Specialist handoff context deficient: UAT-02 |
| U10 / FR-18, FR-19 | AUTOMATED ONLY for no-answer | Interactive branch tested never-dialed technical failure: counted false, no initial-window start or closure. No-answer/retry branch is covered by the separately rerun API tests |
| U11 / FR-18 | PASS | Approved review without fresh identity returned AUTH_REQUIRED on disclosure; verification then allowed disclosure; actual verified feedback completed task, while case remained open. Closure attempt with pending action returned CONFLICT |
| U12 / FR-19 | AUTOMATED ONLY | No three-day clock manipulation in the browser. `test_window_expires_then_lead_hold_and_bounded_new_plan` and `test_three_daily_attempts_exhaust_without_closing` passed in the rerun |
| U13 / FR-27 | PASS, inbound variant | After communicated finding, inbound disagreement created a specialist re-review and under-review case state; no new evidence was fabricated |
| U14 / FR-21, FR-28 | PASS, inbound objection variant | Explicit complaint independently queued; worker requested delivery; coordinator recorded failure, worker retried, then acknowledgement succeeded. Assigned feedback view retained both failure reason and acknowledgement with actor/time; coordinator had no Open/Claim controls |
| U15 / FR-12 | PASS, assistant unused/returned | Manual note and referral submission remained usable after returning the offline draft. Actual provider-outage branch is API-tested, not exercised with a live provider |
| DEV-03 stale evidence | PASS | Changing merchant to OTHER MERCHANT immediately cleared results/selection/evidence, disabled Agent/referral, reset recognition and marked retained edits stale |
| Assignment boundary / NFR-01 | PASS | Unclaimed contact-resolution Open returned FORBIDDEN_OR_NOT_FOUND; claim allowed required details; queue showed masked alias |

Additional evidence anchors: Agent run `b49d9725-1104-46a0-b973-ced96e120735`;
returned draft `053ec173-d43e-41cd-8390-23adeee64cb9`; committed note
`3c8e5f37-e666-465c-8896-80c74a668506`; linked-referral receipt
`d28ead7c-d57c-4e64-a185-756b47e4d0e1`; complaint work
`ff848334-6b85-4f43-80c6-43c0a9bdf1d9`; synthetic acknowledgement
`SYN-FABE82C3`. These are disposable synthetic IDs, not live customer records.

## Defects and required retests

### UAT-01 — P1: never-approved progress exposed after supersession

Parents: DEV-04/DEV-13, FR-05, NFR-01. Blocks acceptance.

1. Start the seeded verified inbound contact and inspect the DEMO STORE pair.
2. As assigned specialist, publish a finding for the existing investigation.
3. Refresh related cases as inbound staff.
4. Under **Customer-safe update**, observe `superseded update ... UNAPPROVED PRIVATE UPDATE`.

Root cause: [case_lookup.py](../../services/api/bank_api/case_lookup.py) includes all
`superseded` commitments; [workflow_commands.py](../../services/api/bank_api/workflow_commands.py)
changes both pending and approved commitments to that state. Supersession is not
proof of prior approval. `decided_at` alone is also insufficient because the publishing
command fills it for superseded pending proposals. The snapshot labels the proposed
time as `approved_update_at` despite no approval.

Required fix: preserve independently provable approval provenance; only approved
customer-safe content may enter this projection. Keep unapproved history in the
appropriate internal view. Do not silently rewrite audit history or infer approval
from non-null decision fields.

Retest: pending -> superseded must remain absent from inbound/Agent customer-safe
evidence; approved -> superseded may remain correctly labelled historical content.
Include API transition tests, browser refresh and consumer/Agent projection checks.
The existing `test_pending_and_private_information_never_disclosed` covers static
pending/approved states but misses this transition. No actual external disclosure
occurred in this synthetic run.

### UAT-02 — P2: assigned specialist cannot see the submitted intake context

Parents: DEV-07/DEV-11, FR-16, FR-23–FR-25. Blocks end-to-end staff usability acceptance.

Submit the paired unresolved recognition with a material gap, then open the assigned
specialist task. It renders merchant/status/version and publication controls, but
not the intake's verbatim statement, recognition scope, requested review, question
answers or material/contact gaps. Transaction rows lack distinguishing IDs/amounts/dates.

[workflow.detail](../../services/api/bank_api/workflow.py) returns persisted `intakes`;
[OperationsDesk](../../apps/web/src/OperationsDesk.tsx) neither types nor renders them.
Saving the data is insufficient if the receiving worker cannot use it.

Required fix: a concise, authorized intake summary with provenance/revision and
distinguishable transaction pair, retaining uncertainty and follow-up ownership.
Retest both new and linked intake, multiple revisions/intakes, unresolved recognition,
missing material and contact gaps; unassigned users must still be denied.

### UAT-03 — P3: obsolete scope text contradicts working referral controls

Parent: DEV-04/DEV-07. [RelatedCases.tsx](../../apps/web/src/RelatedCases.tsx) says
`No referral submission is available in this increment.` Section 6 successfully
submits reviewed enquiries. Replace with current guidance separating lookup from
explicit approval; check page text against the current release scope.

## Follow-up and acceptance boundary

1. Fix UAT-01 and UAT-02 in a reviewable defect PR, with transition/handoff regressions;
   correct UAT-03 in the same bounded usability pass if practical.
2. Clarify UAT seed prerequisites: DEMO-CASE-001 already has history and pending
   actions; it must not be described as a clean new-referral case. Make temporal
   scenarios reproducible with a dedicated controlled-clock fixture/test command.
3. Retest the failed scenarios and visually confirm the distinct-new referral path
   and no-answer/lead continuation before final acceptance.
4. Keep live model qualification, measured BA/agent value, staging recovery and owner
   final sign-off explicitly pending. No application merge or deployment was performed
   as part of this assessment.

Suggested value experiment after defects are fixed: compare the same evidence-grounded
cases manually and with the Agent; record lookup steps, time to a correct reviewed
draft, correction rate, unsupported claims and unauthorized-tool attempts. Define the
baseline and scoring before measurement; do not present synthetic timing as bank savings.
