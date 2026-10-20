# BA-08 design rationale

BANK-S02-v0.4

Keep the shared contract as the source of truth. Separate identity, assignment and disclosure; separate contact, case and work states; separate model proposals from trusted execution. Use durable events and receipts for asynchronous continuation. Field-level DTOs exclude internal notes before model or customer feedback.

Contract links and acceptance criteria are in [spec.md](spec.md). State/database/runtime tests will validate implementation; schema checks alone cannot prove access control or transactional correctness.
