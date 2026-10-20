# DEV-10 offline implementation — 20 October 2026

Current runtime scope supersedes the original planned implementation status, without
marking the whole story accepted. No change to accepted contact rules or model budget.

`bank_api.analytics` reads three SQL marts through the restricted runtime role in one
repeatable-read transaction. Each run/proposal/plan has one row; child facts aggregate
before joining. Actual callback IDs, never-dialed faults and retained old plans remain
visible. An initial deadline is never replaced by a new contact plan. Proposal edits
compare the final payload with the first revision, not revision count alone.

CSV exports aggregates only. Independent source totals and a CSV read-back must agree.
Fingerprints flag later changes at the same cutoff; current-state semantics are explicit.
The default ignored output directory is `data/processed/tableau`. No customer narrative,
identifiers or private notes appear in the workbook data. No credentials in the workbook.

The text-table Tableau candidate and metric dictionary are in
[dashboard/README.md](../../dashboard/README.md). Live cost, measured human effort and
ROI are deliberately unavailable. This release does not claim a completed B0/B1
participant study, live model comparison, or historical time-travel reporting.

## Evidence

Six tests in `services/api/tests/test_analytics.py` passed within the 180-test PostgreSQL
16.2 suite (Python 3.12). The representative export reconciles 1 run, 1 pending proposal,
1 callback outcome, and preserves both initial and lead-approved plans. Repeat export
of unchanged ledger has identical CSV hash; late changes alter the source fingerprint.
Agent failure, cancellation, interruption and active runs all remain in the denominator.
Multi-edit accepted drafts count once; pending excluded from decided-only rate.

Tableau XML parsed/connection checked. Desktop render/refresh is not executed because
the Mac is locked. AC05/06 therefore remain partially verified; owner UAT and release
acceptance are not implied by the automated tests. Existing CFPB data analysis is
separate and untouched. Work-queue aging/commitment breach dimensions can extend this
first view later; current report covers Agent/proposal/contact-plan operational facts.
