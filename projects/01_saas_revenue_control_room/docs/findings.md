# What I found

All figures below come from the synthetic demonstration business. They do not describe a real company.

For 2026-09, closing MRR is CAD 85,826.85, compared with CAD 80,696.17 at the opening. Annualized recurring revenue is CAD 1,029,922.20.

The movement is explained by new subscriptions of CAD 5,828.05, expansion of CAD 1,640.67, reactivation of CAD 1,678.91, contraction of CAD -773.26, churn of CAD -3,455.49 and an FX movement of CAD 211.79. The reconciliation difference is CAD -0.00000000.

Constant currency net revenue retention is 96.8%. Gross revenue retention is 94.8%. These compare the opening paid customer cohort with its closing value and exclude new and reactivated customers. GRR caps each customer's retained amount at their opening value.

Net invoices issued this month total CAD 83,558.88. Net cash associated with those invoices is CAD 79,587.48, leaving CAD 3,971.40 outstanding in that invoice cohort. This is not total accounts receivable across all previous periods.

## What I would check next

I would review churn and contraction alongside acquisition before increasing the marketing budget. A larger customer base can hide weaker retention. The channel filter lets me compare those movements without changing the underlying customer cohort definitions.

I would also separate billing and collections from recurring revenue. Annual invoices and midmonth changes make the figures different even when the subscription calculation is correct. The Midmonth Upgrade account ends September at CAD 200 MRR but is billed CAD 153.33 under the stated proration rule.

## Limits

The data generation intentionally makes paid search churn more common in later months. That pattern demonstrates an analytical workflow, not evidence about marketing channels in real businesses. Every customer has one subscription, channels and regions stay fixed, changes normally happen at month boundaries and payment, credit and refund records settle within the invoice month. Taxes, usage charges, delayed settlements and recognized revenue are outside this model. FX rates are simulated. Results are descriptive and do not establish campaign causality.

The 8 visible data checks passed. Separate automated tests exercise edge cases and segment reconciliations.
