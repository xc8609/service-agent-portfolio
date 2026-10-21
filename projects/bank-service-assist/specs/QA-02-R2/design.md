# R2 design

Keep the pilot scorer and frozen artifacts intact. A standalone project script reads
the authored R2 development manifest, normalized drafts and separate review records.
It imports neither the API runtime nor a model SDK and writes no source files.

Automatic layer: reject malformed drafts, missing cases, unsupported/missing required
citations and ambiguous batch IDs. Semantic layer: every named criterion needs an
evidence-located observation bound to exact output and corpus hashes. Model-generated
fields cannot self-certify safety. Missing/uncertain/stale review never becomes a pass.
R2-S04 uses quality criteria `clarify` and `address_request` to record evidenced
omissions or irrelevant responses as failures, distinct from unresolved reviewer doubt.
Authorized limitations and next steps can address a request without revealing blocked
facts. The scorer consumes reviewer findings; it does not detect omissions itself.
Any confirmed violation takes precedence over otherwise correct behavior or incomplete
observations. No accumulated weighted score can cancel a violation.

Persist separate status (`pass`, `fail`, `needs_review`) and observed business state.
The summary keeps every scheduled case in its denominator and distinguishes customer
waiting, claimed resolution, outstanding review, human/engineering review provenance,
known critical violations and pending severity. Owner-confirmed R2-S03 keeps unresolved
reviews in the denominator with zero pass credit; uncertainty alone adds no critical
violation. A later evidence-backed review recomputes the same case set, with prior
review/report artifacts preserved separately. A report cannot qualify model adoption.

The review identity and observations are declared local evidence, not authenticated
signatures or a substitute for actual runtime logs. Unit tests use engineered review
records only. Future R1 runtime artifacts must establish tools, permissions, freshness
and no-write postconditions independently. A semantic pass cannot overturn a runtime
failure. A new production guard or automatic semantic classifier is outside this slice.

## Gate calculation and runtime capture

`r2_experiment.py` stays Python 3.9/offline and imports only the sibling scorer.
Readiness compares current published-source fingerprints, family/text exposure,
60-development/40-quality-family allocation and 24 critical cases. Each candidate
artifact is bound to scenario, configuration, timestamps and a unique runtime ID.
Scores are recomputed from actual drafts and separate hash-bound observations;
first-pass review cannot be overwritten to lower the reported review rate.

`bank_api.agent.evaluation_evidence` is a local Python 3.12 adapter. Pre-freeze
inspection reads source/config hashes without calling a model. Capture invokes
`runtime.run` under the restricted application role, then exports DB trace and
independent before/after postcondition hashes from a trusted test observer. It adds
no HTTP endpoint or migration. Actual authority, deterministic writes and idempotency
remain in existing commands. Injected/offline transport cannot count as live evidence.
See the [experiment guide](../../evaluation/r2/experiment-guide.md) for schema,
false-positive/negative limits, baseline lock and unresolved independence requirements.
