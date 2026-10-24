# Findings and proposed business actions

Analysis: 24 October 2026. Historical window: 1 December 2009–30 November 2011.
The business review is simulated; figures below are calculated from the real source.
[Definitions](metrics.md) · [Aggregate results](../results/summary.json).

| Finding | Evidence | Proposed next step |
|---|---|---|
| A modest sales increase masks fewer orders | Jan–Nov sales: £8,765,001 in 2010, £9,117,534 in 2011 (+4.0%). Invoices: 18,159 → 17,483 (−3.7%). Average invoice: £482.68 → £521.51 (+8.0%). | Investigate product mix, purchase frequency and wholesale buying patterns before treating higher sales as broader customer growth. |
| Repeat purchasing depends on the observation window | 4,186 / 5,826 customers purchased on multiple invoices in the two-year window (71.9%). Within an equally observable 90-day window, 2,454 / 5,229 repeated (46.9%). | Use a fixed window when comparing customer cohorts. Do not compare a recent customer with someone observed for two years. |
| Repeat buyers with a longer purchase gap deserve review | At 1 December 2011, 591 customers had at least two orders in the previous 12 months but none in the last 90 days. Their recorded 12-month sales: £650,317. | Review a business-approved sample to distinguish seasonal or wholesale cadence from service problems before designing a re-engagement experiment. |
| Identified-customer results do not cover all sales | Identified customer IDs cover 85.9% of sales value and 92.5% of purchase invoices. | Track identification coverage alongside customer measures; investigate why IDs are absent before generalizing. |

## A data-quality decision that changes the report

The source contains two overlapping annual sheets. Every one of the 22,523
first-sheet rows dated 1–9 December 2010 also occurs in the second sheet, including
its multiplicity. Excluding these proven copies removes £438,852.65 of positive
invoice value from a naive concatenation before the accounting exclusions. It also prevents duplicated cancellation
amounts. Raw records are retained in staging, with explicit selection flags.

After that correction, 11,812 exact repeated rows remain across source history.
They cannot be reliably classified as errors without a line ID, so the main report
retains them. In the selected window, potential repeated positive value is
£56,090.47 (about 0.29%). A sensitivity calculation that removes exact repeats
changes Jan–Nov growth from **4.02% to 4.14%**; the direction and fewer-orders finding
remain unchanged. [Quality evidence](../results/quality.json).

## Proposed experiment, after business review

Focus first on understanding the 591-customer lapsed-repeat group. A retail team
would confirm account type, expected ordering cadence, recent service issues and
permitted contact channels. If an outreach experiment is then appropriate, define
eligible customers, a comparison group, contact costs, a fixed follow-up window and
repeat-order measures before starting. This dataset contains neither that outreach
nor its outcomes, so the portfolio makes no claim of improved sales or recovered value.

The practical BA contribution is to turn an ambiguous request to “improve customer
retention” into agreed measures, a reviewable group definition and a testable next step.
