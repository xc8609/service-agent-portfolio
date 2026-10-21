# S02 v0.4 specification handoff

19 October 2026. All six business review items accepted; technical specification completion does not mean implementation or runtime acceptance.

## Coverage

24 four-file packages: BA-01–09, DEV-01–13, QA-01 and OPS-01. Seven newly expanded packages contribute 43 planned acceptance scenarios; the existing eight workflow packages retain 49. Later voice, retail and release stories remain planning-level backlog items.

10 model tools / 12 trusted commands; note and progress-update draft variants; 23 scoped permission actions; 32 entities and 68 foreign keys; 25 transition definitions. Current source is the JSON schema/model and linked docs, not old Trello description history.

## Next execution order

1. Technical walkthrough of DEV-01/QA-01/OPS-01 contracts and demo configuration. Build clean local foundation and disposable Postgres migration/seed path.
2. Implement DEV-02/03/04/05 lookup, case history and policy evidence as the manual B0 baseline. No model credentials required.
3. Implement DEV-06/07 reviewed note/referral and DEV-11/12/13 durable continuation using the same permission/services contracts.
4. Qualify DEV-09 providers, then connect bounded DEV-08 agent. Build DEV-10 operational marts and evaluation evidence without invented savings.

## Remaining decisions and evidence

The six rules need no repeat approval. Proposed 15% lookup improvement and model budgets require experiment/spike review before evaluation/B1. Dependency versions require compatibility installation, not a speculative version pin. The public MIT repository is initialized; see [current runtime increment](implementation/lookup-slice.md) for first-PR scope and remaining contribution gates. SQL/runtime/UI/model/cloud checks have not run in this specification pass. Keep role estimates provisional; re-estimate if implementation reveals added scope.
