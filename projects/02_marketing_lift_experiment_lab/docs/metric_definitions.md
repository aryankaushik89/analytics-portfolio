# Metric definitions

## 1. Population and outcome

An assigned user is a unique retained user_id after identical assignment re-deliveries are removed. An evaluation user has split = Evaluation. The split is assigned independently of treatment and outcomes.

The conversion window is [assigned_at, assigned_at + 7 days), bounded by the fixed extract timestamp. A purchase at the start is included. A purchase exactly seven days later is excluded. All assignments have matured before the extract date.

A converted user has at least one qualifying, deduplicated purchase. Several purchases do not add converted users. Treatment users without ad exposure stay in the denominator. The primary comparison is intention-to-treat.

## 2. Treatment effect

Treatment rate pT = converted treatment users / assigned treatment users.

Control rate pC = converted control users / assigned control users.

Absolute lift d = pT - pC. The dashboard reports 100 × d in percentage points. It does not label a percentage-point difference as a relative percentage increase.

Extra conversions per 1,000 treated = 1,000 × d. This is an estimated increment relative to the randomized control baseline, not the total treatment conversions. It is not an estimate per 1,000 total randomized users.

## 3. Confidence interval

The Wilson score interval for each rate uses z = 1.959963984540054. Let its treatment bounds be LT and UT, and control bounds LC and UC.

Newcombe lower bound = d - sqrt((pT - LT)^2 + (UC - pC)^2).

Newcombe upper bound = d + sqrt((UT - pT)^2 + (pC - LC)^2).

The bounds are limited to [-1, 1]. If either arm has no users, the difference and bounds are undefined. Two zero-conversion arms still have a nonzero-width interval. The interval is pointwise at 95%, not a simultaneous interval across every dashboard slice.

The primary result is all evaluation users in the main experiment. One development-selected customer group has a secondary evaluation interval. Other customer and device slices are exploratory. No family-wise error guarantee or formal interaction result is claimed.

## 4. Quality gate

The expected arm counts use a preconfigured treatment share of 0.5. The SRM chi-square statistic is the sum of (observed - expected)^2 / expected across the two arms, with one degree of freedom. A p-value below 0.001 flags the experiment.

A full experiment is blocked by an SRM flag or any purchase users without an assignment record. A current selection with an SRM flag is also blocked. Filters cannot clear the full-experiment block. The deliberate broken case is expected to fail. Passing is a useful diagnostic, not proof of a sound experiment.

The Python value uses scipy.stats.chi2.sf. Browser values use a complementary-error-function approximation for one degree of freedom. The numerical comparison tolerance is 1.5e-7 in absolute probability, with the same classification for all supported selections.

## 5. Financial scenario and recommendation

Let v be hypothetical CAD contribution per extra conversion and c be hypothetical CAD cost per assigned treatment user.

Net contribution per 1,000 treated = 1,000 × (d × v - c).

The lower and upper net bounds apply the same transformation to the conversion-effect bounds. Cost and contribution are held fixed, with v at least zero. This does not model uncertainty in either money input.

At positive v, break-even absolute lift = c / v. At v = 0 a positive cost cannot be covered. At zero cost and zero contribution the interval is zero and the economic decision stays inconclusive.

The decision first checks data quality and the split. Development gets Development only. In evaluation, a net lower bound above zero supports Worth a follow-up rollout. A net upper bound below zero gives Does not cover assumed cost. Otherwise the answer is Inconclusive at this cost. A rollout recommendation in an exploratory slice is labelled exploratory and should generate a new test.

## 6. Planning sample size

The planner uses the normal approximation for two independent binomial proportions with equal allocation, two-sided alpha = 0.05 and power = 0.8. It assumes an increase from baseline p to p + delta. It rounds the per-arm sample size upward.

For a 7% baseline and a 1 percentage-point increase, the estimate is 10,890 users per arm. This is a fixed-horizon planning calculation, not observed power or a posterior probability. It does not adjust for clustering, missingness, sequential monitoring or multiple primary outcomes.
