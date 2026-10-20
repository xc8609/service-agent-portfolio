# Synthetic workflow operations — DEV-10

This Tableau text-table workbook accompanies reconciled SQL exports from the bank
workflow. It is engineering evidence, not a study of a real bank or an estimate of
savings. Live model qualification and a human effort study have not run.

## Reproduce the synthetic review dataset

From repository root with the Mac development environment installed:

```bash
BANK_ANALYTICS_EXPORT=projects/bank-service-assist/data/processed/tableau \
  .venv-app/bin/python services/api/local_postgres.py test
```

The isolated PostgreSQL test journey publishes a result, records an unanswered
callback, expires its original window, approves a new plan and runs the offline
assistant. The DEV-10 test exports that specific ledger twice. Other tests reset
the disposable database; the retained CSV is this labelled journey, not their totals.
Fixture clock: 20 October 2026; evaluation cutoff: 27 October 2026. Dates are
simulation time, not a claim that future work has happened. IDs and measured runtime
latency vary between new fixture executions; repeated exports of unchanged records
have identical CSV hashes. Generated data is excluded from Git.

For your own running synthetic demo, use its existing restricted runtime environment:

```bash
PYTHONPATH=services/api .venv-app/bin/python -m bank_api.analytics \
  --cutoff 2026-10-27T15:00:00Z
```

Do not put database credentials on the command line or in a workbook. This is a local
operator export, not a new customer-data HTTP endpoint. CSV includes only aggregates;
no customer/staff/contact/transaction IDs, narrative or private notes are exported.

Open `workflow_operations.twb` in Tableau Desktop. Its relative text connection
points to `../data/processed/tableau/workflow_metrics.csv`. If Desktop asks to locate
the file, select that generated CSV. The view groups metric, segment and availability;
blank values retain an explicit unavailable reason. Do not replace missing values
with zero. Verify run/proposal/attempt totals against `manifest.json`, inspect both
plan segments, and check unavailable cost/ROI before publishing any screenshot.

## Metric dictionary

| Metric | Definition and denominator |
|---|---|
| All started runs | One authoritative run ID, including running/failed/cancelled/interrupted; replay is not a new run |
| Run outcome | Current state at extraction; awaiting human means draft prepared, not customer issue resolved |
| Terminal latency | finished minus started; unfinished excluded from mean and shown as missing; not human handling time |
| Missing usage / cost | Missing usage reported; cost unavailable until a qualified pricing/usage source exists |
| Proposal disposition | One proposal ID; committed current payload compared to first revision; multiple edits do not multiply decisions |
| Accepted proportion | Committed / (committed + rejected); pending excluded and separately shown; no denominator yields blank |
| Recorded outcomes | All persisted callback outcomes, including never-dialed faults |
| Quota-counted calls | Authoritative counts_toward_limit; separate initial and lead-approved plans |
| Retained window misses | Window expired without a non-anomalous verified contact by that deadline; subsequent plans cannot erase it |
| Original first-contact miss | Initial plan had no actual first call by original work due time, irrespective of new plans |
| Measured time saved / ROI | Unavailable: no participant timing or benefit attribution study |

Three SQL grains (run, proposal, retained contact plan) aggregate independently to
avoid steps × revisions × attempts fanout. Independent base-table count oracles and
CSV totals must agree or export fails. `manifest.json` records cutoff, extraction
time, source/CSV fingerprints and changes since the preceding export. This is the
**current state of records admitted by cutoff**, not historical time travel. A late
correction can change an export at the same cutoff; retain both manifests if auditing
successive extracts. No mixed synthetic/live segment is inferred from a profile name;
this deployment contains synthetic operational records only.

## Executed evidence and remaining gate

180 PostgreSQL API tests passed, including six DEV-10 tests for reconciliation,
replays/outcomes, multiple revisions, faults, retained continuation history, late
corrections and empty denominators. Exported review journey: 1 run, 1 pending proposal,
1 recorded call, 1 expired initial window; new-plan history retained. No efficacy claim.
Desktop verification on 20 October 2026: Tableau Desktop Free Edition 2026.2.3
opened the repaired workbook and resolved the relative CSV connection. The initial
attempt exposed missing `source-build`, table `style`, and window `cards` elements;
the hand-authored XML now includes them, with a regression check.

The sheet displayed 30 marks: one started run awaiting human review, one pending
proposal, and one recorded contact outcome. Model cost, measured savings and ROI
remained blank with explicit unavailable reasons. This is synthetic engineering
evidence, not a measured business benefit. Some labels are truncated and the title
is not visible in the current sheet layout; presentation polish remains open.
A subsequent refresh action could not be verified when native controls stopped
responding and screenshots became unavailable. Refresh acceptance and owner UAT
remain pending; a successful open is not full visual acceptance.

The installed Free Edition displays a restriction on sharing its assets. This pass
only opened the hand-authored workbook locally; no workbook was published. Choose
an appropriate Tableau publication route/license before sharing a rendered asset.
