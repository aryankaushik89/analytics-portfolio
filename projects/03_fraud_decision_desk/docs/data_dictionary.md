# Data dictionary

| Field | Type | Meaning |
| --- | --- | --- |
| `transaction_id` | text | Sequential synthetic identifier |
| `transaction_time` | timestamp | Generated transaction time over 90 days |
| `day` | date | Calendar date used for the daily queue |
| `amount` | decimal | Synthetic transaction amount |
| `hour` | integer | Hour of day, 0 through 23 |
| `velocity_1h` | integer | Authored count-like feature for recent transaction activity |
| `distance_home_km` | decimal | Synthetic distance from a usual location |
| `merchant_risk` | decimal | Generated input between 0 and 1; not an external merchant rating |
| `device_age_days` | decimal | Synthetic age of the device relationship |
| `customer_history_days` | decimal | Synthetic length of customer history |
| `foreign_transaction` | integer | Generated international flag, 0 or 1 |
| `card_present` | integer | Generated channel flag, 0 or 1 |
| `is_fraud` | integer | Authored outcome label, 0 or 1 |
| `split` | text | `train_fit`, `calibration`, `validation` or `test` |
| `fraud_score` | decimal | Calibrated model output used for queue ranking |

There are no names, card numbers, accounts, merchant IDs or geographic coordinates.
