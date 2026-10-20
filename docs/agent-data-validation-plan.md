# Agent data and validation plan

The application requires authored synthetic customer/account/transaction/case/policy records with independent expected outcomes. Public complaints and intent utterances do not establish transaction truth, internal permissions, handling times or operational outcomes.

- BANKING77 is an optional language source. No local download is claimed in this initial repository; the downloader/profiler and small authored test fixtures are included. See [provenance/status](../projects/bank-service-assist/data/README.md).
- CFPB is a potential public descriptive source and a separate analytical workstream. Its local datasets and earlier workspace analysis are not included in this repository. Never represent those complaints as authenticated account data.
- [Source feasibility review](../projects/bank-service-assist/docs/data-feasibility-review.md) records dated publisher-preview observations and limitations.
- [Contract fixtures](../projects/bank-service-assist/specs/contracts/continuation-schema-cases.json) and [calendar fixtures](../projects/bank-service-assist/specs/contracts/calendar-fixtures.json) are synthetic specification checks, not model evaluation or a bank policy calendar.

Before model evaluation freeze independent scenario families, reference answers, permission context and failure slices. Report provenance, model/configuration versions, denominators, exclusions and skipped suites. Establish human effort baselines separately; do not infer savings from classifier scores or synthetic task success.
