# Four-task lookup rehearsal — protocol v1

Registered before executing the comparison, 22 October 2026. QA-03 exploratory
portfolio evidence; the operator/author/scorer is Codex, with prior familiarity with
the app. This is not an independent human study or a live-model evaluation.

## Question and conditions

Can the existing workspace make an authorized enquiry easier to assemble without
losing business facts? Compare prepared evidence reading, not login, search, system
latency or end-to-end handling time.

- **A — separated sources:** a local read-only pack with transaction, case, rule and
  customer-report pages. The pack is generated from the demo's authorized APIs and
  rendered as plain labelled fields/tables. It is a simulated display baseline,
  not an observed bank legacy system. No generated answer or Agent draft is included.
- **B — integrated workspace:** the running merged app, already logged in with the
  same synthetic customer, transaction pair and saved customer statement. T1–T3 use
  manual evidence; T4 additionally inspects the existing scripted Agent draft.
  This mixed workspace condition cannot isolate a model's contribution.

Shared fixture: DEMO-4242, two DEMO STORE CAD 85 posted entries; customer statement:
“I bought once, but I see two charges for CAD 85. I cannot tell which entry is extra.
I do not have the receipt.” Recognition: one_purchase_unresolved. Matched verified
sessions for the same seeded contact in one disposable database; no financial action or real customer.
Prepare both conditions before timing. Start A at its source index and B at its
workspace entry. Reset that view between tasks; do not carry a completed answer into
the next recorded attempt. Prior knowledge cannot be removed and must be reported.

## Tasks and fixed completeness checks

| Task | Question | Required items (each counts once) | Order |
|---|---|---|---|
| T1 | What do the charge records establish? | Both posted; each CAD 85 at DEMO STORE; occurrence/posting dates; no recorded relationship; similarity alone is not proof of a duplicate. (5) | A → B |
| T2 | Is this pair already being handled, and by whom? | Matching case reference; overall status; specialist work status; assignee and queue; follow up existing work rather than create a duplicate. (5) | B → A |
| T3 | Which procedure applies and what should the representative do? | Source section/version; CA credit-card/two-posted-entry applicability; compare transaction facts; clarify purchase/relationship; reviewed referral without automatic refund/adjudication. (5) | A → B |
| T4 | Prepare a short handoff from this customer's concern. | One purchase reported; extra-entry mapping unresolved; receipt unavailable; two posted CAD 85 facts; duplicate not established; existing investigation and responsible queue; draft/recommendation is not a committed action. (7) | B → A |

If a required item is unavailable from the permitted surfaces, record that as a source
or display gap rather than invent it. Preserve the first answer/draft, then log any
correction and its source. T4's initial B artifact is the actual Agent draft; manual
additions are recorded separately. No business write is required for these tasks.

## What to record

For each of eight attempts record UTC start/end, elapsed operator wall time, actual
navigation actions, evidence locations visited, initial answer, missing items,
unsupported assertions and corrections. A location is one source page or workspace
section actually consulted. Count page changes separately from within-page movement;
do not pretend they are identical units of effort. Time includes browser-tool latency
and Codex deliberation; exclude setup, resets and unrelated work between attempts.

First-pass completeness = required items present / checklist size. Corrections do not
rewrite the first-pass score. Report raw per-task observations, not ROI or significance.
Screenshots and hashes identify the evidence pack. Generated source snapshots remain
local and out of Git; publish only the small task report and reproducible pack builder.

## Decision

Four tasks are enough for this rehearsal. Preserve failures and no-gain results. The
output is a short improvement recommendation, not an adoption threshold. Do not claim
human time saved, independent accuracy, lower operating cost or production acceptance.
A later human walkthrough can reuse these tasks if useful; no extra platform is needed.
