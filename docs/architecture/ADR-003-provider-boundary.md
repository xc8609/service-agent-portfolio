# ADR-003 — Application-owned provider boundary

20 October 2026. Offline implementation accepted for engineering review; live
provider qualification explicitly deferred by the owner.

Business authorization, durable workflow state and human approval stay in application
services. Use a small normalized Python boundary over HTTP APIs; do not give an SDK
control over financial actions, credentials or database transactions. OpenAI Agents
SDK / Claude Agent SDK are not required by this service-assistance use case. This
choice avoids coupling the business model to a vendor runtime, while preserving an
interface into which an SDK-backed adapter may later fit after qualification.

Implemented protocols: OpenAI Responses function calls, Claude Messages client tools,
and a separately labelled compatible-chat shape. Each returns normalized complete
calls/text/usage. Unknown usage is null; no cost is fabricated. Partial argument
buffers cannot execute. Network errors are typed and sanitized, redirects disabled,
no automatic retry/fallback, bounded input/output and 15-second HTTP timeout.

Profiles use exact HTTPS endpoint allowlists. Internal-only profiles cannot use a
public endpoint. Server-side credentials never enter UI or model DTOs. A positive
field projection excludes customer/contact identifiers, private specialist notes and
credentials. Retrieved text remains untrusted and may contain instructions; DEV-08
also constrains tool authority and citations. A regex is not treated as a complete
prompt-injection or financial-claim detector.

## Qualification matrix

| Route | Protocol fixtures | Live compatibility / quality / cost |
|---|---|---|
| Scripted offline fixture | Tested | Not a language model; no quality claim |
| OpenAI Responses | Tested with mock HTTP/normalized calls | Not executed; disabled |
| Claude Messages | Tested with normalized calls | Not executed; disabled |
| Compatible chat (possible DeepSeek/internal) | Tested with normalized calls | No endpoint/model qualified; disabled |

Live routes require explicit server qualification and enablement, credentials and a
reviewed budget; none are enabled in the current application. No model ID is selected
from memory or silently upgraded. Streaming tool-fragment assembly is offline tested;
network adapters currently use bounded complete JSON responses. End-to-end provider
streaming/cancellation and reasoning-item replay remain live qualification gates.

Official references inspected on 20 October 2026:
[OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling)
and [Claude client tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).
The application executes client tools and supplies their results; neither provider
response grants authorization or proves a business action completed.
