# Walkthrough

## A quick way to explain the project

“I already had a fraud classifier project, so I did not want to repeat it. This one starts after a model produces a score. I focused on the operating decision: how many transactions can the team review, which cutoff should they use and what kinds of mistakes does that create?”

## Dashboard controls

### Minimum fraud score

Moves the eligibility cutoff. Raising it normally reduces queue volume and recall while improving precision. The model is calibrated, so the score is probability-like, but the small synthetic sample produces stepped values.

### Daily review capacity

Limits the queue separately for each day. When more transactions clear the threshold than the team can handle, the highest scores are kept.

### Test date

Shows all test days or one day. This helps check whether an overall result is being driven by a small number of dates.

### Reset

Returns to the threshold selected on validation data and 45 reviews per day.

### Result cards

- **Reviews** shows the queue size and share of transactions.
- **Precision** shows the fraud rate inside the queue.
- **Recall** shows the share of all labelled fraud that reached the queue.
- **Scenario net value** applies the visible fixed assumptions. It is not realized savings.

### Decision counts

The four cells are the operational confusion matrix: reviewed fraud, reviewed legitimate transactions, missed fraud and legitimate transactions left out of review.

### Cost view

Compares assumed avoided fraud loss with review and false-positive costs. It is useful for sensitivity testing, not for a financial forecast.

### Review queue

Shows up to 100 current records. **Details** opens the score inputs and known outcome. **Export current queue** downloads all currently selected records as CSV. A high threshold or zero capacity produces an explicit empty state.

## Analysis flow

1. Generate 90 days of transactions at the natural authored fraud rate.
2. Use an ordered 50%/15%/17%/18% split for fitting, calibration, validation and test.
3. Fit scaling and logistic regression on the first block only.
4. Fit isotonic calibration on the next block.
5. Choose the operating threshold on validation data using the fixed cost scenario.
6. Lock the choice and compare it with an amount-only baseline on the final period.

## Questions I would expect in an interview

**Why not use accuracy?** Almost all transactions are legitimate, so a model that predicts “not fraud” can have very high accuracy while finding nothing. I use precision, recall, average precision and the actual review decision.

**Why split by time?** A random split lets later patterns appear in training and does not reflect how a fraud system meets future transactions.

**Why calibrate the score?** Ranking and probability quality are different. Calibration makes a cutoff easier to interpret, although it does not remove uncertainty or drift.

**Why is recall so low?** The selected cost assumptions penalize false positives and the synthetic signal is limited. The result is honest about that. The dashboard shows how a lower threshold increases coverage and work.

**What would make this production-ready?** Real label delays, identity and network features, changing patterns, retraining rules, investigator feedback, fairness and customer-impact review, access controls and monitored data pipelines. None of those are claimed here.
