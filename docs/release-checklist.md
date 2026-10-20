# Release checklist

Initial publication is a specification/tooling baseline, not an application release.

For each later application release:

- Identify the included stories, accepted requirements and change-impact review.
- Link the exact tested commit, CI run and executed acceptance evidence; document pending checks.
- Verify database migrations, permission boundaries, failure recovery and rollback where applicable.
- Record dependency/provider versions, data provenance and dataset licenses.
- Check tracked files and history for secrets, private material and excluded data.
- Confirm deployment configuration, server-side secrets, support ownership and rollback instructions.
- Publish known limitations, demo instructions and versioned release notes.
- Update Trello only for work actually completed; deployment and UAT require their own evidence.

The first contribution PR, branch protection configuration and an application release remain separate acceptance work after repository bootstrap.
