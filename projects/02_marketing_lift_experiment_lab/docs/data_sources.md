# Data sources and terms

Reviewed October 22, 2026.

## 1. Data actually used

All assignment and purchase records in this project are authored synthetic data from generate_data.py, seed 89. They use no real user records and are released with this project's MIT licence. The generator parameters and planted failure are visible in the code and data/scenario.json.

There are three independent fictional experiments. Customer type, device, treatment and the development/evaluation split are assigned before outcomes. Treatment users are exposed with probability 0.78. The baseline probabilities are 0.04 for new customers and 0.11 for returning customers. An exposed user's probability increases by the experiment's configured effect. Purchase times, re-deliveries, extra purchases and out-of-window cases are generated as documented in the code.

## 2. Criteo benchmark extension

I checked the [Criteo Uplift source](https://ailab.criteo.com/criteo-uplift-prediction-dataset/) and its corrected v2.1 download. The download returned an unavailable response from this build environment. I used no Criteo data, sample, features or derived estimates.

Criteo documents privacy sampling, an earlier release correction and CC BY-NC-SA 4.0 terms. Any later benchmark extension must use the appropriate release, preserve its terms and distinguish benchmark estimates from original advertiser lift. This extension remains deferred, not completed.

## 3. Method references

- [NIST difference-of-proportions interval reference](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/diffprop.htm). The implementation uses Wilson bounds combined with the Newcombe difference method. Its formulas are listed in metric_definitions.md.
- [Microsoft Research on sample-ratio mismatch](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/). This informed the allocation diagnostic and the decision to investigate an SRM before interpreting outcomes. The project's threshold is a stated local choice of 0.001.
- [SciPy chi-square distribution documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2.html). Used for the Python survival probability.

These references explain methods. They do not supply this project's user records, financial assumptions or measured results. Company names do not imply a partnership or endorsement.
