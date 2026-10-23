"""Train the fraud score and evaluate operational review decisions."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.metrics import brier_score_loss
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler


FEATURES = [
    "amount",
    "hour_sin",
    "hour_cos",
    "velocity_1h",
    "distance_home_km",
    "merchant_risk",
    "device_age_days",
    "customer_history_days",
    "foreign_transaction",
    "card_present",
]

ASSUMPTIONS = {
    "review_cost": 7.0,
    "false_positive_cost": 18.0,
    "recovery_rate": 0.85,
    "daily_review_capacity": 45,
}


def add_model_features(frame):
    result = frame.copy()
    angle = 2 * np.pi * result["hour"] / 24
    result["hour_sin"] = np.sin(angle)
    result["hour_cos"] = np.cos(angle)
    return result


def assign_time_split(frame):
    result = frame.sort_values("transaction_time").reset_index(drop=True).copy()
    count = len(result)
    boundaries = {
        "train_fit": int(count * 0.50),
        "calibration": int(count * 0.65),
        "validation": int(count * 0.82),
    }
    result["split"] = "test"
    result.loc[: boundaries["train_fit"] - 1, "split"] = "train_fit"
    result.loc[boundaries["train_fit"] : boundaries["calibration"] - 1, "split"] = "calibration"
    result.loc[boundaries["calibration"] : boundaries["validation"] - 1, "split"] = "validation"
    return result


def train_scores(frame):
    result = add_model_features(assign_time_split(frame))
    train = result[result["split"] == "train_fit"]
    calibration = result[result["split"] == "calibration"]

    scaler = StandardScaler()
    train_values = scaler.fit_transform(train[FEATURES])
    model = LogisticRegression(max_iter=700, class_weight="balanced", random_state=89)
    model.fit(train_values, train["is_fraud"])

    calibration_raw = model.predict_proba(scaler.transform(calibration[FEATURES]))[:, 1]
    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(calibration_raw, calibration["is_fraud"])

    raw_scores = model.predict_proba(scaler.transform(result[FEATURES]))[:, 1]
    result["fraud_score"] = calibrator.predict(raw_scores)
    return result, model, scaler


def select_reviews(frame, threshold, daily_capacity):
    eligible = frame[frame["fraud_score"] >= threshold].copy()
    eligible = eligible.sort_values(["day", "fraud_score"], ascending=[True, False])
    eligible["queue_position"] = eligible.groupby("day").cumcount() + 1
    eligible["reviewed"] = eligible["queue_position"] <= daily_capacity
    selected_ids = eligible.loc[eligible["reviewed"], "transaction_id"]
    result = frame.copy()
    result["reviewed"] = result["transaction_id"].isin(selected_ids)
    return result


def decision_metrics(frame, threshold, daily_capacity, assumptions=ASSUMPTIONS):
    evaluated = select_reviews(frame, threshold, daily_capacity)
    reviewed = evaluated[evaluated["reviewed"]]
    true_positive = int(reviewed["is_fraud"].sum())
    false_positive = int(len(reviewed) - true_positive)
    fraud_total = int(evaluated["is_fraud"].sum())
    missed_fraud = fraud_total - true_positive
    captured_amount = reviewed.loc[reviewed["is_fraud"] == 1, "amount"].sum()
    missed_amount = evaluated.loc[(evaluated["is_fraud"] == 1) & (~evaluated["reviewed"]), "amount"].sum()
    review_cost = len(reviewed) * assumptions["review_cost"]
    friction_cost = false_positive * assumptions["false_positive_cost"]
    avoided_loss = captured_amount * assumptions["recovery_rate"]
    net_value = avoided_loss - review_cost - friction_cost
    precision = true_positive / len(reviewed) if len(reviewed) else 0
    recall = true_positive / fraud_total if fraud_total else 0
    return {
        "threshold": round(float(threshold), 4),
        "daily_capacity": int(daily_capacity),
        "transactions": int(len(evaluated)),
        "reviews": int(len(reviewed)),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "missed_fraud": missed_fraud,
        "precision": round(float(precision), 6),
        "recall": round(float(recall), 6),
        "captured_fraud_amount": round(float(captured_amount), 2),
        "missed_fraud_amount": round(float(missed_amount), 2),
        "review_cost": round(float(review_cost), 2),
        "friction_cost": round(float(friction_cost), 2),
        "avoided_loss": round(float(avoided_loss), 2),
        "net_value": round(float(net_value), 2),
    }


def build_threshold_table(validation, daily_capacity=45):
    thresholds = np.unique(np.concatenate([np.linspace(0.01, 0.80, 80), validation["fraud_score"].quantile(np.linspace(0.70, 0.995, 35)).to_numpy()]))
    rows = [decision_metrics(validation, value, daily_capacity) for value in thresholds]
    return pd.DataFrame(rows).sort_values(["net_value", "recall"], ascending=False).reset_index(drop=True)


def score_quality(frame):
    return {
        "average_precision": round(float(average_precision_score(frame["is_fraud"], frame["fraud_score"])), 6),
        "roc_auc": round(float(roc_auc_score(frame["is_fraud"], frame["fraud_score"])), 6),
        "brier_score": round(float(brier_score_loss(frame["is_fraud"], frame["fraud_score"])), 6),
        "fraud_rate": round(float(frame["is_fraud"].mean()), 6),
    }


def calibration_table(frame):
    result = frame.copy()
    result["score_band"] = pd.cut(result["fraud_score"], bins=[-0.001, 0.01, 0.03, 0.06, 0.10, 0.20, 0.40, 0.70, 1.001])
    summary = result.groupby("score_band", observed=False).agg(transactions=("transaction_id", "count"), average_score=("fraud_score", "mean"), observed_fraud_rate=("is_fraud", "mean")).reset_index()
    summary["score_band"] = summary["score_band"].astype(str)
    return summary.fillna(0)


def daily_monitoring(frame, threshold, daily_capacity):
    evaluated = select_reviews(frame, threshold, daily_capacity)
    return evaluated.groupby("day").agg(
        transactions=("transaction_id", "count"),
        reviews=("reviewed", "sum"),
        frauds=("is_fraud", "sum"),
        average_score=("fraud_score", "mean"),
        amount=("amount", "sum"),
    ).reset_index()


def main():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "synthetic_transactions.csv.gz"
    output_dir = project_root / "outputs"
    dashboard_dir = project_root / "dist"

    transactions = pd.read_csv(data_path, parse_dates=["transaction_time"])
    scored, model, scaler = train_scores(transactions)
    validation = scored[scored["split"] == "validation"].copy()
    test = scored[scored["split"] == "test"].copy()

    threshold_table = build_threshold_table(validation, ASSUMPTIONS["daily_review_capacity"])
    selected_threshold = float(threshold_table.iloc[0]["threshold"])
    validation_result = decision_metrics(validation, selected_threshold, ASSUMPTIONS["daily_review_capacity"])
    test_result = decision_metrics(test, selected_threshold, ASSUMPTIONS["daily_review_capacity"])
    baseline_result = decision_metrics(test.assign(fraud_score=(test["amount"] >= test["amount"].quantile(0.95)).astype(float)), 0.5, ASSUMPTIONS["daily_review_capacity"])

    quality = {name: score_quality(scored[scored["split"] == name]) for name in ["validation", "test"]}
    split_summary = scored.groupby("split").agg(rows=("transaction_id", "count"), start=("transaction_time", "min"), end=("transaction_time", "max"), fraud_rate=("is_fraud", "mean")).reset_index()

    metrics = {
        "selected_threshold": selected_threshold,
        "assumptions": ASSUMPTIONS,
        "validation": validation_result,
        "test": test_result,
        "amount_baseline_test": baseline_result,
        "score_quality": quality,
        "split_summary": json.loads(split_summary.to_json(orient="records", date_format="iso")),
        "model": "Logistic regression followed by isotonic calibration",
        "feature_count": len(FEATURES),
    }

    threshold_table.to_csv(output_dir / "threshold_validation.csv", index=False)
    calibration_table(test).to_csv(output_dir / "calibration_test.csv", index=False)
    daily_monitoring(test, selected_threshold, ASSUMPTIONS["daily_review_capacity"]).to_csv(output_dir / "daily_monitoring_test.csv", index=False)
    with open(output_dir / "model_metrics.json", "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)

    dashboard_columns = ["transaction_id", "transaction_time", "day", "amount", "velocity_1h", "distance_home_km", "merchant_risk", "foreign_transaction", "card_present", "is_fraud", "fraud_score"]
    dashboard_records = json.loads(test[dashboard_columns].to_json(orient="records", date_format="iso"))
    with open(dashboard_dir / "data.js", "w", encoding="utf-8") as handle:
        handle.write("window.FRAUD_DATA = ")
        json.dump({"transactions": dashboard_records, "metrics": metrics}, handle, separators=(",", ":"))
        handle.write(";\n")

    print(f"Selected validation threshold: {selected_threshold:.4f}")
    print(f"Test reviews: {test_result['reviews']:,}")
    print(f"Test precision: {test_result['precision']:.1%}")
    print(f"Test recall: {test_result['recall']:.1%}")
    print(f"Test net value under assumptions: ${test_result['net_value']:,.0f}")


if __name__ == "__main__":
    main()
