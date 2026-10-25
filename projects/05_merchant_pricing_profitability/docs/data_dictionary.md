# Data dictionary

## Synthetic merchant input

| Field | Grain and meaning |
| --- | --- |
| `merchant_id` | Unique fictional merchant identifier |
| `segment` | Micro, Small, Mid-market or Enterprise |
| `channel` | In person, E-commerce or Mixed |
| `monthly_sales_cad` | Gross processed card sales for one representative month |
| `transactions` | Processed transaction count |
| `average_ticket_cad` | Generator input used to derive transaction count |
| `refund_rate` | Share of processed sales modelled as refunds |
| `international_share` | Share of sales receiving the hypothetical international cost increment |
| `premium_card_share` | Share of credit sales receiving the hypothetical premium-card increment |
| `debit_share` | Share of volume and transactions modelled as debit |

## Calculated output

| Field | Meaning |
| --- | --- |
| `scenario_sales_cad` | Sales after the selected volume change |
| `scenario_transactions` | Rounded transaction count after the volume change |
| `refund_amount_cad` | Scenario sales multiplied by refund rate |
| `net_sales_cad` | Scenario sales less refund amount |
| `total_cost_cad` | Sum of the five synthetic cost components |
| `fee_revenue_cad` | Modelled merchant fee under the selected plan |
| `contribution_margin_cad` | Fee revenue less total cost |
| `effective_rate_pct` | Fee revenue divided by scenario sales |
| `margin_rate_pct` | Contribution margin divided by fee revenue |
| `break_even_markup_bps` | Volume markup needed to cover costs after fixed fees |

