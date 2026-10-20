# Requirements, detailed design and acceptance

Each story has one folder and four linked files:

```text
DEV-07/
  spec.md          User story, scope, rules and acceptance criteria
  design.md        Components, data, interfaces and failure behavior
  tasks.md         Implementation and verification work
  acceptance.md    Actual evidence and remaining gaps (not assumed passes)
contracts/         Shared permissions, model, tool/command and API schemas
```

| Area | Stories / design |
|---|---|
| Business analysis | BA-01–05: problem, stakeholders, current/target flow, requirements |
| Shared detailed design | BA-06/07/09: rules, data and APIs; [contract index](contracts/interface-notes.md) |
| Authorized investigation | [DEV-02](DEV-02/spec.md), [DEV-03](DEV-03/spec.md), [DEV-04](DEV-04/spec.md), [DEV-05](DEV-05/spec.md) |
| Reviewed records and referral | [DEV-06](DEV-06/spec.md), [DEV-07](DEV-07/spec.md) |
| Agent and provider integration | [DEV-08 design](DEV-08/design.md), [DEV-09](DEV-09/spec.md) |
| Data/BI evidence | [DEV-10](DEV-10/spec.md) |
| Specialist results and feedback | [DEV-11](DEV-11/spec.md), [DEV-12](DEV-12/spec.md), [DEV-13](DEV-13/spec.md) |
| Quality and packaging | [QA-01](QA-01/spec.md), [OPS-01](OPS-01/spec.md) |

Scheduling belongs in [delivery planning](../../../docs/backlog/README.md), not a
second copy here. Runtime source belongs in `services/api/` and `apps/web/`.
[Agent source boundary](../../../services/api/bank_api/agent/README.md) is explicitly
planned; a complete tool schema does not imply an implemented Agent or command.

D-23–D-25 are recorded in the [intake refinement](DEV-07/referral-intake-review.md).
Only accepted business rules are binding; detailed field representations remain
technical candidates until contracts and tests are updated together.
