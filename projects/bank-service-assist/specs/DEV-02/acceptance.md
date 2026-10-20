# DEV-02 acceptance record

BANK-SDD-v0.2

Implementation: not started. Runtime tests: not executed. Actual reviewer: not yet assigned for implementation acceptance. No bank approval is implied.

| AC | Planned test | Expected outcome | Actual / evidence | Status |
|---|---|---|---|---|
| DEV-02-AC01 | DEV-02-T01 | return only the permitted card/account context with source timestamp and version | Pending implementation | Not executed |
| DEV-02-AC02 | DEV-02-T02 | deny without returning private fields and offer the verification route | Pending implementation | Not executed |
| DEV-02-AC03 | DEV-02-T03 | derive scope from the session and disclose no out-of-scope existence or details | Pending implementation | Not executed |
| DEV-02-AC04 | DEV-02-T04 | reject the action; read access does not grant financial authority | Pending implementation | Not executed |
| DEV-02-AC05 | DEV-02-T05 | reject with AUTH_REQUIRED and preserve the editable draft | Pending implementation | Not executed |

Structural validation of specifications is reported separately in workflow-validation.json and does not pass these tests. Record environment, fixture/calendar/policy/provider versions, commands, actual output, defects and review decision when run.
