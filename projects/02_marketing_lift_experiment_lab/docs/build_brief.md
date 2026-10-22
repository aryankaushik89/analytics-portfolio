# Marketing Lift and Experiment Lab

## 1. The decision

Would I continue a campaign if its extra conversions had to cover the advertising cost? I want the answer to show the uncertainty and stop when the experiment data is unreliable.

The intended reader is a marketing analyst or campaign lead. The project adds inspectable experimentation work alongside my existing customer and fraud projects. It covers user-level data preparation, randomized comparisons, a development/evaluation split, sample-ratio mismatch, uncertainty and a financial sensitivity check.

## 2. Data choice

I checked the Criteo Uplift source and its corrected v2.1 download on October 22, 2026. The download was unavailable from the build environment. The source also documents privacy sampling and restrictions on reconstructing the original campaign lift. I have not used or redistributed any Criteo records. That public benchmark extension is deferred.

This version instead uses three authored synthetic experiments. A campaign with different effects for new and returning customers demonstrates the main analysis. A smaller, weak-effect experiment demonstrates an inconclusive result. A third extract deliberately omits control users to demonstrate a blocked decision. None of the results describe a real advertiser.

## 3. Rules set before analysis

- Randomize treatment at the user level with a planned 50/50 allocation.
- Assign an independent 40/60 development/evaluation split before generating outcomes.
- Use a fixed seven-day conversion window. The extract date allows every assignment to mature.
- Use all assigned users in the denominator, whether they saw an ad or not.
- Inspect new and returning customer groups in development. Freeze one candidate group before evaluation. Never choose a device group from evaluation outcomes.
- Report a 95% Newcombe-Wilson interval for the overall evaluation risk difference. Use a two-sided 95% interval for the one development-selected group. Other segment views are exploratory. No claim that one segment differs from another without an interaction test.
- Use a chi-square goodness-of-fit check against the configured allocation. A p-value below 0.001 blocks the experiment recommendation. Passing this check does not prove data quality.
- Treat cost per assigned treatment user and contribution per conversion as assumptions. Translate the effect interval into a net-contribution interval. This does not include uncertainty in those assumptions or prove that a larger rollout would have the same effect.
- Do not stop early or repeatedly test until significance. The synthetic extraction date is fixed.

## 4. Completion checks

The generator must reproduce the published files. SQL and pandas must agree at user grain. Event duplication, events outside the window and users with no events need explicit checks. Development and evaluation IDs must be disjoint. The primary, inconclusive and blocked paths must be exercised. Python and browser calculations must agree for every supported filter combination. Test navigation, details, downloads, empty states and a narrow layout through the supported browser. Retain executed notebook outputs, the matching script and a readable HTML report.

## 5. Interface

The dashboard has experiment, customer type and device filters. Evaluation is the default and development is clearly marked. The decision view shows conversion rates, uncertainty, sample-ratio status and cost assumptions. A group view compares the two predefined customer types. A record view traces selected synthetic users back to assignment and conversion events. Exports match the active selection. A planning view shows an approximate fixed-horizon sample size for a chosen baseline and absolute effect.
