# DEV-10 — Build operational event marts and a reconciled Tableau view

BANK-S02-v0.4 · Detailed specification candidate; implementation not started.
Forecast: S05A | Release: B1 | Estimate: Dev 3, BA 1, QA 0.5 person-days. Provisional until technical review.

- [x] Write detailed specification and linked expected outcomes.
- [ ] Review current dependencies, fixtures, contract version and estimate.
- [ ] Record run/contact/proposal/action IDs and authoritative timestamps without sensitive payloads.
- [ ] Build SQL marts and aggregate exports for Tableau; retain existing CFPB descriptive analysis separately.
- [ ] Add reconciliation totals and labelled synthetic/live-test segmentation. Report cost unavailable if usage is missing.
- [ ] Implement and record DEV-10-T01: build marts.
- [ ] Implement and record DEV-10-T02: calculate run metrics.
- [ ] Implement and record DEV-10-T03: calculate proposal metrics.
- [ ] Implement and record DEV-10-T04: calculate callback metrics.
- [ ] Implement and record DEV-10-T05: render Tableau.
- [ ] Implement and record DEV-10-T06: export and refresh workbook.
- [ ] Record runtime defects, re-test and owner UAT/release review; do not mark Done from artifact validation.
