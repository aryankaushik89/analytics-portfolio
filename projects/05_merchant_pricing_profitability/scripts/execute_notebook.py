from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


CELLS = [
    ("markdown", "# Merchant Pricing and Profitability\n\nA checked synthetic example of how transaction mix and pricing assumptions affect contribution margin."),
    ("markdown", "## 1. Load the merchant-month data\n\nThe data is authored and deterministic. Each row is one fictional merchant for one representative month."),
    ("code", "from pathlib import Path\n\nimport pandas as pd\n\nfrom src.analyze_pricing import calculate_merchant_economics\nfrom src.analyze_pricing import compare_plans\n\nROOT = Path.cwd()\nmerchants = pd.read_csv(ROOT / 'data' / 'synthetic_merchants.csv')\nprint(merchants.shape)\nprint(merchants[['monthly_sales_cad', 'transactions', 'refund_rate']].describe().round(2).to_string())"),
    ("markdown", "## 2. Check the row grain and totals\n\nThe merchant identifier should be unique and the transaction and sales totals should be positive."),
    ("code", "checks = pd.DataFrame({\n    'check': ['unique merchant rows', 'positive monthly sales', 'positive transaction counts'],\n    'passed': [merchants['merchant_id'].is_unique, merchants['monthly_sales_cad'].gt(0).all(), merchants['transactions'].gt(0).all()],\n    'observed': [merchants['merchant_id'].nunique(), round(merchants['monthly_sales_cad'].sum(), 2), int(merchants['transactions'].sum())]\n})\nprint(checks.to_string(index=False))"),
    ("markdown", "## 3. Compare the three pricing options\n\nEvery plan uses the same synthetic underlying payment costs. Only the markup, transaction fee and monthly fee change."),
    ("code", "detail, summary = compare_plans(merchants)\nprint(summary.to_string(index=False))"),
    ("markdown", "## 4. Compare merchant segments\n\nA weighted effective rate uses total fee revenue divided by total processed sales. This avoids averaging merchant percentages equally."),
    ("code", "segment = detail.groupby(['plan', 'segment'], as_index=False).agg(sales_cad=('scenario_sales_cad', 'sum'), fee_revenue_cad=('fee_revenue_cad', 'sum'), contribution_margin_cad=('contribution_margin_cad', 'sum'))\nsegment['weighted_effective_rate_pct'] = segment['fee_revenue_cad'] / segment['sales_cad'] * 100\nprint(segment.round(2).to_string(index=False))"),
    ("markdown", "## 5. Test a cost shock\n\nPricing is held fixed while credit costs rise by 100 basis points. This is a stress test, not a forecast."),
    ("code", "stress = calculate_merchant_economics(merchants, 'Growth', cost_shock_bps=100)\nstress_summary = pd.DataFrame({\n    'measure': ['contribution margin', 'negative-margin merchants'],\n    'observed': [round(stress['contribution_margin_cad'].sum(), 2), int(stress['contribution_margin_cad'].lt(0).sum())]\n})\nprint(stress_summary.to_string(index=False))"),
    ("markdown", "## 6. Inspect break-even pressure\n\nThe break-even markup is the additional volume rate needed after the selected fixed and transaction fees. A negative value means those fixed components already cover the modelled costs."),
    ("code", "current = detail[detail['plan'].eq('Current')]\nprint(current[['merchant_id', 'segment', 'channel', 'scenario_sales_cad', 'contribution_margin_cad', 'break_even_markup_bps']].nsmallest(8, 'contribution_margin_cad').round(2).to_string(index=False))"),
    ("markdown", "## 7. Interpretation\n\nThe current plan produces the largest total contribution margin in the base case. The growth plan lowers the portfolio weighted effective rate, but a large unpriced cost shock can turn the portfolio negative. The result supports a monitored pricing decision, not a claim about a real provider or merchant."),
]


def run_cell(source, namespace):
    output = StringIO()
    with redirect_stdout(output):
        exec(compile(source, "<notebook>", "exec"), namespace)
    return output.getvalue()


def main():
    namespace = {"__name__": "__main__"}
    notebook_cells = []
    execution_count = 0
    for cell_type, source in CELLS:
        if cell_type == "markdown":
            notebook_cells.append({"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)})
            continue
        execution_count += 1
        text = run_cell(source, namespace)
        notebook_cells.append(
            {
                "cell_type": "code",
                "execution_count": execution_count,
                "metadata": {},
                "outputs": [{"name": "stdout", "output_type": "stream", "text": text.splitlines(True)}],
                "source": source.splitlines(True),
            }
        )
    notebook = {
        "cells": notebook_cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": sys.version.split()[0]}},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    target = ROOT / "notebooks" / "merchant_pricing_profitability.ipynb"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(f"Executed {execution_count} code cells")


if __name__ == "__main__":
    main()

