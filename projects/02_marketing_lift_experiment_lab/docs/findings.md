# What I found

## 1. The main synthetic campaign supports a useful incremental effect

There are 30,003 treatment and 30,282 control users in the main evaluation set. Of these, 2,407 treatment users and 2,031 control users convert in the first seven days.

| Measure | Result |
| --- | --- |
| Treatment conversion | 8.02% |
| Control conversion | 6.71% |
| Absolute lift | +1.32 percentage points |
| 95% lift interval | +0.90 to +1.73 percentage points |
| Estimated extra conversions / 1,000 treated | 13.16 |
| Full-experiment SRM p-value | 0.3493 |
| Evaluation SRM p-value | 0.2558 |

At CAD 0.60 cost per assigned treatment user and CAD 90 contribution per extra conversion, estimated net contribution is CAD 584 per 1,000 treated. Its interval is CAD 209 to CAD 960. The entire interval is above zero under these fixed assumptions. I would take this to a measured follow-up rollout, while checking whether the audience and costs remain comparable.

The recommendation changes when the cost changes. At CAD 1.60 per treated user, the main campaign's net interval is below zero. This is why the conversion result and the economic recommendation need separate explanations.

## 2. Development selects returning customers

Using development outcomes only, returning customers have the larger lower interval bound. That group is fixed before evaluation. In evaluation, it has 24,242 users and +2.58 percentage points of lift, with an interval from +1.76 to +3.41.

This is a secondary check. The group was selected independently of its evaluation outcomes, but I have not established a statistical interaction with new customers or a family-wise error guarantee across all comparisons. Device slices remain exploratory.

## 3. The small test shows why an honest uncertain answer matters

The small evaluation has 1,450 treatment and 1,541 control users. It has 83 treatment conversions and 105 control conversions. The estimated difference is -1.09 percentage points, with an interval from -2.83 to +0.66.

The conversion interval includes zero. I would not describe that as evidence of no effect. At the default cost, the upper net bound is only about CAD -5 per 1,000 treated. At CAD 0.30, the net interval crosses zero and the decision is inconclusive. I would check the actual cost, decide whether another test is worth running and plan its sample size before collecting more data.

## 4. The broken extract needs investigation first

The deliberately broken experiment retains 13,127 users after some control assignment rows are omitted. There are 349 purchase users with no retained assignment. The allocation strongly fails the configured 50/50 SRM check.

I withhold conversion-effect and contribution recommendations in the interface. The cause is planted and known here. In real work I would trace assignment, extraction filters and event joins before interpreting a campaign effect. Filtering to a subgroup does not repair an incomplete denominator.

## 5. What these findings do not establish

The campaigns, ad exposures and conversions are synthetic. No result is a real advertiser performance estimate. The financial inputs are hypothetical and held fixed. The work does not establish long-term value, a channel attribution model, a live platform integration, independence between households or absence of user interference. A larger rollout may have a different audience and cost structure.
