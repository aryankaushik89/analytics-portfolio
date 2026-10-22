# Data dictionary

All records are synthetic. Source monetary amounts use integer minor units. Reporting outputs use CAD currency units. The baseline is December 2024; reported months are January 2025 through September 2026.

| Source | Grain and identifier | Important fields |
| --- | --- | --- |
| customers.csv | One row per customer_id | Fictional company, fixed region and acquisition channel, currency and signup date |
| subscription_events_raw.csv | Event delivery; event_id can repeat | effective_at is when the state applies, received_at is the delivery timestamp, unit_amount_minor is the recurring amount per billing interval, quantity, billing_interval and status |
| invoices_raw.csv | Invoice delivery; repeated identical invoice_id rows are planted | Invoice date, customer, currency, gross_minor, billing interval and service_months |
| payments.csv | One row per payment_id | Invoice identifier and payment amount |
| credit_notes.csv | One row per credit_id | Invoice identifier and positive credit amount that reduces billed value |
| refunds.csv | One row per refund_id | Invoice identifier and positive refund amount that reduces net cash |
| fx_rates.csv | One row per month and currency | cad_rate means CAD for one source currency unit; CAD is one and USD is simulated |
| months.csv | One row per month | YYYY-MM month and inclusive month end date |

No personal identifiers, addresses or actual customer contact details are present. A company label such as Maple Annual describes a fictional scenario, not an actual company relationship.

The clean event query keeps the most recently delivered copy of each event_id. Raw duplicate invoices are identical in this dataset, so DISTINCT is appropriate here. Conflicting versions of an invoice would require a version or update timestamp before this rule could be used on actual source data.

The main output grain is one customer per reporting month. Invoice outputs retain one row per invoice. Payment, credit and refund source tables are aggregated independently to invoice_id before joining.
