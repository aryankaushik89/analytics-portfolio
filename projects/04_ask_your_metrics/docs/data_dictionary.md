# Data dictionary

## customers

| Field | Meaning |
| --- | --- |
| `customer_id` | Synthetic sequential identifier |
| `segment` | SMB, Mid-market or Enterprise |
| `region` | Canada, United States or United Kingdom |
| `signup_month` | First synthetic subscription month |

## subscription_monthly

| Field | Meaning |
| --- | --- |
| `customer_id` | Joins to `customers` |
| `month` | Month-start date for the snapshot |
| `status` | `active`, `past_due` or `inactive` |
| `mrr` | Monthly-normalized synthetic subscription value |
| `prior_mrr` | Previous month's MRR for the same customer |

## invoices

| Field | Meaning |
| --- | --- |
| `invoice_id` | Synthetic sequential invoice identifier |
| `customer_id` | Joins to `customers` |
| `invoice_month` | Month-start date |
| `amount` | Subscription value plus an occasional synthetic one-time amount |
| `payment_status` | `paid`, `open` or `uncollectible` |

There are no names, emails, addresses, payment details or external account identifiers.
