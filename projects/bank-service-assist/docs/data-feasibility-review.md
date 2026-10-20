# BANKING77 and banking agent benchmark feasibility

Reviewed: 18 October 2026. Scope: the owner's customer-service desktop experience,
the planned duplicate-transaction enquiry and existing-case-status workflows.
Role evidence: data provenance/quality, API contracts, decision rules and UAT.
Parent: [data plan](../../../docs/agent-data-validation-plan.md).

## Evidence and execution status

The local download remains blocked: DNS failed in the normal sandbox; automatic
approval review failed twice due to model capacity, so neither elevated command
executed. No alternate mechanism was used to bypass that review. Source pages
were read for research; their previews are not a complete local data audit.

Prepared a standard-library downloader/profiler, verified its offline parser and
overlap checks, and documented the intended source manifest. Full row counts,
class balance, duplicates, source hashes and a commit-pinned task inventory remain
pending. No model calls, benchmark runs, phone sessions or savings measurements
were made. Observations below refer to browsed `master`/`main`, which can change.

## 1. BANKING77: observed samples and proposed use

The publisher's [training CSV](https://github.com/PolyAI-LDN/task-specific-datasets/blob/master/banking_data/train.csv)
has `text,category`. For example, one query says “My account is showing a double
charge.” Another says “My refund is not showing.” These are customer statements,
not verified ledger findings. Other inspected training rows ask why a payment is
pending. Some wording is ambiguous about purchase processing versus card-payment
processing; clarification remains necessary even when an intent label is known.

The [category file](https://github.com/PolyAI-LDN/task-specific-datasets/blob/master/banking_data/categories.json)
supports the following proposed mapping. This is an authored scope decision,
not an upstream annotation or a completed business review.

| Exact upstream label | Use in our case | Missing evidence before answering or acting |
|---|---|---|
| `transaction_charged_twice` | Core duplicate enquiry | Authorized account, two transaction IDs, amount/currency, status, purchase context; equal amounts do not prove duplication |
| `pending_card_payment` | Core clarification and status explanation | Which payment the customer means, timestamp, pending/posted evidence and applicable explanation |
| `card_payment_not_recognised`, `compromised_card` | Recognition and manual fraud-handling branch | Authorized identity, customer denial and changed intent; no automatic refund or card mutation in MVP |
| `Refund_not_showing_up`, `request_refund` | Adjacent requests, scope/fallback tests | Merchant refund evidence and transaction link; neither label establishes an existing bank case |
| `reverted_card_payment?`, `extra_charge_on_statement` | Confusable neighbours | Evidence distinguishes reversal, fee, duplicate and unrelated charge |
| `unable_to_verify_identity` | Verification fallback | Backend session result, not model opinion about identity |

Preserve spelling, capitalization and punctuation in upstream labels. In particular,
`Refund_not_showing_up` and `reverted_card_payment?` must not be silently renamed.
No dedicated bank-dispute-status label was found in the inspected category list.
Do not relabel a merchant refund enquiry as case tracking. Keep all remaining
categories for explicit scope analysis, rather than discard them and report a
misleading full-dataset accuracy.

Initial discovery uses training data only. The prepared profiler will extract
three deterministic training examples per selected label once a verified snapshot
exists. This preview review did not inspect upstream test utterances. A broader
paraphrase and ambiguity review is still needed after download.

## 2. τ-bench: concrete task selection

Inspected source: [banking tasks](https://github.com/sierra-research/tau2-bench/blob/main/data/tau2/domains/banking_knowledge/tasks.json).
This is a targeted review, not a census of every task. Derived tasks must have
new IDs and a changelog; do not claim their results are official benchmark scores.

| Task | Observed purpose / score basis | Decision |
|---|---|---|
| `task_004` | Failed ownership verification and escalation; `ACTION` | Adapt the failure branch; assert no disclosure and an actual handoff record |
| `task_031` | Merchant service dispute with evidence gathering; `DB` | Adapt intake into a reviewed proposal; no autonomous dispute/refund commitment |
| `task_039` | Disambiguate selected transactions among many; `DB` | Reuse ambiguity pattern with fewer records; exclude provisional-credit optimization and card replacement |
| `task_040` | Multiple cards and prior dispute history; `DB` | Later context test; start with read-only history, not credit-limit rules |
| `task_008` | Repeated offer refusal followed by escalation; `ACTION` | Adapt escalation intent; do not require eight refusals before helping |
| `task_005` | Recovery using a special bypass code; `DB` | Exclude its recovery mechanism; author a separate unauthorized-bypass negative case |
| `task_053` | Credit-limit/dispute sequencing; `DB` | Defer: beyond MVP and dependent on artificial product rules |

### What exists, and what is not production-ready

The [data model](https://github.com/sierra-research/tau2-bench/blob/main/src/tau2/domains/banking_knowledge/data_model.py)
includes users, accounts, card transactions, verification history and transaction
disputes. These are useful schema references. Presence of a table does not prove
that the benchmark covers our complete case-status lifecycle.

The inspected [tools](https://github.com/sierra-research/tau2-bench/blob/main/src/tau2/domains/banking_knowledge/tools.py)
include account transaction lookup and `get_user_dispute_history_7291`, which
returns dispute IDs, statuses and dates. The visible lookup methods accept user
IDs; they do not establish our required authenticated session boundary.
`transfer_to_human_agents` validates a reason and returns success text, without
connecting a phone call. `get_current_time` returns a fixed simulated time.
Do not treat either as production telemetry.

The inspected [special recovery policy](https://github.com/sierra-research/tau2-bench/blob/main/data/tau2/domains/banking_knowledge/documents/doc_customer_support_special_support_codes_001.json)
explicitly defines a shared static bypass code. That explains task 005's expected
behavior but is not an authentication design to copy. Our application must reject
a caller's unsupported assertion of supervisor approval. Other dispute policies
referenced by the selected tasks were identified by document ID, but direct
retrieval of two policy files failed; their full contents remain unreviewed.
No Canadian compliance endorsement is inferred from these synthetic rules.

The [scoring guide](https://github.com/sierra-research/tau2-bench/blob/main/docs/evaluation.md)
distinguishes expected final state from required actions. Read each task's
`reward_basis`; a listed reference action is not automatically a hard criterion.
Our UAT additionally checks authorization, mandatory evidence, approval and
audit events even where the final state appears correct. Never expose evaluator
answers, future user facts or `required_documents` gold references to the live agent.

## 3. Data gaps, construction and acceptance

| Gap | How to fill it | Evidence required to pass |
|---|---|---|
| Verified customer/account context | Small authored synthetic customers/accounts plus backend-issued session scope | Another customer's ID is denied without revealing its existence; a text claim cannot upgrade scope |
| Duplicate versus pending transaction | Linked synthetic transactions with integer minor units, currency, status and fixed event times | Same wording with different ledger states produces different supported explanations; no guaranteed refund/expiry date |
| Existing case status | Synthetic cases and append-only events: opened, awaiting evidence, in review, closed; explicit unknown/conflicting cases | Status reconstructed from eligible events; no future events, invented ETA or conflation with a merchant refund |
| Policy and authority | Versioned fictional-bank decision table informed by sourced public guidance | Each required question and permitted action traces to a rule; wrong date/jurisdiction excluded; owner review status explicit |
| Staff approval and execution | Proposal, version, approval, idempotency key and operation result records | A repeated approval commits once; stale facts require refresh; an unapproved proposal changes nothing |
| Natural conversation | BANKING77 training wording as attributed inspiration plus authored multi-turn scripts | State/expected outcomes fixed first; paraphrases grouped before splitting; customer correction invalidates stale output |
| Voice and handoff | Consented role-play, labelled TTS variants, later actual test calls | Reference transcript/entity checks; telephony events plus recipient confirmation; distinguish queued/connected/failed |
| Efficiency/cost | Instrumented manual-versus-assisted task study | Time includes correction and completion; quality scored separately; no cost-saving claim from synthetic outcomes |

Minimum new fixture contract: `scenario_id`, `family_id`, `data_kind`, provenance,
fixed `as_of`, policy version, authenticated scope, initial records, timed events,
agent-visible facts, evaluator-only expectations, allowed outcomes, forbidden
actions, reviewer status and split. This is a specification, not yet a dataset.

Start with the existing ten [backlog seeds](../../../docs/bank-first-release-backlog.md).
Review three contrasts first: one pending/one posted versus two posted charges;
duplicate enquiry changing to purchase denial; and case update arriving after an
assistant draft. Add unknown-case, conflicting-status, wrong-customer, missing-policy,
prompt-injection and repeated-save cases. Design independent postcondition checks
before letting a model generate dialogue variants.

## 4. Next bounded checks

1. Resume the publisher download after the approval-service issue is resolved.
   Record the real commit, timestamps and hashes; run the full profiler.
2. Review the generated training-only samples and the per-intent counts. Resolve
   duplicate/label conflicts before freezing a derived evaluation subset.
3. Acquire a pinned τ-bench snapshot and validate selected tasks, required documents,
   initial-state overrides and score rules together. Browsed `main` pages may
   represent different cached revisions, so this must precede benchmark execution.
4. Author/review the ten local business fixtures and decision table. Keep upstream
   benchmark comparison and application UAT as separate reports.

The offline suite covers malformed CSV, quoted multiline records, unknown labels,
cross-split duplicates/conflicting labels and tampered snapshots. No full source
profile or model evaluation has passed yet.

Executed on 18 October 2026: the five new offline checks passed with the bundled
Python runtime. The repository `.venv` pytest run passed 13 tests and skipped two
DuckDB-dependent modules because the data dependency was unavailable there.
`git diff --check`, local documentation links and the raw/processed ignore rules
were also checked. These results do not validate network download or full datasets.
