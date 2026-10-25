from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20261025
SEGMENTS = ["Micro", "Small", "Mid-market", "Enterprise"]
SEGMENT_WEIGHTS = [0.29, 0.36, 0.25, 0.10]
CHANNELS = ["In person", "E-commerce", "Mixed"]
CHANNEL_WEIGHTS = [0.39, 0.28, 0.33]


def build_merchants(rows=360, seed=SEED):
    rng = np.random.default_rng(seed)
    segment = rng.choice(SEGMENTS, rows, p=SEGMENT_WEIGHTS)
    channel = rng.choice(CHANNELS, rows, p=CHANNEL_WEIGHTS)
    segment_scale = pd.Series(segment).map(
        {"Micro": 8.7, "Small": 9.8, "Mid-market": 11.1, "Enterprise": 12.3}
    ).to_numpy()
    monthly_sales = np.exp(rng.normal(segment_scale, 0.48)).round(2)
    avg_ticket = np.where(
        channel == "E-commerce",
        rng.uniform(55, 145, rows),
        np.where(channel == "In person", rng.uniform(22, 78, rows), rng.uniform(38, 105, rows)),
    ).round(2)
    transactions = np.maximum(1, np.rint(monthly_sales / avg_ticket)).astype(int)
    refund_rate = np.where(
        channel == "E-commerce",
        rng.beta(2.4, 48, rows),
        np.where(channel == "Mixed", rng.beta(2.0, 62, rows), rng.beta(1.5, 85, rows)),
    )
    international_share = np.where(
        channel == "E-commerce",
        rng.beta(2.2, 12, rows),
        rng.beta(1.4, 28, rows),
    )
    premium_share = rng.beta(2.7, 8.5, rows)
    debit_share = np.where(
        channel == "In person",
        rng.beta(5.0, 5.5, rows),
        np.where(channel == "Mixed", rng.beta(3.0, 7.0, rows), rng.beta(1.2, 18, rows)),
    )
    dataframe = pd.DataFrame(
        {
            "merchant_id": [f"M{index:04d}" for index in range(1, rows + 1)],
            "segment": segment,
            "channel": channel,
            "monthly_sales_cad": monthly_sales,
            "transactions": transactions,
            "average_ticket_cad": avg_ticket,
            "refund_rate": refund_rate.round(5),
            "international_share": international_share.round(5),
            "premium_card_share": premium_share.round(5),
            "debit_share": debit_share.round(5),
        }
    )
    return dataframe


def save_data(output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe = build_merchants()
    dataframe.to_csv(output_path, index=False)
    return dataframe


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    saved = save_data(root / "data" / "synthetic_merchants.csv")
    print(f"Saved {len(saved):,} synthetic merchants")

