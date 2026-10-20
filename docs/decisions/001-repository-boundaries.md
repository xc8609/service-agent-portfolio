# ADR-001: One portfolio repository with separate business modules

Date: 19 October 2026. Status: adopted for initial publication.

## Context and decision

The bank assistant, its voice extension and the planned retail assistant share a portfolio delivery method, while retaining distinct workflows and authority. Use one public repository with independent project directories. Start with the bank module; do not create empty production services for later releases.

The bank voice channel will reuse bank business services and require a narrower authorization policy. Retail customer follow-up remains a separate domain. Extract a shared package or separate repository only when implemented contracts, independent releases or contributor ownership justify the cost.

## Publication boundary

Bootstrap with a new Git history and an explicit file allowlist. The personal workspace and its history are not upstream sources to merge. Original code and documents use MIT; third-party sources retain their terms. Synthetic contract examples are specifications, not downloaded records or measured outcomes.

## Consequences

Reviewers can follow requirements, tools, acceptance and evidence in one place. CI must remain scoped and reproducible. Future changes must avoid coupling unrelated bank and retail data or permissions. Trello mirrors planning; this repository owns versioned specs and implementation.
