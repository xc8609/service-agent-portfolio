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

The target process uses one documented set of measures and three complementary
views. A reviewer starts with sales, examines customer and product purchasing
patterns, and records a specific next action with its evidence and remaining
questions. This draws on the owner's sales-associate-system experience: turning
customer records into useful priorities for a business team.

| Business question | Analysis and visual | Decision supported |
|---|---|---|
| What explains the difference between sales growth and order decline? | Comparable-month trends, distinct-order/average-value measures and a customer order-change bridge | Identify which observed customer components contribute to the change |
| Which customer groups deserve attention? | Counts and sales by explicit recency/frequency groups, repeat measures and cohort activity | Prioritize a group for investigation and inspect the strength of its evidence |
| Which products contribute to the purchasing pattern? | Product value changes, purchase-invoice penetration and customer-group product preferences | Choose a product or mix change to review with merchandising and customer-development colleagues |

The [industry/design review](client-development-design.md) connects this workflow
with luxury retail client development: client-portfolio review, repeat business
and data quality. The actual observations remain those of the source retailer.

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

The scope covers transaction quality, a fact/dimension analytical model, sales,
customer purchasing and product preferences. Customer visits, assigned sales staff,
follow-up tasks and costs are not present. The case therefore uses observed
purchasing to support review priorities, rather than estimating store conversion,
staff performance, profit or outreach effects.

## Target decision workflow

1. **Prepare and reconcile.** The analyst validates the source and records how
   duplicates, missing customer IDs and cancellation records affect each measure.
2. **Locate a change.** The manager selects a complete period and reads sales,
   orders and cancellation figures together.
3. **Investigate purchasing patterns.** The analyst reconciles customer components
   of the order change, checks cohorts/groups and their observation windows, and
   examines associated product value and purchase patterns.
4. **Propose an action.** The analyst records a finding, the supporting measure,
   an explanation to investigate, and the information needed before acting.
5. **Review the proposal.** A business owner chooses the next investigation or
   experiment. Any actual customer contact would need the organisation's customer
   records, permissions and operating process.

The analyst owns metric definitions and reconciliation. The business owner owns
commercial priorities and any future experiment. The dashboard presents evidence;
it does not send messages or create customer tasks.

## Success and delivery evidence

The case succeeds when a reviewer can answer the three business questions,
trace a displayed value to SQL, and understand which next decision the result
supports. The case study should include actual findings and an example action
proposal, without presenting the proposed action as a measured improvement.

Implementation uses **Python → DuckDB staging/facts/dimensions → diagnostic marts
and Tableau exports → visual reporting**. Source files, local databases and
customer-level exports stay local; public results contain aggregate analysis.
Stories, estimated effort and acceptance cases are in the
[delivery plan](../../../docs/backlog/retail-analytics.md).

The baseline reproducible analysis and portable report have technical evidence.
The model and interactive diagnosis increment is tracked as RA-05/06; native
Tableau acceptance and owner review are recorded separately in the
[verification record](../dashboard/README.md).
