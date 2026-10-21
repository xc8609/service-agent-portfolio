# DEV-09 offline delivery

Owner decision: finish offline development first; defer real-model verification.
See [ADR-003](../../../../docs/architecture/ADR-003-provider-boundary.md).

Implementation: `bank_api/agent/providers.py`; tests: `test_providers.py`.
AC01: normalized fixture multi-turn calls; application orchestration follows DEV-08.
AC02: buffer partial arguments, schema check only a finished call, reject invalid/
forbidden calls. AC03: typed timeout/rate-limit/cancel/incomplete errors, unknown usage
remains null. AC04: endpoint/internal-only/qualification gates precede transport.
AC06: positive model DTO projection. AC05/07: live qualification **not executed**;
OpenAI, Claude, DeepSeek/internal endpoints remain unqualified and disabled.

No paid calls, live benchmark, latency promise, model pricing or vendor SDK adoption
is claimed. Pinned existing httpx/jsonschema dependencies are reused; no new SDK.
