# Implementation journal

## Scope decision

I kept this separate from the usual “train a fraud model and report accuracy” project. The deliverable is a threshold and queue simulator with enough modelling to produce an out-of-period score.

## Data decision

I checked the ULB/Worldline handbook and public Kaggle description. The published dataset is small in time coverage and anonymized. A direct download and clear redistribution path were not available in this run, so I did not use or package it.

I wrote a deterministic generator instead. It creates transaction features and outcomes from documented assumptions. There are no hidden real records.

## What ran

- Generated 60,000 transactions with seed 89.
- Fitted standardization on the training block only.
- Fitted logistic regression on 30,000 early records.
- Fitted isotonic calibration on the next 9,000 records.
- Searched thresholds on 10,200 validation records.
- Evaluated the locked choice on 10,800 final records.
- Executed 8 notebook code cells in a fresh Python namespace.
- Ran the matching Python script and wrote dashboard data.
- Ran 11 automated tests covering reproducibility, time order, queue capacity, thresholds, cost arithmetic and empty results.

## Dashboard checks

The release check covers default results, threshold changes, capacity changes, individual date selection, queue details, CSV export and the zero-capacity empty state. The desktop layout was inspected through the supported browser route. Responsive CSS rules were reviewed, but a separate narrow browser or mobile-device check was not available in this run.

## Known limits

- Synthetic features do not reproduce an actual payment network.
- There are no customer identifiers or behavioral histories across cards.
- Labels are available immediately, so chargeback delay is not represented.
- Cost assumptions are fixed in the analysis and only the queue controls move in the dashboard.
- The test period is about 17 days; one high-value fraud can move the cost result.
- The hosted dashboard is static and retrospective.
