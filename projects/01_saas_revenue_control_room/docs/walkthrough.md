# Walkthrough for the app and the code

## 1. What this project is trying to show

The main skill is turning an unclear commercial question into defined, reproducible metrics. The project shows SQL window functions, source deduplication, dimensional thinking, currency treatment, revenue retention, reconciliation and an interface a business stakeholder can use.

It extends my customer analytics background into subscription billing and revenue operations. It is a personal project, not work delivered for a former employer. The demo data is generated and the results are not real business performance.

## 2. A two-minute explanation

I wanted to understand why recurring revenue changed and whether the dashboard totals could be traced to the source records. I generated a small subscription business with monthly and annual contracts, then used SQL to reconstruct each customer's month end state.

I calculated customer movements before adding them up, separating new business, expansion, contraction, reactivation, churn and FX. I checked that those movements explain the entire change in MRR. I also compared growth with retention from the opening customer cohort.

I kept invoicing and cash separate. A midmonth upgrade is a useful example because its closing MRR is CAD 200 while its prorated invoice is CAD 153.33. The dashboard lets someone inspect that account, change the reporting view and export the exact records behind a number.

## 3. The interface

| Control | What happens | Useful check |
| --- | --- | --- |
| Reporting month | Changes metrics, customer and invoice records; the trend stops at the selected month | Try August and September 2026 |
| Region | Filters the same fixed customer population in all views | Compare Canada with United States |
| Acquisition channel | Filters records for the customer acquisition source | Compare Organic and Paid search without inferring causal effectiveness |
| Reset filters | Restores the latest month and all regions/channels | Search is cleared and pagination returns to the first page |
| Revenue overview | Shows MRR, ARR, NRR, selected invoice balances, trend, movement bridge and checks | Inspect growth alongside retention |
| Customer ledger | Shows the selected customer month records with search and pagination | Search Midmonth Upgrade |
| Account name | Opens an account dialog with recurring revenue history, movement and current-month invoices | Check MRR against the actual invoice amount |
| Billing & collections | Shows invoice-cohort totals and source currency transaction amounts | Confirm billed minus cash equals outstanding |
| How this works | Explains definitions, assumptions and limits | Check the currency and retention rules |
| Export selected data | Downloads the filtered customer rows, also respecting ledger search | A single account search exports that account |
| Export invoice data | Downloads all invoices in the selected month, region and channel | This is not restricted by customer ledger search |
| Take a quick tour | Opens a six-step explanation of the analysis | Close with the close button or Escape |

## 4. Trace a result through the files

1. `generate_data.py` creates customers, events and billing records. Seed 89 gives the same scenario on every run.
2. `01_subscription_history.sql` removes repeated events and selects the latest effective event for each month and customer.
3. `02_revenue_movements.sql` compares local recurring value and FX with the previous month. It calculates signed movements and the constant currency retention numerator.
4. `03_invoice_reconciliation.sql` creates an invoice ledger after separately adding payments, credits and refunds.
5. `analysis.py` executes that SQL in SQLite and exports metrics, cohort retention, checks and findings.
6. `tools/make_notebook.py` executes the smaller learning flow and captures its actual tables and charts. The matching `.py` preserves that flow.
7. `dist/data.js` contains the exported calculation results. `metrics.js` filters and aggregates those rows in the browser. `app.js` renders the views and handles controls.

The browser does not train a model, call an LLM or query a live Stripe account. It gives an interactive view over the checked exported results.

## 5. Questions I should be able to answer

**Why not calculate MRR from paid invoices?** Annual billing, proration and unpaid invoices make cash and invoice value different from a subscription run rate. The source contract state is the basis for MRR here.

**Why can total MRR grow while NRR is below 100%?** New business adds to total MRR but is excluded from the opening retention cohort. Acquisition can offset contraction and churn.

**Why separate FX?** A USD contract can keep the same local value while its reported CAD value changes. Treating that as expansion would misdescribe the commercial result.

**How do you prevent double counting?** Check source grain, deduplicate events and identical repeated invoices, rank month end states, and aggregate each one-to-many billing table before joining.

**Why not average individual retention percentages?** Accounts have different opening values. The correct total compares summed retained value with summed opening value.

**What would change with actual billing data?** I would first check account and subscription grain, lifecycle statuses, discounts, event versions, currency policy, late records, invoice adjustments and settlement timing. Multiple subscriptions require aggregation to customer before classifying customer churn and reactivation.

**What does this say about paid-search performance?** Nothing about a real channel. The generator deliberately creates a higher later churn probability to make a diagnostic example.

**What would improve next?** Add historical receivables ageing, effective-date billing periods and multiple subscriptions. These are separate extensions with additional definitions, not features already delivered.

## 6. Verification record

The analytical build passed eight visible data checks and fourteen Python tests. The JavaScript checks covered 525 month, region and channel combinations, including empty selections. Browser checks exercised navigation, account search, account dialog, month and region filters, billing, definitions, the tour and downloads. The implementation journal records the exact checks completed and any limits.
