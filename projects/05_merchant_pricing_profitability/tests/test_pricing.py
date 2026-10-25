import math

import pandas as pd

from src.analyze_pricing import PLAN_ASSUMPTIONS
from src.analyze_pricing import calculate_merchant_economics
from src.analyze_pricing import compare_plans
from src.analyze_pricing import summarize_plan
from src.generate_data import build_merchants


def test_generator_is_deterministic():
    assert build_merchants().equals(build_merchants())


def test_generator_has_expected_grain_and_ranges():
    data = build_merchants()
    assert len(data) == 360
    assert data["merchant_id"].is_unique
    assert (data["monthly_sales_cad"] > 0).all()
    assert data["refund_rate"].between(0, 1).all()
    assert data["debit_share"].between(0, 1).all()


def test_fee_revenue_reconciles_to_cost_plus_markup_components():
    data = build_merchants(12)
    result = calculate_merchant_economics(data, "Current")
    plan = PLAN_ASSUMPTIONS["Current"]
    expected = (
        result["total_cost_cad"]
        + result["scenario_sales_cad"] * plan["markup_bps"] / 10000
        + result["scenario_transactions"] * plan["per_transaction_cents"] / 100
        + plan["monthly_fee_cad"]
    )
    assert (result["fee_revenue_cad"] - expected).abs().max() < 1e-8


def test_contribution_margin_reconciles():
    result = calculate_merchant_economics(build_merchants(15), "Growth")
    difference = result["fee_revenue_cad"] - result["total_cost_cad"] - result["contribution_margin_cad"]
    assert difference.abs().max() < 1e-8


def test_debit_and_credit_transactions_reconcile():
    result = calculate_merchant_economics(build_merchants(20), "Simple")
    assert (result["debit_transactions"] + result["credit_transactions"] == result["scenario_transactions"]).all()


def test_refunds_reduce_net_sales():
    result = calculate_merchant_economics(build_merchants(9), "Current")
    expected = result["scenario_sales_cad"] - result["refund_amount_cad"]
    assert (result["net_sales_cad"] - expected).abs().max() < 1e-8


def test_zero_volume_has_no_division_error():
    data = build_merchants(1)
    data.loc[0, "monthly_sales_cad"] = 0
    data.loc[0, "transactions"] = 0
    result = calculate_merchant_economics(data, "Current")
    assert math.isnan(result.loc[0, "effective_rate_pct"])
    assert math.isnan(result.loc[0, "break_even_markup_bps"])
    assert result.loc[0, "contribution_margin_cad"] == PLAN_ASSUMPTIONS["Current"]["monthly_fee_cad"]


def test_cost_shock_can_create_negative_margin():
    result = calculate_merchant_economics(build_merchants(30), "Growth", cost_shock_bps=200)
    assert (result["contribution_margin_cad"] < 0).any()


def test_negative_volume_change_clamps_transactions_at_zero_for_full_loss():
    result = calculate_merchant_economics(build_merchants(5), "Current", volume_change_pct=-100)
    assert (result["scenario_transactions"] == 0).all()
    assert (result["scenario_sales_cad"] == 0).all()


def test_summary_matches_detail_totals():
    result = calculate_merchant_economics(build_merchants(25), "Simple")
    summary = summarize_plan(result)
    assert summary["sales_cad"] == round(result["scenario_sales_cad"].sum(), 2)
    assert summary["fee_revenue_cad"] == round(result["fee_revenue_cad"].sum(), 2)


def test_three_plans_cover_same_merchants():
    detail, summary = compare_plans(build_merchants(18))
    assert len(detail) == 54
    assert summary["merchants"].tolist() == [18, 18, 18]


def test_empty_input_returns_empty_detail_without_silent_result():
    empty = build_merchants(0)
    detail, summary = compare_plans(empty)
    assert detail.empty
    assert summary["merchants"].eq(0).all()

