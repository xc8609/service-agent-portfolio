# SDD working agreement and execution record

Version 0.1 · 19 October 2026 · GOV-01/02/03 draft for owner review.

## Artifact and change rules

Evidence/owner input → problem P → requirement ID → draft RULE → delivery story/spec version → BANK-AC → planned BANK-T → implementation PR → executed evidence → release. Acceptance examples are reviewable before code. None of these IDs alone proves execution.

Each BA story has spec.md (business content), design.md (artifact/design rationale and downstream contracts), tasks.md (actual drafting work vs remaining owner decisions), and acceptance.md (artifact checks and pending acceptance). These are specifications for analysis work, not fake application source files.

No requirement is Ready when authorization, rule, data authority, observable acceptance or critical dependency remains unknown. Requirements may be drafted before upstream owner acceptance but cannot be treated as an accepted implementation baseline.

Change behavior by updating the spec and CR first. Assess API/data/UI, tests, migrations, access/privacy, deployment and support. Record requester, actual decision maker, rationale, dates and estimates. Do not silently overwrite prior decisions.

## Working and review workflow

Backlog → drafting/in progress → **review candidate** → accepted/done. Trello originally has no review column; add a review column for candidate BA artifacts so review does not inflate implementation WIP. Sprint S01 stays in the roadmap with actual status in its description.

Actual owner has requested S01 start on 19 October. Planned end is 1 November 2026, inherited from forecast and subject to review. No elapsed effort or team velocity is invented. Only the portfolio owner and assisting agent are established participants; two/three developers and BA/QA remain resource modelling roles.

- One active major implementation slice per developer; S01 specification drafting is one coordinated evidence package.
- Before code: walk through Given/When/Then and challenge an exception.
- At review: demonstrate artifact or working increment; record actual reviewer and decision.
- End of sprint: carry incomplete work explicitly, assess remaining estimate, record retro from observed work.
- Done is actual acceptance + required evidence. Drafting a full document or assigning a future test ID is not Done.

## Release scope

M0: accepted business/rule/data/API baseline and deterministic foundation (S02).
B0: usable manual bank evidence and reviewed-record workflow (S04).
B1: comparative evaluation plus UAT, qualified providers and operable hosted demo (S06).
B2: actual inbound test call and context-preserving human continuation (S08).
R1: retail manual/assisted case and evaluated release (S10).
Current branch: S01 BA discovery only. No source-data download, model integration, financial action or cloud provisioning occurs in this activity.

## Review evidence and limitations

The author can verify IDs, links, requirement coverage and logical consistency, but cannot supply a bank's approval or an independent human usability finding. Record automated structural checks separately from business acceptance. Claim only exact checks that ran in review-report.md.
