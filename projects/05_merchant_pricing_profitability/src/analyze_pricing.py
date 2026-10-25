from pathlib import Path

import pandas as pd


PLAN_ASSUMPTIONS = {
    "Current": {"markup_bps": 58.0, "per_transaction_cents": 9.0, "monthly_fee_cad": 18.0},
    "Growth": {"markup_bps": 44.0, "per_transaction_cents": 7.0, "monthly_fee_cad": 35.0},
    "Simple": {"markup_bps": 70.0, "per_transaction_cents": 0.0, "monthly_fee_cad": 0.0},
}

COST_ASSUMPTIONS = {
    "credit_interchange_bps": 132.0,
    "premium_increment_bps": 28.0,
    "international_increment_bps": 48.0,
    "network_bps": 13.0,
    "processor_bps": 4.0,
    "processor_per_transaction_cents": 4.5,
    "debit_per_transaction_cents": 7.0,
    "refund_handling_cents": 12.0,
}


def calculate_merchant_economics(dataframe, plan_name, cost_shock_bps=0.0, volume_change_pct=0.0):
    plan = PLAN_ASSUMPTIONS[plan_name]
    result = dataframe.copy()
    volume_factor = 1 + volume_change_pct / 100
    result["scenario_sales_cad"] = result["monthly_sales_cad"] * volume_factor
    result["scenario_transactions"] = (result["transactions"] * volume_factor).round().astype(int)
    result["refund_amount_cad"] = result["scenario_sales_cad"] * result["refund_rate"]
    result["net_sales_cad"] = result["scenario_sales_cad"] - result["refund_amount_cad"]
    result["debit_transactions"] = (result["scenario_transactions"] * result["debit_share"]).round()
    result["credit_transactions"] = result["scenario_transactions"] - result["debit_transactions"]
    result["credit_sales_cad"] = result["scenario_sales_cad"] * (1 - result["debit_share"])
    result["debit_sales_cad"] = result["scenario_sales_cad"] * result["debit_share"]
    interchange_bps = (
        COST_ASSUMPTIONS["credit_interchange_bps"]
        + result["premium_card_share"] * COST_ASSUMPTIONS["premium_increment_bps"]
        + result["international_share"] * COST_ASSUMPTIONS["international_increment_bps"]
        + cost_shock_bps
    )
    result["interchange_cost_cad"] = result["credit_sales_cad"] * interchange_bps / 10000
    result["debit_cost_cad"] = result["debit_transactions"] * COST_ASSUMPTIONS["debit_per_transaction_cents"] / 100
    result["network_cost_cad"] = result["scenario_sales_cad"] * COST_ASSUMPTIONS["network_bps"] / 10000
    result["processor_cost_cad"] = (
        result["scenario_sales_cad"] * COST_ASSUMPTIONS["processor_bps"] / 10000
        + result["scenario_transactions"] * COST_ASSUMPTIONS["processor_per_transaction_cents"] / 100
    )
    result["refund_handling_cost_cad"] = (
        result["scenario_transactions"] * result["refund_rate"]
        * COST_ASSUMPTIONS["refund_handling_cents"] / 100
    )
    result["total_cost_cad"] = result[
        ["interchange_cost_cad", "debit_cost_cad", "network_cost_cad", "processor_cost_cad", "refund_handling_cost_cad"]
    ].sum(axis=1)
    priced_cost_cad = result["total_cost_cad"] - result["credit_sales_cad"] * cost_shock_bps / 10000
    result["fee_revenue_cad"] = (
        result["scenario_sales_cad"] * plan["markup_bps"] / 10000
        + result["scenario_transactions"] * plan["per_transaction_cents"] / 100
        + plan["monthly_fee_cad"]
        + priced_cost_cad
    )
    result["contribution_margin_cad"] = result["fee_revenue_cad"] - result["total_cost_cad"]
    result["effective_rate_pct"] = result["fee_revenue_cad"].div(result["scenario_sales_cad"]).where(result["scenario_sales_cad"] > 0) * 100
    result["margin_rate_pct"] = result["contribution_margin_cad"].div(result["fee_revenue_cad"]).where(result["fee_revenue_cad"] > 0) * 100
    fixed_and_transaction_revenue = (
        result["scenario_transactions"] * plan["per_transaction_cents"] / 100 + plan["monthly_fee_cad"]
    )
    result["break_even_markup_bps"] = (
        (result["total_cost_cad"] - fixed_and_transaction_revenue)
        .div(result["scenario_sales_cad"])
        .where(result["scenario_sales_cad"] > 0)
        * 10000
    )
    result["plan"] = plan_name
    return result


def summarize_plan(result, plan_name=None):
    sales = result["scenario_sales_cad"].sum()
    fees = result["fee_revenue_cad"].sum()
    costs = result["total_cost_cad"].sum()
    contribution = result["contribution_margin_cad"].sum()
    return {
        "plan": plan_name if result.empty else result["plan"].iloc[0],
        "merchants": int(len(result)),
        "sales_cad": round(sales, 2),
        "transactions": int(result["scenario_transactions"].sum()),
        "fee_revenue_cad": round(fees, 2),
        "total_cost_cad": round(costs, 2),
        "contribution_margin_cad": round(contribution, 2),
        "weighted_effective_rate_pct": round(fees / sales * 100, 4) if sales else None,
        "contribution_margin_rate_pct": round(contribution / fees * 100, 4) if fees else None,
        "negative_margin_merchants": int((result["contribution_margin_cad"] < 0).sum()),
    }


def compare_plans(dataframe):
    details = []
    summaries = []
    for plan_name in PLAN_ASSUMPTIONS:
        result = calculate_merchant_economics(dataframe, plan_name)
        details.append(result)
        summaries.append(summarize_plan(result, plan_name))
    detail = pd.concat(details, ignore_index=True)
    summary = pd.DataFrame(summaries)
    return detail, summary


def run_analysis(data_path, output_directory):
    dataframe = pd.read_csv(data_path)
    detail, summary = compare_plans(dataframe)
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    detail.to_csv(output_directory / "merchant_plan_economics.csv", index=False)
    summary.to_csv(output_directory / "plan_summary.csv", index=False)
    segment_summary = (
        detail.groupby(["plan", "segment"], as_index=False)
        .agg(
            merchants=("merchant_id", "nunique"),
            sales_cad=("scenario_sales_cad", "sum"),
            fee_revenue_cad=("fee_revenue_cad", "sum"),
            total_cost_cad=("total_cost_cad", "sum"),
            contribution_margin_cad=("contribution_margin_cad", "sum"),
        )
    )
    segment_summary["effective_rate_pct"] = segment_summary["fee_revenue_cad"] / segment_summary["sales_cad"] * 100
    segment_summary["margin_rate_pct"] = segment_summary["contribution_margin_cad"] / segment_summary["fee_revenue_cad"] * 100
    segment_summary.to_csv(output_directory / "segment_summary.csv", index=False)
    return detail, summary, segment_summary


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    detail, summary, segment = run_analysis(root / "data" / "synthetic_merchants.csv", root / "outputs")
    print(summary.to_string(index=False))

