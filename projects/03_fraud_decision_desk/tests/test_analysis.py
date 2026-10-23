import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analyze_fraud import ASSUMPTIONS
from analyze_fraud import assign_time_split
from analyze_fraud import decision_metrics
from analyze_fraud import select_reviews
from generate_data import build_transactions


def small_scored_frame():
    return pd.DataFrame(
        {
            "transaction_id": ["A", "B", "C", "D"],
            "transaction_time": pd.to_datetime(["2026-01-01 09:00", "2026-01-01 10:00", "2026-01-01 11:00", "2026-01-02 09:00"]),
            "day": ["2026-01-01", "2026-01-01", "2026-01-01", "2026-01-02"],
            "amount": [100.0, 60.0, 40.0, 200.0],
            "fraud_score": [0.9, 0.8, 0.7, 0.6],
            "is_fraud": [1, 0, 1, 0],
        }
    )


def test_generator_is_reproducible():
    first = build_transactions(count=200, seed=11)
    second = build_transactions(count=200, seed=11)
    pd.testing.assert_frame_equal(first, second)


def test_generated_records_are_sorted_and_unique():
    frame = build_transactions(count=1000, seed=12)
    assert frame["transaction_time"].is_monotonic_increasing
    assert frame["transaction_id"].is_unique


def test_generated_labels_keep_both_classes():
    frame = build_transactions(count=5000, seed=13)
    assert set(frame["is_fraud"]) == {0, 1}


def test_time_splits_do_not_overlap():
    frame = assign_time_split(build_transactions(count=1000, seed=14))
    ordered = frame.groupby("split")["transaction_time"].agg(["min", "max"])
    assert ordered.loc["train_fit", "max"] <= ordered.loc["calibration", "min"]
    assert ordered.loc["calibration", "max"] <= ordered.loc["validation", "min"]
    assert ordered.loc["validation", "max"] <= ordered.loc["test", "min"]


def test_daily_capacity_is_respected():
    selected = select_reviews(small_scored_frame(), threshold=0.5, daily_capacity=2)
    daily = selected.groupby("day")["reviewed"].sum()
    assert daily.max() <= 2


def test_threshold_is_respected():
    selected = select_reviews(small_scored_frame(), threshold=0.75, daily_capacity=10)
    assert selected.loc[selected["fraud_score"] < 0.75, "reviewed"].sum() == 0


def test_zero_capacity_returns_no_reviews():
    selected = select_reviews(small_scored_frame(), threshold=0, daily_capacity=0)
    assert selected["reviewed"].sum() == 0


def test_metrics_reconcile_confusion_counts():
    metrics = decision_metrics(small_scored_frame(), threshold=0.5, daily_capacity=2)
    assert metrics["reviews"] == metrics["true_positive"] + metrics["false_positive"]
    assert metrics["missed_fraud"] + metrics["true_positive"] == 2


def test_cost_calculation_matches_assumptions():
    metrics = decision_metrics(small_scored_frame(), threshold=0.75, daily_capacity=10)
    expected = metrics["avoided_loss"] - metrics["review_cost"] - metrics["friction_cost"]
    assert np.isclose(metrics["net_value"], expected)


def test_empty_queue_metrics_are_defined():
    metrics = decision_metrics(small_scored_frame(), threshold=1.1, daily_capacity=10)
    assert metrics["reviews"] == 0
    assert metrics["precision"] == 0
    assert metrics["recall"] == 0


def test_assumptions_are_positive_and_bounded():
    assert ASSUMPTIONS["review_cost"] > 0
    assert ASSUMPTIONS["false_positive_cost"] > 0
    assert 0 < ASSUMPTIONS["recovery_rate"] <= 1
    assert ASSUMPTIONS["daily_review_capacity"] > 0
