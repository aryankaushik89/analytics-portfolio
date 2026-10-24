"""Run the governed-question evaluation and prepare dashboard outputs."""

import json
from pathlib import Path

import pandas as pd

from metric_engine import answer_question


CASES = [
    ("What was MRR in June 2026?", "mrr"),
    ("What was ending MRR in December 2025?", "mrr"),
    ("How many active customers were there in March 2026?", "active_customers"),
    ("What was customer churn in April 2026?", "churn_rate"),
    ("What was NRR in September 2026?", "nrr"),
    ("What was net revenue retention in February 2026?", "nrr"),
    ("Which segment had the highest MRR in June 2026?", "segment_mrr"),
    ("Show monthly MRR for 2026", "monthly_mrr"),
    ("Show monthly MRR in 2025", "monthly_mrr"),
    ("What was the invoice collection rate in July 2026?", "collection_rate"),
    ("How is revenue doing?", "clarification"),
    ("How are we performing?", "clarification"),
    ("What was CAC in June 2026?", "unsupported"),
    ("List every customer email", "unsupported"),
    ("Drop the customer table", "unsupported"),
    ("Update MRR to 10", "unsupported"),
]


def pandas_reference(intent, parameters, customers, monthly, invoices):
    if intent == "mrr":
        data = monthly[(monthly["month"] == parameters[0]) & (monthly["status"].isin(["active", "past_due"]))]
        return [[round(data["mrr"].sum(), 2)]]
    if intent == "active_customers":
        data = monthly[(monthly["month"] == parameters[0]) & (monthly["mrr"] > 0)]
        return [[int(len(data))]]
    if intent == "churn_rate":
        data = monthly[monthly["month"] == parameters[0]]
        base = (data["prior_mrr"] > 0).sum()
        churned = ((data["prior_mrr"] > 0) & (data["mrr"] == 0)).sum()
        return [[round(100 * churned / base, 2)]]
    if intent == "nrr":
        data = monthly[(monthly["month"] == parameters[0]) & (monthly["prior_mrr"] > 0)]
        return [[round(100 * data["mrr"].sum() / data["prior_mrr"].sum(), 2)]]
    if intent == "segment_mrr":
        data = monthly[(monthly["month"] == parameters[0]) & (monthly["mrr"] > 0)].merge(customers, on="customer_id")
        result = data.groupby("segment", as_index=False)["mrr"].sum().sort_values("mrr", ascending=False)
        return [[row.segment, round(row.mrr, 2)] for row in result.itertuples()]
    if intent == "monthly_mrr":
        data = monthly[(monthly["month"] >= parameters[0]) & (monthly["month"] <= parameters[1])]
        result = data.groupby("month", as_index=False)["mrr"].sum().sort_values("month")
        return [[row.month, round(row.mrr, 2)] for row in result.itertuples()]
    if intent == "collection_rate":
        data = invoices[invoices["invoice_month"] == parameters[0]]
        paid = data.loc[data["payment_status"] == "paid", "amount"].sum()
        return [[round(100 * paid / data["amount"].sum(), 2)]]
    return []


def run_evaluation(project_root):
    database_path = project_root / "data" / "metrics_demo.sqlite"
    customers = pd.read_csv(project_root / "data" / "customers.csv")
    monthly = pd.read_csv(project_root / "data" / "subscription_monthly.csv")
    invoices = pd.read_csv(project_root / "data" / "invoices.csv")

    results = []
    correct = 0
    for question, expected in CASES:
        answer = answer_question(question, database_path)
        classification_ok = answer["intent"] == expected if expected not in {"clarification", "unsupported"} else answer["status"] == expected
        result_ok = True
        if answer["status"] == "answered":
            expected_rows = pandas_reference(answer["intent"], answer["parameters"], customers, monthly, invoices)
            result_ok = answer["rows"] == expected_rows
        passed = classification_ok and result_ok
        correct += int(passed)
        results.append({
            "question": question,
            "expected": expected,
            "status": answer["status"],
            "intent": answer["intent"],
            "classification_ok": classification_ok,
            "result_ok": result_ok,
            "passed": passed,
        })

    scorecard = {
        "cases": len(results),
        "passed": correct,
        "accuracy": round(correct / len(results), 4),
        "answered_cases": sum(item["status"] == "answered" for item in results),
        "clarification_cases": sum(item["status"] == "clarification" for item in results),
        "unsupported_cases": sum(item["status"] == "unsupported" for item in results),
    }
    pd.DataFrame(results).to_csv(project_root / "outputs" / "question_evaluation.csv", index=False)
    with open(project_root / "outputs" / "evaluation_summary.json", "w", encoding="utf-8") as handle:
        json.dump(scorecard, handle, indent=2)

    example_questions = [case[0] for case in CASES[:10]] + [CASES[10][0], CASES[12][0]]
    examples = [answer_question(question, database_path) | {"question": question} for question in example_questions]
    with open(project_root / "dist" / "data.js", "w", encoding="utf-8") as handle:
        handle.write("window.METRIC_DEMO = ")
        json.dump({"scorecard": scorecard, "examples": examples}, handle, separators=(",", ":"))
        handle.write(";\n")
    return scorecard, examples


def main():
    project_root = Path(__file__).resolve().parents[1]
    scorecard, examples = run_evaluation(project_root)
    print(f"Evaluation cases passed: {scorecard['passed']}/{scorecard['cases']}")
    print(f"Answered questions: {scorecard['answered_cases']}")
    print(f"Clarification cases: {scorecard['clarification_cases']}")
    print(f"Unsupported cases: {scorecard['unsupported_cases']}")
    print(f"Dashboard examples: {len(examples)}")


if __name__ == "__main__":
    main()
