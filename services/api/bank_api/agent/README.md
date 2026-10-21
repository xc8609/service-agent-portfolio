# Bounded evidence assistant

`runtime.py` owns scoped state rehydration, positive DTO projection, a four-step /
20-second run budget, persisted run/step records and draft-only output. Every tool
step repeats trusted session/assignment and source-version checks through the same
`scope`, `pair_context` and workflow services used by manual paths. The model cannot
choose customer/account IDs or call human commands. No provider owns transactions.

`providers.py` normalizes OpenAI Responses, Claude Messages and compatible-chat
shapes. Default application profile is **`offline-scripted-v1`**, a deterministic fixture,
not a language model. `selection.py` loads a server-owned deployment profile and
records a configuration fingerprint with each new run. Live candidates remain
unqualified and disabled; protocol substitution is tested through mock HTTP only.
See [configuration examples](../../../../examples/README.md).

Inbound assistance creates an ordinary uncommitted note proposal with a deterministic
operation key. Use Load note history → Review saved draft → human approval. Feedback
and progress assistance produce an editable suggestion; existing current-result,
fresh identity, human review and trusted command gates still apply. No Agent write
executes a referral, callback, complaint, closure or financial operation.

Runs stop at human review. A later run uses a new trigger and current persisted
business state, not conversation memory. Same actor/trigger replays the stored run;
a changed scope/source rejects reuse. An expired running lease is marked interrupted,
not silently retried. An interrupted draft may already exist in note history, but
there is no business commit to reconcile. Get/cancel endpoints enforce original scope.
Trace stores source references and outcomes only; draft output is scoped customer
content, not an unrestricted telemetry log. Missing usage stays unavailable.

Server API: POST `/v1/assistant/run`, `/get_run`, `/cancel_run`.
UI clears prior output on context change. Network response loss retains the trigger;
manual functions stay usable. Streaming UI/live-provider quality is not claimed.

[DEV-08 evidence](../../../../projects/bank-service-assist/specs/DEV-08/runtime-contract.md) ·
[Provider ADR](../../../../docs/architecture/ADR-003-provider-boundary.md).
