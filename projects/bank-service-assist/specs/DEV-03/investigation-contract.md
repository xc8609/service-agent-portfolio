# DEV-03 manual investigation increment

20 October 2026. Implements D-23 / RI-AC01,02,07,08,12 for a simulated inbound
contact. D-24/25 remain referral obligations, not new submission gates here.

## Human API and permission boundary

POST `/v1/workspace/get_investigation` accepts only `contact_id`; returns append-only
`history` and `current_revision`. POST `/v1/workspace/save_investigation` accepts the
strict [input schema](investigation-input.schema.json). Neither endpoint is a model
tool. Both reuse fresh session, inbound membership, owned open contact, customer
verification and account scope checks. Actor/time come from the server.

A non-blank customer statement (1–2,000 characters) is required. Recognition is
`not_recorded` (no pair), `specific_entry` (exactly one recognized ID in the pair),
`one_purchase_unresolved` (recognizes one purchase, cannot map it to an entry),
`both`, or `neither`. All latter modes require exactly two distinct same-account,
authorized transactions with their current source versions. Recognition is a
customer report, never a ledger fact or fraud/duplicate determination. Unresolved
mapping must leave recognized entry null. Supporting documents/contact details
are not required for this capture step.

Each save inserts a new immutable contact revision, statement, recognition, source
versions, actor/time and operation key. Original statements survive corrections.
Expected revision gives optimistic concurrency (409 on competing edits). A repeated
operation key with identical input returns its original receipt, without another
revision; different input with that key is rejected. Authentication/scope are
rechecked before replay, including access to referenced transactions. Source version
conflicts on new saves return 409. Save and safe audit metadata commit atomically;
no statement, merchant, token or account content goes into audit logs.

## UI state and invalidation

Changing card/date/amount/merchant immediately clears results, selection, evidence
and recognition. Changing selection clears evidence and recognition. Editing a
statement clears evidence/recognition, keeping the typed correction and selected
IDs for reinspection. In-flight responses from older query/contact revisions are
ignored. Retyping the old filter does not restore evidence. Source failure is not
an empty result. Starting another contact clears all local statement/history.

Saved revisions are visibly historical and never restored as current evidence.
Reloading the same demo contact retrieves history and the latest statement for
editing, but requires fresh lookup/inspection/recognition before a paired save.
Old revisions are superseded by later revisions; no proposal exists in this slice.
Future proposals must bind the saved revision and source versions and reject stale
commits. `neither` displays the reviewed manual risk-handoff route; it does not
create a fraud case or promise a refund. Failed/uncertain saves keep local text;
retry of unchanged input reuses the operation key. Refresh loads committed history.

## Review scenarios

- **SI-01:** save a statement without a pair, then append a corrected statement;
  both remain readable after a new session. No ledger mutation.
- **SI-02:** specific recognition identifies one selected entry; unresolved pair
  stores both IDs and no invented disputed/recognized ID.
- **SI-03:** deny both after correction; preserve history, clear stale evidence,
  offer manual risk review, no automatic financial/case action.
- **SI-04:** edit each filter or selection/statement; earlier results cannot be used;
  a delayed search/inspection response cannot repopulate the old context.
- **SI-05:** reject foreign customer IDs, forbidden roles, expired proof, extra
  authority fields, malformed pairs, stale versions and revision conflicts.
- **SI-06:** replay safely after a lost response, protect immutable history, and
  preserve local edits on save failures.

Existing-case status/detail (DEV-04), policy retrieval (DEV-05), proposal commit
and specialist referral (DEV-06/07), Agent and owner UAT remain separate work.
