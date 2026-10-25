# Merchant Pricing and Profitability

I built this project to compare clear merchant pricing options without treating one blended percentage as the whole answer. The analysis separates merchant fee revenue from modelled payment costs, then shows contribution margin, break-even pressure and sensitivity to volume and credit-cost changes.

[Open the private dashboard](https://aryan-merchant-pricing-lab.arz2389.chatgpt.site)

## Business question

How do three hypothetical pricing structures affect merchant cost and provider contribution margin, and which merchants become exposed when costs change before pricing does?

## What is included

- 360 deterministic synthetic merchant-month records
- an executed notebook and matching Python analysis
- three transparent price plans and five cost components
- merchant and segment outputs with weighted effective rates
- a browser dashboard with plan, segment, channel, cost and volume controls
- merchant detail, CSV export, empty-state handling and a reset path
- metric definitions, findings, data dictionary, walkthrough and implementation journal

## Base result

The synthetic portfolio contains CAD 18.77 million in monthly processed sales and 315,622 transactions. Current produces CAD 143,763 in contribution margin at a 2.054% weighted effective rate. Growth lowers the rate to 1.913% and produces CAD 117,290 in contribution margin. A 100 basis point unpriced credit-cost shock moves Growth contribution margin to negative CAD 13,632 in this scenario.

These are model outputs, not realized results. Every price, cost and response assumption is hypothetical.

## Reproduce the work

```bash
python scripts/run_analysis.py
PYTHONPATH=. python -m pytest -q tests
python scripts/execute_notebook.py
python scripts/build_dashboard_data.py
```

Open `dist/index.html` through a local web server to use the dashboard.

## Files to start with

- `notebooks/merchant_pricing_profitability.ipynb` keeps the question, checks and interpretation together.
- `src/analyze_pricing.py` contains the matching calculations.
- `outputs/plan_summary.csv` contains the checked portfolio comparison.
- `docs/walkthrough.md` explains every interface control.
- `docs/metric_definitions.md` defines the financial measures and denominators.

## Sources and limits

The component structure was checked against public explanations from [Mastercard Canada](https://www.mastercard.ca/en-ca/business/overview/interchange.html), [Visa Canada](https://www.visa.ca/en_CA/support/small-business/interchange.html) and the [Financial Consumer Agency of Canada](https://www.canada.ca/en/financial-consumer-agency/services/merchants/rights-merchant.html). The project does not copy their rate tables. No real Moneris, network, merchant, employer or assessment data is included.

Contribution margin here excludes sales, support, hardware, compliance, fraud losses, tax and overhead. A real decision would require governed contracts and settlement records.

