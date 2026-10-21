# DEV-03 / DEV-08 — evidence-bound UI state regression

20 October 2026. Synthetic local workflow; automated evidence, not owner UAT or
live-model qualification. Delivered as a corrective commit in PR #13 and carried
forward into PRs #14–#15.

## Trigger and diagnosis

During the stacked merge, PR #3 lost the manual risk prompt after selecting
`neither`; PR #13 twice failed to display the Agent's `awaiting_human` result.
Historical CI: [recognition failure](https://github.com/xc8609/service-agent-portfolio/actions/runs/39531734721),
[Agent failure](https://github.com/xc8609/service-agent-portfolio/actions/runs/39534076487).

The UI enabled actions before passive reset effects finished. Recognition was
reset after the newly inspected evidence rendered, so a newly made choice could
be cleared. The inbound Agent could start while inspection was in flight; the
subsequent context reset could discard that run's display. Durable-run reloads
also lacked an obsolete-context guard and could restore an old result or error.

Against the unchanged PR #13 application, new browser tests reproduced four
failures: launch remained enabled during a held evidence response; a delayed
reload success restored an old draft; a delayed reload failure restored an old
error; immediate `neither` recognition became `not_recorded`. The fifth case,
a delayed initial run after a query edit, already passed and remains protected.

## Requirement, design and acceptance

| Requirement | Design | Regression evidence |
|---|---|---|
| DEV-03-AC04: preserve the customer's choice and invalidate obsolete evidence | Bind the choice to its inspected snapshot. Derive `not_recorded` for a different snapshot; do not reset the choice later in an effect. Keep statement/history independently. | SI-07: four immediate choices under CPU throttling retain the risk prompt and persist the exact recognition with both source versions; existing SI-01–06 remain. |
| DEV-08-AC03: use current evidence | Block inbound launch during inspection/report save and until evidence exists. Key the Agent panel by identity/context before it becomes interactive. | AG-02: a held inspection blocks launch, then exactly one run produces a reviewed draft after release. |
| DEV-08-AC03/04: stale responses cannot replace current context | Scope run/reload state to one panel lifetime; ignore responses after that lifetime ends. Serialize run/reload controls. | AG-03 success/failure: released old reloads restore neither draft nor error; AG-04: late initial run stays absent after query change. |
| Diagnose future failures without weakening the gate | Upload browser failure snapshots/traces for seven days using a pinned official Action. | CI retains all existing assertions, timeouts and zero retries. |

No tool authority, financial operation, deadline or database schema changes.
The assigned-work Agent keeps its existing work scope; backend authorization and
version validation remain authoritative. Drafts still need human review.

## Executed local verification

- TypeScript check and production Vite build passed.
- Seven targeted cases (the two original journeys plus five regressions), repeated
  five times: **35 passed**. Recognition stress uses CPU throttling; delayed-response
  tests use explicit gates rather than sleeps or increased timeouts.
- Python 3.12 / isolated PostgreSQL 16.2 API suite: **186 passed**; existing
  Starlette/httpx deprecation warning remains.
- Root offline suite: **5 passed**. Workflow and S02 contract validators passed.
- Full Chromium browser suite: **40 passed**. Publication scan passed after
  removing local-only test configuration/dependency links. Cloud CI uses PostgreSQL 17 and additionally runs
  container smoke plus Python 3.9/3.12 offline checks.

Local browser verification used a temporary isolated service on the existing
allowed development origin `127.0.0.1:5173`; the owner's running `8000` demo and its
database were not changed. Local-only configuration, dependencies, traces and
synthetic databases are excluded from the commit. No provider keys or live model
calls were used. Historical Sprint forecasts and whole-story UAT gates remain.
