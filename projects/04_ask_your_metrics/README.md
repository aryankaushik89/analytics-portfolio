# Ask Your Metrics

This project asks whether a business-question interface can stay tied to approved definitions instead of inventing a plausible query.

The first release is deliberately constrained. A deterministic parser selects from seven reviewed SQL templates, extracts safe date parameters and runs the query against a read-only SQLite database. Every answer shows the interpretation, SQL, parameters, result and metric definition. Ambiguous or unsupported questions stop without a query.

The browser dashboard is an **offline replay of checked SQL answers**. There is no live language model, Stripe account or production database connection.

## What I found

All 16 authored evaluation questions passed. Ten supported questions matched independent pandas calculations, two broad questions asked for clarification and four unsupported or unsafe requests ran no SQL.

For the synthetic data:

- ending MRR in June 2026 was $249,283.27;
- Enterprise had the highest June MRR at $167,009.50;
- April 2026 customer churn was 2.02%;
- September 2026 NRR was 96.19%;
- July 2026 invoice collection rate was 89.84%.

These are results from authored demonstration data, not actual company metrics.

## Open the work

- `notebooks/ask_your_metrics.ipynb` — executed learning notebook
- `src/metric_engine.py` — approved templates, question routing and read-only execution
- `src/run_analysis.py` — independent result checks and dashboard export
- `sql/approved_metrics.sql` — readable metric queries
- `dist/` — static interactive demo
- `docs/walkthrough.md` — control-by-control explanation
- `docs/interview_explanation.md` — short interview version

## Run it

```bash
python -m pip install -r requirements.txt
python src/generate_data.py
python src/run_analysis.py
python scripts/execute_notebook.py
python -m pytest -q
```

Serve `dist/` through a local web server for the browser interface.

## Guardrails

1. Questions map to a fixed metric registry; user text is never executed as SQL.
2. Only `SELECT` and `WITH` templates pass validation.
3. Tables are restricted to `customers`, `subscription_monthly` and `invoices`.
4. Dates are passed as bound parameters.
5. SQLite opens the database with `mode=ro&immutable=1` and an authorizer denies writes, DDL, PRAGMA, attach and detach operations.
6. A progress handler limits work and the result is capped at 200 rows.
7. Unsupported requests and ambiguous metric language run no query.

## Data and definitions

The generator creates 240 synthetic customers, 5,760 monthly customer snapshots and 3,392 invoices across 2025 and 2026. It contains no names, email addresses, employer information or real subscription records.

The MRR definition follows the idea of monthly-normalized active and past-due subscription value described in Stripe Billing Analytics. The schema and calculations here are authored for this project and are not a Stripe integration.

- Stripe Billing metric definitions: https://docs.stripe.com/billing/subscriptions/analytics
- Python SQLite interface: https://docs.python.org/3/library/sqlite3.html

Code uses the MIT licence. The authored synthetic CSV and SQLite data are released under CC0 1.0.

## Limits

This is not open-ended text-to-SQL and does not use a generative model. It does not handle synonyms beyond the tested patterns, conversational memory, database discovery or production permissions. The evaluation set is small and authored with the project, so 16/16 is a regression check, not a general language-understanding benchmark.
