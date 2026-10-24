# INV-04 — evidence retrieval and research drafts

24 October 2026. Business question: after comparing the annual figures, which
reported evidence helps explain the changes, and what still needs investigation?

The workflow is **question → scoped evidence tools → cited draft → analyst edits**.
The draft stays beside existing notes until the analyst explicitly appends it.
It never marks the work reviewed or saves a final version; those are INV-05.

## Application and runtime boundaries

The investment application owns its runtime in `src/research_brief/agent/`, its
API in `api/research_api/` and its UI in `web/`. There are no bank-runtime imports,
bank credentials, shared customer records or ValueFocus code dependencies.

ValueFocus informed three principles: stable evidence identities with lineage,
an explicit tool catalogue, and checking the proposed evidence before rendering
an answer. This implementation uses one small loop and the existing calculator;
it does not introduce investor personas, orchestration layers or a vector database.

`run_research(packet, passage_pack, question, provider=None, max_tool_calls=8)`
owns one validated evidence snapshot, tool dispatch, the call budget and final
reference validation. A provider implements `name` and `next_step(question, history)`.
It returns one tool request or a final plan of metric and passage IDs.

The current `offline-scripted-v1` provider exercises the same four tool calls and
selects evidence by the question's topic. No external model is called. Numeric
sentences are rendered from calculator outputs; explanations are the retrieved,
attributed summaries. This verifies the workflow and evidence boundaries, not
live-model reasoning quality. A future provider can use the same contract.

## Read-only evidence tools

| Tool | Purpose | Boundary |
|---|---|---|
| `list_sources` | Identify the selected registered company report. | No arbitrary source discovery or URLs. |
| `read_facts` | Read the selected report's numeric facts and their locators. | Source and periods remain those of the request snapshot. |
| `compare_periods` | Call the existing Python comparison logic. | Model text cannot supply formulas or alter the source facts. |
| `read_passages` | Retrieve the relevant registered commentary summaries. | Text is evidence, never an instruction or a tool definition. |

The runtime accepts at most eight tool calls. Unknown tools, invalid arguments,
unretrieved final references or a provider failure return an incomplete result.
Missing evidence produces a specific follow-up question rather than an explanation
with no source. No tool writes a note, changes permissions, executes code or trades.

Final plans contain references, not unrestricted numeric claims. The renderer
separates calculated facts from company explanations and builds citations from
the actual retrieved evidence. The operating-income summary gives context; the
cause and size of a margin improvement still require further investigation.

## API and draft contract

`POST /v1/research/runs` accepts exactly:

```json
{
  "source_id": "msft-ar2025",
  "question": "What changed in operating cash flow?",
  "expected_source_hash": "SHA-256 from the loaded comparison"
}
```

The question is trimmed and bounded to 1–1,000 characters. The source must be
registered; a changed report hash returns 409 and requires a new comparison.
The client cannot choose a provider, change the tool budget or submit file paths.

The response includes `status` (`draft` or `incomplete`), the question, source ID/hash,
provider identity, `findings`, `open_questions`, `trace` and `issues`. Each finding
is either `calculated_fact` or `reported_explanation`, with citations containing
evidence ID, label, URL and locator. Trace records the tools actually executed.
An unreadable registered file is a recoverable 503; an absent optional commentary
pack leaves explicit research gaps. The manual comparison remains available.

## UI acceptance

- Generate only against a loaded comparison and the current question.
- Show **Facts / Company explanations (summarized) / Open questions**, with citations.
- Changing the report, question or comparison invalidates the displayed/in-flight draft.
- Reject a response that belongs to another source, hash or question.
- Preserve analyst notes when generation fails or evidence is incomplete.
- Append a draft only on an explicit click, preserving existing notes and attribution.

[Story and acceptance criteria](../../../docs/backlog/investment-research.md#inv-04--produce-a-bounded-evidence-backed-agent-draft)
· [Executed verification](agent-acceptance.md).
