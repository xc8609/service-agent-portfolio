# DEV-08: scoped transaction context and staff question

22 October 2026 · Increment of DEV-08-AC01/03/05 and the
[small portfolio plan](../../evaluation/r2/portfolio-scope.md). Primary pain: the
representative must assemble transaction facts, handling rules and existing work
before answering a duplicate-charge question.

## Story and acceptance

As a verified representative, I want to ask a specific question about my selected
pair and receive a sourced draft, so I can review the explanation and next step
without assembling the facts again. All operational records remain synthetic.

- **CC-01:** Given an authorized posted pair and saved customer report, a run exposes
  original merchant text, amount/currency, status, occurrence/posting dates and
  source versions. Recorded relationships include only links wholly inside the pair.
  Missing relationships do not establish duplication. Private account fields stay out.
- **CC-02:** Given a staff question of 1–1000 characters containing non-whitespace,
  the provider receives it as user input, never as system instructions or authority.
  Omitted input retains the default question for existing clients/events.
- **CC-03:** Given related cases, the provider sees reference, status, concern coverage,
  owner queue and permitted work-owner/status summaries. It can distinguish matching
  work from another concern; no specialist private notes are exposed.
- **CC-04:** Given the same trigger and question, replay returns the saved run. Changing
  the question with that trigger conflicts. The UI clears the old preview and uses a
  new trigger after editing, and blocks blank input and editing during a run.
- **CC-05:** Given a generated draft, no note is committed until the existing trusted
  staff command approves it. Changed source relationships invalidate both the run
  and subsequent note approval, including an added link where none existed before.
- **CC-06:** A question requesting a refund or increased access cannot add a tool or
  permission. Provider failures retain the manual workflow. These are engineering
  checks, not proof of a live model's semantic robustness.
- **CC-07:** After staff saves `both` or `neither` for the current posted pair, the
  old run is stale and fresh read assistance remains available. Preparing a
  duplicate-charge referral under that recognition is still rejected.
- **CC-08:** The rules tool exposes the same applicability, gap/conflict state and
  next-step suppression as the manual workspace. Missing/conflicting rules result
  in manual policy-review guidance, not an implied applicable rule.
- **CC-09:** The offline demonstration includes active related-work progress/owner,
  a missing merchant-description gap and the callback verification/review reminder.
  It remains labelled scripted and does not infer arbitrary questions' meaning.

## Design and compatibility

`AgentPanel` sends optional `staff_question` in `/v1/assistant/run`. It is included in
the existing request hash and private scope snapshot; traces still store sanitized
outcomes rather than raw conversations. No new table, migration or external service.

`safe_context` expands the transaction field allowlist. `runtime.current` adds scoped
relationships, related-work summaries and source references. `recorded_relationships`
is shared by inbound context and proposal source snapshots, so changes cannot leave a
previously reviewed statement apparently current. Link facts are tied to selected
transaction citations and locked by the full source snapshot, not guessed from names.
Existing pre-change drafts may require refreshed review because the source snapshot
now includes relationship data. Recreate the draft through normal UI controls;
do not reset data or bypass approval.

The system prompt states the descriptor/recognition distinction and treats source
text and the staff question as untrusted. Current tool order and budgets remain.
The scripted provider now produces a visibly evidence-based example with amounts,
dates and existing-work guidance. It does not interpret arbitrary questions: the UI
labels that limitation. Real provider adapters receive the question through the same
runtime but remain disabled/unqualified until separately tested.

There is limited overlap with pending PR #23's merchant-text projection and prompt.
This increment does not depend on or replace its replay harness. Integrate the
compatible descriptor changes once when merging; do not overwrite the richer context.
PR #24 supplies the current plan/evidence foundation; this incremental PR is stacked
on that branch to keep its review focused. No parent PR is merged by this work.

## Verification record

Follow-up: the [12-case subscription exercise](../../evaluation/r2/subscription-results-20261022.md)
records actual same-conversation answers, limitations and the defects behind CC-07–09.
The final local suite passed 262 API tests and 43 browser tests. `pair_context` keeps
strict referral recognition by default; only the Agent read path uses its broader
read option. Policy applicability reuses `pair_rules`; no new workflow or migration.
The earlier verification below remains historical evidence for CC-01–06.

- API: 247 tests passed on disposable PostgreSQL 16.2 / Python 3.12, including nine
  new context/question cases (parameterized validation included).
- Focused tests observe actual runtime tool output, staff question placement, private
  field exclusion, selected-only links, replay/conflict, added-link stale rejection,
  forbidden tool rejection and draft-to-trusted-note-commit.
- Browser: all 11 affected Agent/evidence/workflow tests passed after fixing question
  entry during an unfinished evidence refresh. The first full run exposed this race
  and a separate workflow timeout; both affected paths passed on rerun. Final full
  browser and CI results are recorded in the implementation PR.
- Offline: 109 passed, two SQL modules skipped locally because DuckDB is unavailable.
  Frontend build/typecheck, Ruff, SDD validators, publication and whitespace passed.
- No paid model call, human UAT approval or measured business saving is claimed.
