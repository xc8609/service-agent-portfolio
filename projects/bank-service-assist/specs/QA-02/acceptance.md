# QA-02-R1 acceptance

All examples are engineering fixtures, not model evaluations or owner sign-off.
Tests: `services/api/tests/test_agent_replay.py`.

| ID | Given / when | Required result |
|---|---|---|
| R1-01 | Capture three fixture exchanges; replay through runtime in same synthetic context | Actual evidence/rules/draft steps persist; only uncommitted proposal is added; usage unknown |
| R1-02 | A recorded reply names an unauthorized tool, invalid args, wrong order, repeated call ID or invented citation | Existing runtime rejection, no new proposal or business write |
| R1-03 | Evidence changes before replay or prompt/tool schema changes | Request digest differs; fail replay, never reuse recorded tool facts |
| R1-04 | Contact is unverified | AUTH_REQUIRED before any recorded response is consumed |
| R1-05 | Evidence changes, cancel arrives or time expires during replay | STALE_EVIDENCE/CANCELLED/TIME_BUDGET; no new draft |
| R1-06 | Recorded read loop exceeds four runtime steps | STEP_BUDGET, no draft |
| R1-07 | Missing next turn, unused success suffix, invalid/oversized file, non-synthetic declaration | Explicit failure; not counted as a successful scenario |

Run full isolated API suite and required PR CI. Fixtures confirm integration and
negative control behavior, not model reasoning, independently reviewed business
expectations, accessibility or real API latency. Record outcome/date in tasks.md.
