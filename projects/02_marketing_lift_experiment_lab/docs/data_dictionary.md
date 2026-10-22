# Data dictionary

## 1. Assignment deliveries

data/assignments.csv.gz has 118,202 rows, including 75 identical re-deliveries. There are 118,127 unique retained users. The grain before deduplication is one delivery of a user assignment. IDs are globally unique across experiments.

| Column | Meaning |
| --- | --- |
| experiment_id | retargeting, small_test or missing_controls |
| user_id | Synthetic user identifier, prefixed with its experiment |
| assigned_at | UTC timestamp of the treatment or control assignment |
| arm | Control or Treatment, with a planned equal allocation |
| customer_type | New or Returning, set before treatment |
| device | Desktop or Mobile, set before treatment |
| split | Development or Evaluation, independently assigned before outcomes |
| exposed | 1 when the synthetic user sees the ad, otherwise 0. Only treatment users can be exposed |

The intended experiments have 100,000, 5,000 and 18,000 users. The broken extract retains only 13,127 of the third experiment's users after some control assignments are deliberately omitted. This omission is a planted failure, not normal exclusion logic.

## 2. Purchase event deliveries

data/conversion_events.csv has 9,570 rows, including 105 identical event re-deliveries. The grain is one delivery of a purchase event. Several event IDs can belong to one user.

| Column | Meaning |
| --- | --- |
| experiment_id | Experiment whose assigned population generated the event |
| user_id | Synthetic user associated with the event |
| event_id | Unique purchase identifier before re-delivery |
| event_at | UTC timestamp of the purchase |
| event_type | purchase |

The source includes purchases before assignment and after the seven-day window, as well as second purchases. Those cases make the window and user-grain checks inspectable. The broken extract leaves purchase events for some users whose assignment rows are missing. These are reported as orphan users.

## 3. Derived user outcomes

Both pandas and sql/user_outcomes.sql produce one row per retained assigned user, with the assignment fields above plus these measures.

| Column | Meaning |
| --- | --- |
| purchases_in_window | Deduplicated purchases at or after assignment and strictly before seven days later, observed by the extract date |
| converted | 1 if purchases_in_window is greater than zero, otherwise 0 |

No purchase event is a valid zero outcome for an assigned user in the two intact synthetic experiments. That rule is part of the generator's complete-event assumption. In a real system I would verify outcome capture separately before treating an absent event as zero.

## 4. Aggregates and interface data

outputs/aggregate_counts.csv has one row per experiment × split × customer type × device × arm. users is the assignment denominator; conversions is the sum of binary conversion flags; exposed is the sum of the exposure flags. The aggregate table has 48 rows.

dist/data.json includes these aggregates, experiment-level quality flags, the development-selected group, 144 example users and their deduplicated events. The examples take the first three retained users in each aggregate cell. They are a tracing aid, not a random sample or a separate estimator.

outputs/filter_results.csv and outputs/python_oracles.json contain 54 supported filter selections, including withheld diagnostics for the deliberately broken experiment. The dashboard suppresses effect and money results for blocked experiments. The oracle file retains diagnostic calculations to test that the blocking decision does not depend on a convenient-looking effect.

data/scenario.json records seed 89, the fixed extract date of March 1, 2026, the seven-day window, the intended 50/50 allocation, the SRM threshold of 0.001 and the hypothetical CAD cost defaults.
