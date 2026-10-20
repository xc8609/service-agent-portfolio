# Contributing

This repository follows specification-driven development. For a feature or fix:

1. Find its Trello/story ID and current spec, design, tasks and acceptance record.
2. Explain the business question and update affected requirements/contracts before implementation.
3. Branch as `codex/<story-id>-<topic>`. Keep unrelated changes out of the PR.
4. Implement with relevant offline, API/database, UI and recovery checks as applicable. Do not claim an unexecuted suite passed.
5. Link executed evidence and limitations in the PR; update the story and acceptance record after review.

The first import is a clean portfolio-only history. Future product features use PRs. Trello is the planning/review mirror; versioned specs and code in Git are canonical. Do not attach customer records, employer documents, access tokens or private job-search material.

Before submitting, run the README checks. Public data terms remain independent of project code licensing. Report security issues using SECURITY.md; do not place exploit credentials or private records in public issues.

Main is protected: PR required, all four CI contexts must pass and the branch must be up to date; conversations must be resolved. Force push/deletion are disabled and administrators are included. The solo portfolio requires zero additional human approvals; this is not independent review. See [verified settings](docs/github-branch-protection.json). Application changes additionally run the [runtime checks](services/api/README.md).
