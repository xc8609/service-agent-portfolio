# Retail customer and sales analysis

**Decision:** where should a retail trading and customer-development team focus its
next investigation and follow-up planning?

The project connects transaction analysis with practical decisions: understand
sales changes, compare repeat purchasing, and identify customer groups worth a
closer review. It builds on customer-management, commerce and payments workflows.
The operating scenario and proposed actions are simulated. The transactions are
real public data.

## Business background

In the simulated current process, a manager receives transaction exports and
compares headline sales. Separate spreadsheets answer customer and product
questions, with different definitions of an order, an active customer and a
cancellation. This makes it difficult to explain a change or agree which customer
group to investigate next.

The target process uses one documented set of measures and three connected views.
A reviewer starts with sales, examines customer purchasing patterns, and records a
specific next action with its evidence and remaining questions.

| Business question | Analysis and visual | Decision supported |
|---|---|---|
| Where did sales change? | Complete-month sales and order trends, country contributions, cancellation amounts shown separately | Choose the period or market to investigate; product mix is a follow-up question |
| Are customers purchasing again? | Repeat-buyer counts and rates, monthly cohort purchasing heatmap, eligible observation windows | Identify cohorts whose purchasing patterns merit review |
| Which groups deserve attention? | Customer counts and sales by explicit recency/frequency segments | Prioritize a group for investigation and propose a follow-up experiment |

## Data and analytical scope

[UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
contains 1,067,371 invoice lines from a UK online gift retailer, covering
1 December 2009 to 9 December 2011. Many customers are wholesalers. Fields include
invoice, product, description, quantity, invoice time, unit price, customer ID and
country. Amounts are in GBP. Source attribution is Chen, D. (2012),
[Online Retail II](https://doi.org/10.24432/C5CG6D), licensed CC BY 4.0.

The main monthly analysis ends on **30 November 2011**, so the nine days of
December 2011 do not appear as a full-month decline. Customer analysis uses the
identified-customer subset and reports its coverage. A first purchase means the
first purchase observed in this dataset, not the customer's lifetime first order.
The [metric definitions](metrics.md) own the calculation and exclusion rules.

The first release covers transaction quality, monthly sales, repeat purchasing,
cohorts and transparent customer segments. It does not require a model or an Agent.
Customer visits, assigned sales staff, follow-up tasks and contact permissions are
not present, so this analysis does not measure store conversion or staff performance.
It also does not estimate profit, lifetime value or the effect of an outreach campaign.

## Target decision workflow

1. **Prepare and reconcile.** The analyst validates the source and records how
   duplicates, missing customer IDs and cancellation records affect each measure.
2. **Locate a change.** The manager selects a complete period and reads sales,
   orders and cancellation figures together.
3. **Investigate purchasing patterns.** The analyst checks the relevant customer
   cohorts and segments, including their sizes and available observation windows.
4. **Propose an action.** The analyst records a finding, the supporting measure,
   an explanation to investigate, and the information needed before acting.
5. **Review the proposal.** A business owner chooses the next investigation or
   experiment. Any actual customer contact would need the organisation's customer
   records, permissions and operating process.

The analyst owns metric definitions and reconciliation. The business owner owns
commercial priorities and any future experiment. The dashboard presents evidence;
it does not send messages or create customer tasks.

## Success and delivery evidence

The first release succeeds when a reviewer can answer the three business questions,
trace a displayed value to SQL, and understand which next decision the result
supports. The case study should include actual findings and an example action
proposal, without presenting the proposed action as a measured improvement.

Implementation uses **Python → DuckDB SQL → aggregate CSV → visual reporting**,
with Tableau as the selected BI delivery tool. Source files and local databases
stay local; public results contain aggregate analysis. Stories, estimated effort
and six acceptance cases are in the [delivery plan](../../../docs/backlog/retail-analytics.md).

Current status: the reproducible analysis and portable three-page report are
implemented and technically verified. Native Tableau acceptance and owner review
of the findings/actions remain pending. See the [verification record](../dashboard/README.md).
