# Findings

## The operating choice is selective

The validation search chose a 0.15 minimum score under the fixed cost assumptions. In the final 10,800-transaction test period, only 9 records entered the review queue. Four were fraud, so precision was 44.4%, but recall was only 5.6%.

That is the main trade-off. A narrow queue can avoid many false positives, but it leaves most labelled fraud outside review.

## A high-value fraud can change the cost result

The four reviewed frauds totalled $4,233.59. With 85% assumed recovery, the avoided-loss term was $3,598.55. Review and false-positive costs totalled $153, leaving a scenario net value of $3,445.55.

This does not mean the model would make that amount in practice. The result depends on the generated amounts, fixed recovery assumption and labels being known without delay.

## The amount-only rule created too much review work

The comparison baseline marked the top 5% of test transactions by amount. It reviewed 537 records, found 16 frauds and had 3.0% precision. Its higher recall did not cover the review and friction costs in this scenario, producing a value of negative $5,356.86.

## Ranking quality was useful but not strong enough to hide the limits

Test average precision was 0.099 against a 0.0066 fraud rate, and ROC AUC was 0.758. Those measures show better ordering than random selection, but they do not answer the queue question by themselves. The dashboard keeps the threshold and capacity controls visible for that reason.

## What I would check next

- Repeat the threshold choice across several later validation windows instead of one period.
- Add realistic label delays and investigator outcomes.
- Track score and fraud-rate drift by week and by channel.
- Compare a tree model only if it improves time-based validation without making the decision harder to explain.
