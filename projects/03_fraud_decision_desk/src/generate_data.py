"""Create the synthetic transaction history used in the project."""

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 89
TRANSACTION_COUNT = 60000


def logistic(values):
    return 1 / (1 + np.exp(-values))


def build_transactions(count=TRANSACTION_COUNT, seed=SEED):
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("2026-01-01 00:00:00")
    minute_offsets = np.sort(rng.integers(0, 90 * 24 * 60, count))
    timestamps = start + pd.to_timedelta(minute_offsets, unit="m")

    amount = np.round(rng.lognormal(mean=3.55, sigma=0.95, size=count), 2)
    hour = timestamps.hour.to_numpy()
    velocity_1h = np.clip(rng.poisson(1.1, count) + (rng.random(count) < 0.025) * rng.integers(3, 10, count), 0, 16)
    distance_home_km = np.round(rng.gamma(shape=1.4, scale=17, size=count), 1)
    merchant_risk = np.round(rng.beta(1.3, 8.5, size=count), 4)
    device_age_days = np.round(rng.exponential(170, count), 1)
    customer_history_days = np.round(rng.gamma(2.2, 250, count), 1)
    foreign_transaction = rng.binomial(1, 0.075, count)
    card_present = rng.binomial(1, 0.63, count)

    night = ((hour <= 5) | (hour >= 23)).astype(int)
    log_odds = (
        -7.15
        + 0.0085 * np.clip(amount - 90, 0, None)
        + 0.31 * velocity_1h
        + 0.009 * distance_home_km
        + 3.0 * merchant_risk
        + 0.72 * foreign_transaction
        + 0.48 * (1 - card_present)
        + 0.52 * night
        + 0.7 * (device_age_days < 5)
        + 0.35 * (customer_history_days < 30)
    )
    fraud_probability = np.clip(logistic(log_odds), 0, 0.82)
    is_fraud = rng.binomial(1, fraud_probability)

    frame = pd.DataFrame(
        {
            "transaction_id": [f"TX-{value:06d}" for value in range(1, count + 1)],
            "transaction_time": timestamps,
            "amount": amount,
            "hour": hour,
            "velocity_1h": velocity_1h,
            "distance_home_km": distance_home_km,
            "merchant_risk": merchant_risk,
            "device_age_days": device_age_days,
            "customer_history_days": customer_history_days,
            "foreign_transaction": foreign_transaction,
            "card_present": card_present,
            "is_fraud": is_fraud,
        }
    )
    frame["day"] = frame["transaction_time"].dt.date.astype(str)
    return frame


def main():
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "synthetic_transactions.csv.gz"
    transactions = build_transactions()
    transactions.to_csv(
        output_path,
        index=False,
        compression={"method": "gzip", "compresslevel": 9, "mtime": 0},
    )
    print(f"Saved {len(transactions):,} synthetic transactions to {output_path}")
    print(f"Fraud rate: {transactions['is_fraud'].mean():.3%}")


if __name__ == "__main__":
    main()
