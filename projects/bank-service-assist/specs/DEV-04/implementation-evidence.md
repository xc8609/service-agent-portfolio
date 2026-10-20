# DEV-04 related-case lookup evidence

20 October 2026. Synthetic inbound manual workflow; not production or owner UAT.
Branch `codex/dev-04-related-case-progress`, stacked on unmerged DEV-03 PR #2.

## Delivered and traced

The [runtime contract](runtime-contract.md) maps CK-01–07 to DEV-04 acceptance.
`case_lookup.py` projects the same scoped domain data into the canonical
get_case_snapshot tool response and the manual get_related_cases response.
Migration 004 adds public case reference, status freshness/head fields and a
customer-safe event timeline. Runtime access to new tables is SELECT only; there
is no case-create, reassignment, reopening, closing or financial command.

`RelatedCases.tsx` automatically checks selected evidence, shows accountable queue,
assigned/unassigned staff, work status, original/current due times, outstanding
requirements, approved progress and a sequence-ordered timeline with both times.
Partial/different/closed/unknown-status concerns require review. Errors clear
current detail and retain only the stale lookup-time label, never an empty-success
or permission to submit. Existing statement capture is not a new referral.

## Executed checks

- API/PostgreSQL: 78 tests passed on local PostgreSQL 16.2 / Python 3.12.14.
  Includes the 56 earlier tests and 22 case-read scenarios/parameter cases.
- Browser: 15 Playwright journeys passed (six case journeys plus nine regressions).
- Production TypeScript/Vite build, Ruff check/format, root offline tests, SDD and
  v0.4 contract validation and publication/link checks are recorded with this PR.
- HTTP/container smoke now checks related-case status/ownership and canonical
  snapshot equivalence, excluding unapproved progress. Cloud PostgreSQL 17 and
  container results are shown in the PR checks, separately from local evidence.

The initial API run caught a timezone-dependent assertion (Winnipeg offset vs UTC
representing the same instant); the test now compares aware datetimes. The first
browser run caught an ambiguous owner locator because one specialist owns two
work items; the assertion now targets the investigation task. One existing
Starlette/httpx deprecation warning remains; it is not an application failure.

## Explicit remaining boundaries

AC01/04 assigned outbound feedback claim/reassignment permissions remain pending;
the implemented paths are verified inbound reads plus denial of unsupported
feedback/Agent roles. Outbound contact-plan projection is not implemented here.
AC05 is read projection of separate synthetic tasks, not implementation of their
creation or completion. DEV-05 handling rules and DEV-07 atomic submission-time
same-concern checks remain pending. Do not mark the full story or S03 Done.
Owner UAT, live bank integration, model execution and production deployment have
not been performed.
