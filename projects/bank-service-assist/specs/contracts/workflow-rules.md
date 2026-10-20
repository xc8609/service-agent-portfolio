# Rules and state review v0.2

BANK-SDD-v0.2

- **SR-01 — Accepted D-11:** Ordinary representatives read only authorized transaction context; financial actions stay external and privileged.
- **SR-02 — Accepted D-12/D-13:** Routine referral is asynchronous; specialists investigate; the shared feedback queue contacts customers.
- **SR-03 — Accepted D-14:** Human callback first. App messages are deferred. Reverify identity before private disclosure.
- **SR-04 — Accepted D-14:** One service day for specialist acceptance; two from submission for investigation; one after approved result for first callback attempt. Progress update by investigation deadline if unfinished; no reset of overdue history.
- **SR-05 — Accepted D-14; fixture detail pending:** Service calendar Mon–Fri 09:00–17:00 America/Winnipeg, configured holidays excluded; one service day is eight service hours. Store UTC instants and calendar version.
- **SR-06 — Accepted D-16/D-19:** At most three actual callback attempts including the first within three service days; at most one per service date. Exhaustion or elapsed window leads to responsible-person review, never automatic resolved closure.
- **SR-07 — Accepted D-14:** Normal closure requires authorized findings, completed/no required actions, verified feedback and no remaining work. Silence, sent messages and pending funds do not prove resolution.
- **SR-08 — Accepted D-20; deduplication is an engineering proposal:** Overdue investigation retains its original specialist and original deadline. Notify the responsible lead and create customer progress work in the feedback queue. The specialist proposes the next update time; the responsible lead confirms it. Preserve original overdue history. The agent may gather evidence, remind and draft, but cannot commit a completion date.
- **SR-09 — Accepted D-21:** Feedback staff preserve the customer statement and new evidence, and route disputed findings to specialist re-review. An explicit complaint request creates an independent complaint-intake record without waiting for re-review. Both tracks link to the original case and keep independent ownership/status. Objection or silence never implies resolved closure.
- **SR-10 — Engineering proposal:** All mutations require trusted actors, version checks, unique operation keys and atomic domain/audit/outbox commit; LLM cannot approve.
- **SR-11 — Engineering proposal:** Agent tool access is scoped, bounded and read/proposal only; source content is untrusted data and no raw hidden reasoning is logged.

- **SR-12 — Accepted D-18:** A technical failure with dial_state=not_placed does not consume contact quota. Persist the fault and preserve all original deadlines. A placed unanswered call consumes one contact attempt. The server derives counting from trusted call evidence; the agent cannot override it.

Separate case, investigation, feedback, proposal and agent-run states. Lead review is not resolved closure. D-16 approves retry exhaustion review, not automatic administrative closure. DEV-13 responsibility and parallel-routing rules are accepted in D-20/D-21; detailed contracts remain candidates. Business acceptance does not establish implementation.

- **SR-13 — Accepted D-19:** First actually placed callback service date is day 1; the retry window ends at 17:00 America/Winnipeg on the third service date, excluding configured holidays and weekends. At the deadline, unresolved feedback enters lead review even if fewer than three calls occurred; no extension or automatic resolved closure. Before the first placed call, the original first-callback target still applies. Never-placed technical faults do not start or reset this window.

- **SR-14 — Accepted D-22:** After contact quota or window exhaustion, the responsible lead may approve a reasoned new contact plan or a review hold with a named owner and review date. Preserve all original attempts, deadlines and approval history. Never reset history or mark the case resolved merely because the customer did not answer. Agent suggestions cannot authorize the new plan or hold.
