# Bank service assistant data

Sprint 1 update, 19 October 2026: public TD and FCAC pages were read for the
[source register](../docs/sprint-01/evidence-register.md). The
[22 authored acceptance examples](../docs/sprint-01/scenarios.md) are synthetic
specification examples, not downloaded data, executed tests or a blind holdout.
No new operational dataset or BANKING77 file was downloaded in this activity.

Status at initial publication, 19 October 2026: **BANKING77 local download is pending**. No dataset is bundled in this repository.
No download date, local row count, source commit or checksum is claimed.
Public source previews were inspected separately for the
[feasibility review](../docs/data-feasibility-review.md).

## BANKING77

- Publisher: [PolyAI-LDN/task-specific-datasets](https://github.com/PolyAI-LDN/task-specific-datasets).
- Files: `banking_data/train.csv`, `test.csv`, `categories.json`, plus root
  `LICENSE` and `README.md` for provenance.
- Terms: publisher repository identifies CC BY 4.0. Attribute the publisher and
  [Casanueva et al., 2020](https://arxiv.org/abs/2003.04807); record adaptations.
- Expected publisher contract: 10,003 training records, 3,080 test records,
  77 categories, CSV fields `text,category`. These are not locally measured yet.
- Purpose: intent understanding and wording discovery. No account facts,
  conversation chronology, resolution outcome or audio. Customer geography is
  not established. A complaint/query label does not establish transaction truth.

## Reproduction

From the repository root, with network access and after reviewing publisher terms:

```bash
python3 projects/bank-service-assist/scripts/banking77.py download
```

The script resolves the publisher commit, downloads only five allowlisted files
from that exact revision, validates the CSV contract and atomically publishes a
snapshot under `data/raw/banking77/<commit>/`. Its `manifest.json` records each
file's actual UTC retrieval time, URL, bytes and SHA-256. An existing snapshot is
verified rather than overwritten. To reproduce it, use `download --revision`
with its exact commit. Network execution is not yet verified.

Then pass the printed snapshot directory:

```bash
python3 projects/bank-service-assist/scripts/banking77.py profile projects/bank-service-assist/data/raw/banking77/<commit>
```

Replace `<commit>` with the actual directory name. Profiling checks hashes before
reading records. Outputs go to `data/processed/banking77/<commit>/profile.json`
and `training_review_samples.json`: counts, normalized duplicates, cross-split
overlap, conflicting labels, scope counts and three deterministic training
examples per selected intent. Unicode/case/whitespace matching does not detect
all semantic paraphrases. CSV record counts must not be inferred from line counts.
Review samples are disposable generated outputs, not a place for manual labels.

Keep the original train/test files unchanged. Do not use test text for discovery
or prompt examples. Report any discovered overlap separately before selecting a
deduplicated evaluation protocol. Raw files, generated outputs and their embedded
text remain Git-ignored by the repository's existing project data rules. A small
source manifest may later be copied to the tracked data directory once verified.

## τ-bench and authored scenarios

Only public previews of selected banking tasks, tool code, data models and one
special policy were inspected. No local τ-bench checkout, pinned revision or
benchmark execution exists. These are synthetic scenarios and benchmark rules,
not an operating bank's customer records or approved policies. See the review for
task IDs, exclusions, required adaptations and tests still needed.

Future fixtures must declare `data_kind`, provenance, fixed clock, policy version,
authorization scope and expected permitted outcomes. Do not connect BANKING77
queries to fabricated transactions and label the resulting conversation real.
No audio or real customer information is collected by these scripts.

## S02 contract fixtures, authored 19 October 2026

The v0.4 JSON payload and calendar fixtures in `specs/contracts/` are authored synthetic specification inputs. They were not downloaded, do not contain real customers and are not model-evaluation results. The 26 October holiday is deliberately synthetic. Source: this portfolio design and owner decisions D-17–D-22. Public dataset terms remain separate; no new BANKING77 download is claimed.

## Runtime seed fixtures — 20 October 2026

The authored `services/api/bank_api/fixtures.py` generator (repository root) creates two synthetic customers, masked demo cards, seven transaction records, fixed staff personas and explicitly fake verification assertions. Version: `bank-lookup-synthetic-v1`. It is not downloaded bank data, does not contain PAN/CVV, and does not measure real outcomes. Database instances and generated records are excluded from Git. BANKING77 remains optional and was not downloaded by this runtime implementation.

## DEV-04 authored case fixtures — 20 October 2026

`services/api/bank_api/case_fixtures.py` (repository root) extends the runtime seed
to `bank-cases-synthetic-v2`: three fake cases, a customer-safe timeline, linked
work ownership/due dates and an unapproved commitment used for disclosure tests.
DEMO-CASE-001 covers both $85 DEMO STORE entries. No actual bank/customer data
was downloaded; staff names and progress are invented demonstration records.
Own fixture code is MIT; public dataset terms are unchanged. Generated databases
remain excluded from Git. Dates/deadlines are test inputs, not bank service promises.
