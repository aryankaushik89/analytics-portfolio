"""Create the synthetic commercial data used by Ask Your Metrics."""

import csv
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 89
MONTHS = pd.date_range("2025-01-01", "2026-12-01", freq="MS")


def build_frames(customer_count=240, seed=SEED):
    rng = np.random.default_rng(seed)
    segments = rng.choice(["SMB", "Mid-market", "Enterprise"], customer_count, p=[0.58, 0.30, 0.12])
    regions = rng.choice(["Canada", "United States", "United Kingdom"], customer_count, p=[0.62, 0.27, 0.11])
    start_index = rng.integers(0, 15, customer_count)
    customers = pd.DataFrame({
        "customer_id": [f"C-{i:04d}" for i in range(1, customer_count + 1)],
        "segment": segments,
        "region": regions,
        "signup_month": [MONTHS[i].strftime("%Y-%m-01") for i in start_index],
    })

    base_ranges = {"SMB": (90, 360), "Mid-market": (450, 1500), "Enterprise": (2200, 7500)}
    churn_rates = {"SMB": 0.032, "Mid-market": 0.019, "Enterprise": 0.011}
    rows = []
    invoices = []
    invoice_number = 1

    for idx, customer in customers.iterrows():
        low, high = base_ranges[customer["segment"]]
        current_mrr = 0.0
        prior_mrr = 0.0
        active = False
        for month_index, month in enumerate(MONTHS):
            if month_index == start_index[idx]:
                active = True
                current_mrr = float(rng.uniform(low, high))
            elif active:
                if rng.random() < churn_rates[customer["segment"]]:
                    active = False
                    current_mrr = 0.0
                else:
                    movement = rng.choice([0, 0, 0, 0, 0.08, 0.14, -0.07], p=[0.35, 0.20, 0.13, 0.10, 0.09, 0.06, 0.07])
                    current_mrr = max(0.0, current_mrr * (1 + movement))
            elif month_index > start_index[idx] and rng.random() < 0.018:
                active = True
                current_mrr = float(rng.uniform(low, high))

            status = "inactive"
            if active:
                status = "past_due" if rng.random() < 0.035 else "active"
            month_text = month.strftime("%Y-%m-01")
            mrr = round(current_mrr, 2) if active else 0.0
            rows.append({
                "customer_id": customer["customer_id"],
                "month": month_text,
                "status": status,
                "mrr": mrr,
                "prior_mrr": round(prior_mrr, 2),
            })

            if active:
                one_time = float(rng.uniform(40, 240)) if rng.random() < 0.08 else 0.0
                amount = round(mrr + one_time, 2)
                payment_status = rng.choice(["paid", "open", "uncollectible"], p=[0.94, 0.045, 0.015])
                invoices.append({
                    "invoice_id": f"INV-{invoice_number:06d}",
                    "customer_id": customer["customer_id"],
                    "invoice_month": month_text,
                    "amount": amount,
                    "payment_status": payment_status,
                })
                invoice_number += 1
            prior_mrr = mrr

    return customers, pd.DataFrame(rows), pd.DataFrame(invoices)


def write_database(project_root):
    data_dir = project_root / "data"
    customers, monthly, invoices = build_frames()
    customers.to_csv(data_dir / "customers.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    monthly.to_csv(data_dir / "subscription_monthly.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    invoices.to_csv(data_dir / "invoices.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    database_path = data_dir / "metrics_demo.sqlite"
    if database_path.exists():
        database_path.unlink()
    connection = sqlite3.connect(database_path)
    customers.to_sql("customers", connection, index=False)
    monthly.to_sql("subscription_monthly", connection, index=False)
    invoices.to_sql("invoices", connection, index=False)
    connection.executescript("""
        CREATE INDEX idx_subscription_month ON subscription_monthly(month);
        CREATE INDEX idx_subscription_customer ON subscription_monthly(customer_id);
        CREATE INDEX idx_invoice_month ON invoices(invoice_month);
    """)
    connection.close()
    return customers, monthly, invoices


def main():
    project_root = Path(__file__).resolve().parents[1]
    customers, monthly, invoices = write_database(project_root)
    print(f"Customers: {len(customers):,}")
    print(f"Monthly customer rows: {len(monthly):,}")
    print(f"Invoices: {len(invoices):,}")
    print(f"Final-month MRR: ${monthly.loc[monthly['month'] == '2026-12-01', 'mrr'].sum():,.2f}")


if __name__ == "__main__":
    main()
