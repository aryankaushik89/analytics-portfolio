# SaaS Revenue Control Room

I wanted to explain what was driving a change in recurring revenue, then trace the answer back to the subscription and invoice records. This project takes that question through SQL modelling, analysis and an interactive dashboard.

The data is entirely synthetic. It contains 360 fictional accounts, subscription changes, invoices, payments, credit notes, refunds and simulated FX rates. No employer or customer data is used.

![Revenue Room dashboard](docs/dashboard_overview.jpg)

## What you can do

- Change the reporting month, region or acquisition channel.
- See the movement from opening to closing MRR, including the currency effect.
- Compare total growth with retention from the opening customer cohort.
- Search for an account and inspect its recurring revenue history and invoice records.
- Compare invoicing, collections and the outstanding balance for a selected invoice month.
- Export the data for the current selection and read the definitions inside the app.

## A useful example

Open September 2026, select Customer ledger and search **Midmonth Upgrade**. It moves from CAD 100 to CAD 200 MRR, but its invoice is CAD 153.33 under the stated proration rule. This is why I keep subscription run rate separate from billing and cash.

September closing MRR is **CAD 85,826.85**, up from CAD 80,696.17. Constant currency NRR is **96.8%**. The total grows even though the opening customer cohort loses some recurring value. These are measured results from the generated scenario, not observations about a real business.

Read [the findings](docs/findings.md), [the app and code walkthrough](docs/walkthrough.md), [metric definitions](docs/metric_definitions.md) and [the data dictionary](docs/data_dictionary.md).

## Run the analysis

Use Python 3.11 or later and run these commands from the project folder.

```sh
python -m pip install -r requirements.txt
python analysis.py
python -m unittest discover -s tests -v
python tools/make_notebook.py
node tests/check_dashboard.mjs
```

The notebook builder executes the code cells in a fresh shared namespace, captures the printed results and actual charts, and writes `revenue_analysis.ipynb`, `revenue_analysis.py` and `outputs/revenue_analysis.html`. It does not use an external Jupyter kernel. The resulting notebook can also be run normally in Jupyter with the project files available.

Open `dist/index.html` in a browser to use the dashboard. It loads its local `data.js`, so the app also works from a local folder without a database, API key or paid service. A simple local server is another option.

```sh
python -m http.server 8000 --directory dist
```

Node is only needed for the JavaScript calculation checks, not for opening the app. The optional Google Fonts request changes typography; the interface falls back to system fonts when offline.

## How the files fit together

| File or folder | Purpose |
| --- | --- |
| `generate_data.py` | Recreates the source records using seed 89 |
| `data/` | Source CSV files, including deliberate repeated deliveries |
| `sql/01_subscription_history.sql` | Deduplicates events and reconstructs month end subscription states |
| `sql/02_revenue_movements.sql` | Builds customer movements, constant currency retention values and the bridge check |
| `sql/03_invoice_reconciliation.sql` | Aggregates each transaction type before joining the invoice ledger |
| `analysis.py` | Runs the SQL in SQLite and exports the results used by the dashboard |
| `revenue_analysis.ipynb` | Executed learning notebook with short steps and actual outputs |
| `revenue_analysis.py` | Matching Python version of the notebook |
| `outputs/` | Metric tables, cohort retention, checks, charts and an HTML notebook view |
| `dist/` | Browser interface and exported demonstration data |
| `tests/` | Fourteen Python tests and 525 JavaScript filter selection checks |
| `docs/` | Definitions, interpretation, app controls and interview walkthrough |

## Analytical choices

I normalize annual subscriptions to a monthly value and use customer level changes before aggregating. This avoids mixing annual billing with monthly recurring revenue. I keep an FX movement in the reported revenue bridge and calculate retention at constant currency.

The region and acquisition channel are fixed customer attributes in this scenario. That makes a segment's opening and closing cohort comparable. Filtering by a changing subscription plan would need separate treatment for movement between segments.

The SQL uses window functions and separate aggregation of payments, credits and refunds to avoid join fanout. It runs in SQLite through Python's standard library. There is no claim of a live Stripe, Snowflake or dbt integration.

## Limits

Each account has one fixed-price subscription. Most changes happen at the start of the month, while one account demonstrates a midmonth proration. Annual contract changes happen at renewal. Payment, credit and refund records settle within the invoice month. Taxes, usage billing, delayed settlements and recognized revenue are outside the model.

The generator deliberately increases later paid-search churn probability. Any channel difference demonstrates a method rather than a real marketing result. The data cannot support causal claims about campaigns.

## Source references

I checked the treatment of normalized subscription value, annual pricing and FX against [Stripe's Billing Analytics documentation](https://docs.stripe.com/billing/subscriptions/analytics). This is an independently built demonstration with its own documented assumptions, not a reproduction of a Stripe account or an endorsement from Stripe.

Code and generated data are released under the [MIT licence](LICENSE). Third-party source documentation retains its own rights.
