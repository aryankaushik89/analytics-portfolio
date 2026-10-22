# How I would explain this project

## 1. A short explanation

I built this to show how I would decide whether a campaign created useful incremental conversions. I started with user assignments and purchase events, kept the randomized groups intact and checked the same user-level result in Python and SQL. Then I put an interval around the lift and compared it with a cost assumption. The dashboard also has a small inconclusive test and a broken extract, because a useful tool needs to know when to stop short of a recommendation.

The data is synthetic. I am showing the analytical method and the implementation, not claiming a real campaign result.

## 2. Why not compare only people who saw an ad?

Exposure happens after assignment. People who saw an ad can differ from people who did not. Keeping every assigned treatment user gives an intention-to-treat comparison with the randomized control group. Exposure is available for tracing, but it is not a filter for the effect estimate.

## 3. Why keep users with no purchase records?

They belong in the assigned population. Joining only purchase users would remove the non-converters and corrupt the denominator. I use a left join and check the output grain. In these intact synthetic experiments the event process is complete. With real data I would verify capture before assuming a missing event means no conversion.

## 4. What does the interval mean?

It quantifies sampling uncertainty under the stated independent-user assumptions. The main result is +1.32 percentage points and its 95% interval is +0.90 to +1.73. I would not say there is a 95% probability that this fixed true effect lies in this particular interval. The method is designed for long-run coverage across repeated samples.

## 5. Why development and evaluation?

I use development to choose one customer group, then hold that choice fixed when looking at evaluation. I also test that changing evaluation outcomes cannot change the selection. The overall evaluation comparison remains primary. Other interactive slices are exploratory. I have not done a formal interaction test or claimed a multiple-comparison guarantee.

## 6. Is a statistically positive effect enough?

It needs to be useful at the actual cost. Here I show hypothetical contribution per extra conversion and cost per assigned treatment user. At the defaults the main campaign's whole net interval is positive. At a higher cost it is negative. The money result holds the assumptions fixed, so it is not a realized profit measure.

## 7. What makes the broken example important?

Some control assignments are missing. The resulting allocation fails an SRM check, and 349 purchase users have no assignment record. I block the recommendation even if the observed conversion difference looks attractive. A subgroup filter cannot fix the full denominator.

## 8. What did I verify?

SQLite and pandas agree on user IDs, purchase counts and conversion flags. The targeted tests cover duplicate events, time boundaries, zero conversions, missing arms, development isolation, cost changes and blocked decisions. JavaScript matches Python for all 54 supported filter selections. I also used the browser to check controls, record details and the actual downloaded CSVs.

## 9. What would I do next with real campaign data?

I would agree on randomization unit, eligibility, costs, outcome capture and a fixed analysis plan before the test. I would check clustering or interference, give every user the full outcome window and preserve assignment logs. I would decide which comparisons are primary and adjust the testing plan if there are several. A public benchmark is a separate extension; the Criteo download was unavailable here and is not part of this result.
