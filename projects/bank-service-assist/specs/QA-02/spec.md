# QA-02-R1 — offline runtime recording and replay

Parent QA-02; first slice only. Status: implementation under review, no new model run.
Business question: does assistance follow authorized evidence and produce only a
reviewable draft, beyond selecting an action in one-shot JSON?

All records are synthetic. Preserve pilot-v1/review-v2 and their frozen inputs.
Use the existing `Provider` injection seam in `runtime.run`; do not add endpoints,
credentials, new orchestration or deployment profiles. Each recorded response binds
to the exact preceding messages (including actual tool results) and domain schemas.
Mismatch fails rather than substituting canned evidence or guessing identifiers.

[Design](design.md) · [Tasks](tasks.md) · [Acceptance](acceptance.md) ·
[Owner review packet](owner-review.md) ·
[Revised stage plan and pending owner decisions](../../../../docs/backlog/validation-next.md).
