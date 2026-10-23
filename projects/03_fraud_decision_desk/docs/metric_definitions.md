# Metric definitions

## Review decision

A transaction is eligible when its fraud score is at least the selected threshold. Eligible records are ranked from highest to lowest score inside each calendar day. Only the first records up to the daily capacity are reviewed.

## Precision

Reviewed fraud transactions divided by all reviewed transactions. It answers: when the team reviews something, how often is the label fraud?

## Recall

Reviewed fraud transactions divided by all fraud transactions in the selected period. It answers: how much labelled fraud did the queue find?

## Average precision

Area under the precision-recall curve. It summarizes score ranking across thresholds and is more informative than accuracy under strong class imbalance.

## Brier score

Mean squared difference between the calibrated score and the 0/1 outcome. Lower is better. It is used here with a calibration table rather than as a threshold decision.

## Scenario net value

`captured fraud amount × recovery rate − reviews × review cost − false positives × friction cost`

The default recovery rate is 85%, review cost is $7 and false-positive friction cost is $18. These are authored scenario inputs, not accounting results.

## Amount baseline

The comparison assigns a score of 1 to transactions at or above the test period's 95th amount percentile and 0 to the rest, then applies the same daily capacity rule.
