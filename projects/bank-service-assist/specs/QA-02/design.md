# QA-02-R1 design

`agent/replay.py` implements `RecordingProvider` and `RecordedProvider` using the
existing `complete(messages, schemas, cancelled)` boundary. Runtime still owns
authorization, tool execution, citations, budgets, fresh evidence and persistence.

The versioned JSON envelope declares synthetic data and operator-reported provenance
(`synthetic_fixture` or `subscription_session`), a label and ordered turns. Each turn
contains SHA-256 of canonical full messages+schemas and a normalized response. It
stores no precomputed tool result; a replay receives the actual result from runtime.
Full response content is local evaluation data, not production trace output. No
credential or private customer data is permitted. Generated exports stay ignored.

Bound file reads to 1 MB, envelopes to eight turns; the real runtime's four-step and
20-second limits still apply. Domain-invalid calls remain representable so runtime
can reject them. Envelope-invalid data fails with INVALID_RECORDING. Request drift,
exhaustion and unused positive-path suffixes have distinct errors. Copy inputs/outputs
to prevent accidental mutation. Replay usage is null; never reuse captured tokens as
new consumption. Fingerprint identifies the recording, not an approved model route.

No public configuration selects this provider. Evaluation invokes the trusted Python
seam against disposable synthetic PostgreSQL; audit identity remains
`injected-test-provider`. Persist the recording fingerprint in evaluation evidence
outside the runtime trace. The regular demo remains scripted and unchanged.

## Human-operated subscription capture procedure

An operator-owned exchange adapter receives only the current runtime prompt, tool
schemas and previous real tool results; it returns a normalized Reply from the next
subscription turn. Wrap it in RecordingProvider. Do not include future results,
expected actions or answer keys. Keep session/model/date/export evidence separately,
label hand transcription and preserve errors; provenance is declared, not attested.
No subscription automation or bridge is delivered in R1. The integration fixtures
demonstrate recording with the existing synthetic provider, not a subscription model.

Replay unchanged synthetic fixture versions in a disposable DB and change only the
trigger key for a new run. Run RecordedProvider.load(path) through runtime.run and
assert_consumed on expected-success cases. Capture DB postconditions and error codes
separately; a provider transcript alone is not an acceptance result. A mismatch means
capture a new session or retain the old fixture baseline, never edit hashes to force
success. Replay is not live-wire reasoning/signature compatibility testing.
