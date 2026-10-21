# Tableau draft verification — 2026-09-28

## Artifact and scope

`complaint_operations.twb` contains 13 worksheets and two dashboards:
Complaint Overview; Text Coverage and AI Readiness. The workbook references the
local aggregate CSV without embedding records. The final canvas is authored at
1200 × 740. The installed app is Tableau Desktop Free Edition 2026.2.3 on macOS.

This is a **draft, not an accepted dashboard release**. BA trace: simulated
operations lead US-2, requirements/data validation/reporting evidence. No user or
stakeholder acceptance is implied.

## Checks actually performed

- Re-ran `scripts/export_tableau.py` against the existing real-data DuckDB database:
  status `reconciled`, 5,228 aggregate rows. All seven product totals matched.
- Source/CSV totals: 27,011 complaints; 6,409 narratives; 26,620 timely Yes;
  391 timely No; zero unknown timeliness. No public narrative: 20,602.
- Opened the two-page workbook in Tableau after repairing XML structure errors.
  Tableau rendered the text-readiness page with 27,011 complaints, 6,409 narratives
  and 23.7% coverage. The five displayed team totals and seven coverage bars were
  inspected. These are real Tableau outputs, not an HTML mockup.
- Saved through Tableau once to confirm native serialization.
- Initial layout was too wide/tall for the editor. Subsequently authored a compact
  layout, smaller headings/notes and removed crowded stacked-bar labels.
- XML parses successfully; both dashboards and all worksheet references exist.

## Outstanding acceptance and tool limitation

After the compact layout edit, Tableau logged a loading warning. The automation
interface repeatedly returned the underlying blank Book5 window instead of the
warning, or timed out. A temporary relative-path experiment was reverted to the
original absolute CSV path. (Public copy, 2026-10-21: the path now points to
`../results`; this portable path has not been re-verified in Desktop.) The **latest compact revision has not been visually
accepted**, and the loading warning still needs inspection. Do not represent this
as a verified portable workbook or publish it yet.

Product/team/channel/date filter controls and shared filter groups exist, but no
successful filter interaction, empty-selection check or reset test is claimed.
The timeliness KPI and final overview page still need visual reconciliation.
No final screenshots or public URL were produced. No model/SQL logic changed;
unit tests were not rerun in this dashboard-only session.

## Resume acceptance

1. Bring the actual loading warning or `complaint_operations` window to the front.
   Inspect and resolve the warning; use Edit Connection if the CSV cannot be found.
2. Inspect both 1200 × 740 pages; verify no clipped source notes or overlapping labels.
3. Reconcile all five base counts and weighted rates. Expected rates rounded to one
   decimal: narrative coverage 23.7%; timely response 98.6%.
4. Apply each product filter; compare complaint/narrative counts to `README.md`.
   Verify both dashboards, not just the sheet hosting the filter.
5. Test date/channel/team intersections, an empty selection, and reset to the full
   month/all categories. No data must not be shown as a successful zero-rate result.
6. Save in Tableau, close/reopen without warnings, and export final screenshots.
   Only then update the draft status and checked UAT items.

## Follow-up inspection — 2026-09-28

The compact 1200 × 740 revision is now open in Tableau. Both dashboards were
inspected by switching through the Window menu. The overview visibly shows
27,011 complaints, 6,409 narratives, 98.6% timely response and zero unknowns.
All seven product volume labels match the expected CSV totals. Response-category
labels (20,084; 2,558; 1,707; 2,431; 231) also reconcile to 27,011.
The text page shows 20,602 records without public narratives, along with 23.7%
coverage and the expected headline counts. Most layout content now fits; the last
sentence in the AI-readiness note is truncated and still needs shortening.

Outstanding issues found during this inspection:

- The saved XML has product filters without a shared `filter-group`; other filter
  groups remain. Cross-sheet product filtering must be corrected/verified in
  Tableau before the on-canvas “all filters apply to both pages” claim is accepted.
- The native log reports a temporary normalized narrative-coverage column warning
  during rendering. Visible headline values are correct, but a clean reopen and
  warning review remain necessary.
- Export Image reached the native Save Image call in Tableau's log. The automation
  interface cannot access that dialog; no image file was saved by the agent.
  The user has been asked to cancel that dialog and bring the main window forward.
- Product/team/channel/date interactions, empty selection and reset are still not
  passed. No new classifier or model tests were run.

The initial business interpretation and additional product-level timeliness checks
are recorded in [findings.md](findings.md). No stakeholder UAT approval is implied.
