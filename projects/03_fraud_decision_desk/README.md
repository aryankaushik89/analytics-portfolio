# Fraud Decision Desk

This project asks a narrower question than a standard fraud classifier: **given a limited review team, which transactions should enter the queue?**

I use a chronological model, calibration data, a validation period for the threshold choice and a final test period. The dashboard lets the score cutoff and daily review capacity change independently, so the trade-off between fraud coverage and false positives is visible.

The 60,000 transactions are synthetic. They do not represent a bank, payment processor or employer. The cost of review, customer friction and recovery rate are also scenario assumptions.

## Main result

The validation choice was a 0.15 score cutoff with capacity for 45 reviews per day. On the untouched test period:

- 9 of 10,800 transactions entered the queue;
- 4 of those 9 were labelled fraud, giving 44.4% precision;
- the queue found 5.6% of all labelled fraud, so coverage was intentionally low;
- the scenario net value was $3,446 using 85% recovery, $7 per review and $18 per false positive;
- a simple top-5%-by-amount baseline reviewed 537 transactions and had a negative scenario value of $5,357.

These values are useful for comparing choices inside this example. They are not realized savings.

## What is included

| Path | Purpose |
| --- | --- |
| `notebooks/fraud_decision_desk.ipynb` | Executed analysis with the split, model, calibration, threshold search and final result |
| `src/generate_data.py` | Reproducible transaction generator |
| `src/analyze_fraud.py` | Matching runnable analysis and dashboard export |
| `sql/review_queue.sql` | Window-function version of the daily queue rule |
| `dist/` | Static interactive dashboard |
| `outputs/` | Checked metrics, calibration and monitoring tables |
| `tests/` | Automated checks for time order, queue limits, metrics and costs |
| `docs/` | Findings, definitions, data dictionary, walkthrough and implementation notes |

## Run it

```bash
python -m pip install -r requirements.txt
python src/generate_data.py
python src/analyze_fraud.py
python scripts/execute_notebook.py
python -m pytest -q
```

Open `dist/index.html` through a local web server to use the interface. The published private preview is linked from the portfolio index after release.

## Method in brief

1. Sort transactions by timestamp.
2. Fit preprocessing and logistic regression on the earliest 50%.
3. Fit isotonic calibration on the next 15%.
4. Choose the threshold on the following 17%, with the review-cost assumptions fixed.
5. Use the last 18% once for the final comparison.
6. Rank qualifying transactions inside each day and stop at the chosen daily capacity.

The model uses ten transaction-level inputs. There are no customer or card identifiers, no delayed fraud labels and no live decisions. Those are important limits, not missing details to infer.

## Data and licence notes

I first checked the ULB/Worldline public-data references. The well-known public dataset covers two days of September 2013 and uses anonymized features. I did not include or redistribute it because a direct source download and clear redistribution path were not available in this run. The project instead uses an original deterministic generator and keeps the output clearly labelled synthetic.

- ULB Fraud Detection Handbook: https://fraud-detection-handbook.github.io/fraud-detection-handbook/
- ULB/Worldline Kaggle description: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Project code is MIT licensed. The generated dataset is released under CC0 1.0; see `data/README.md`.

## Limits

The generator is deliberately small and understandable. It does not recreate card networks, customer histories, chargeback delays, investigator feedback or changing fraud patterns. Isotonic calibration creates score steps, and the threshold result is sensitive to the authored cost assumptions. The dashboard evaluates known outcomes after the fact; it is not a real-time fraud system.
