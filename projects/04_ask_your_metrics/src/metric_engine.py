"""Approved metric questions, inspected SQL and read-only execution."""

import re
import sqlite3
from pathlib import Path


ALLOWED_TABLES = {"customers", "subscription_monthly", "invoices"}
FORBIDDEN_WORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "ATTACH", "DETACH", "PRAGMA", "REPLACE", "CREATE"}
MONTH_PATTERN = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(2025|2026)"
MONTH_NUMBERS = {name: index for index, name in enumerate([
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
], start=1)}


SQL_TEMPLATES = {
    "mrr": """SELECT ROUND(SUM(mrr), 2) AS ending_mrr\nFROM subscription_monthly\nWHERE month = ?\n  AND status IN ('active', 'past_due')""",
    "active_customers": """SELECT COUNT(*) AS active_customers\nFROM subscription_monthly\nWHERE month = ?\n  AND mrr > 0""",
    "churn_rate": """SELECT\n  ROUND(100.0 * SUM(CASE WHEN prior_mrr > 0 AND mrr = 0 THEN 1 ELSE 0 END)\n    / NULLIF(SUM(CASE WHEN prior_mrr > 0 THEN 1 ELSE 0 END), 0), 2) AS customer_churn_rate_pct\nFROM subscription_monthly\nWHERE month = ?""",
    "nrr": """SELECT\n  ROUND(100.0 * SUM(CASE WHEN prior_mrr > 0 THEN mrr ELSE 0 END)\n    / NULLIF(SUM(CASE WHEN prior_mrr > 0 THEN prior_mrr ELSE 0 END), 0), 2) AS net_revenue_retention_pct\nFROM subscription_monthly\nWHERE month = ?""",
    "segment_mrr": """SELECT c.segment, ROUND(SUM(s.mrr), 2) AS ending_mrr\nFROM subscription_monthly s\nJOIN customers c ON c.customer_id = s.customer_id\nWHERE s.month = ?\n  AND s.mrr > 0\nGROUP BY c.segment\nORDER BY ending_mrr DESC""",
    "monthly_mrr": """SELECT month, ROUND(SUM(mrr), 2) AS ending_mrr\nFROM subscription_monthly\nWHERE month BETWEEN ? AND ?\nGROUP BY month\nORDER BY month""",
    "collection_rate": """SELECT\n  ROUND(100.0 * SUM(CASE WHEN payment_status = 'paid' THEN amount ELSE 0 END)\n    / NULLIF(SUM(amount), 0), 2) AS invoice_collection_rate_pct\nFROM invoices\nWHERE invoice_month = ?""",
}


DEFINITIONS = {
    "mrr": "Ending MRR is the monthly-normalized value of active and past-due subscriptions at month end.",
    "active_customers": "Active customers have MRR greater than zero in the selected month.",
    "churn_rate": "Customer churn rate is customers moving from positive prior MRR to zero, divided by customers with positive prior MRR.",
    "nrr": "Net revenue retention compares current MRR from the starting customer base with that base's prior MRR, including expansion, contraction and churn.",
    "segment_mrr": "Segment MRR applies the ending-MRR definition and groups customers by the authored segment field.",
    "monthly_mrr": "Monthly MRR applies the ending-MRR definition to each month in the requested range.",
    "collection_rate": "Invoice collection rate is paid invoice amount divided by total invoiced amount in the selected month.",
}


def month_value(match):
    return f"{match.group(2)}-{MONTH_NUMBERS[match.group(1)]:02d}-01"


def classify_question(question):
    clean = " ".join(question.strip().split())
    month_match = re.search(MONTH_PATTERN, clean, re.IGNORECASE)
    if month_match:
        normalized_match = re.search(MONTH_PATTERN, clean.title())
        month = month_value(normalized_match)
        lower = clean.lower()
        if "which" in lower and "segment" in lower and "mrr" in lower:
            return "segment_mrr", (month,), f"Compare ending MRR by customer segment for {month[:7]}."
        if "active customer" in lower:
            return "active_customers", (month,), f"Count customers with positive MRR for {month[:7]}."
        if "churn" in lower:
            return "churn_rate", (month,), f"Calculate customer churn rate for {month[:7]}."
        if "net revenue retention" in lower or re.search(r"\bnrr\b", lower):
            return "nrr", (month,), f"Calculate net revenue retention for {month[:7]}."
        if "collection" in lower and "invoice" in lower:
            return "collection_rate", (month,), f"Calculate invoice collection rate for {month[:7]}."
        if "mrr" in lower:
            return "mrr", (month,), f"Calculate ending MRR for {month[:7]}."

    year_match = re.search(r"monthly mrr (?:for|in) (2025|2026)", clean, re.IGNORECASE)
    if year_match:
        year = year_match.group(1)
        return "monthly_mrr", (f"{year}-01-01", f"{year}-12-01"), f"Return ending MRR for each month in {year}."

    lower = clean.lower()
    if any(term in lower for term in ["revenue", "growth", "performance", "performing", "doing"]):
        return "clarification", (), "The request needs a metric and time period before a query can run."
    return "unsupported", (), "This question is outside the approved metric dictionary."


def validate_sql(sql):
    normalized = " ".join(sql.upper().split())
    if not (normalized.startswith("SELECT ") or normalized.startswith("WITH ")):
        raise ValueError("Only SELECT or WITH queries are allowed.")
    if ";" in sql:
        raise ValueError("Multiple statements are not allowed.")
    words = set(re.findall(r"[A-Z_]+", normalized))
    blocked = sorted(words & FORBIDDEN_WORDS)
    if blocked:
        raise ValueError(f"Blocked SQL keyword: {blocked[0]}")
    referenced = set(re.findall(r"(?:FROM|JOIN)\s+([A-Z_]+)", normalized))
    if not referenced.issubset({name.upper() for name in ALLOWED_TABLES}):
        raise ValueError("Query references a table outside the approved schema.")
    return True


def read_only_connection(database_path):
    uri = f"file:{Path(database_path).resolve()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    denied = {
        sqlite3.SQLITE_CREATE_INDEX, sqlite3.SQLITE_CREATE_TABLE, sqlite3.SQLITE_CREATE_TEMP_INDEX,
        sqlite3.SQLITE_CREATE_TEMP_TABLE, sqlite3.SQLITE_CREATE_TEMP_TRIGGER, sqlite3.SQLITE_CREATE_TEMP_VIEW,
        sqlite3.SQLITE_CREATE_TRIGGER, sqlite3.SQLITE_CREATE_VIEW, sqlite3.SQLITE_DELETE, sqlite3.SQLITE_DROP_INDEX,
        sqlite3.SQLITE_DROP_TABLE, sqlite3.SQLITE_DROP_TEMP_INDEX, sqlite3.SQLITE_DROP_TEMP_TABLE,
        sqlite3.SQLITE_DROP_TEMP_TRIGGER, sqlite3.SQLITE_DROP_TEMP_VIEW, sqlite3.SQLITE_DROP_TRIGGER,
        sqlite3.SQLITE_DROP_VIEW, sqlite3.SQLITE_INSERT, sqlite3.SQLITE_PRAGMA, sqlite3.SQLITE_UPDATE,
        sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH, sqlite3.SQLITE_ALTER_TABLE,
    }
    connection.set_authorizer(lambda action, p1, p2, db, source: sqlite3.SQLITE_DENY if action in denied else sqlite3.SQLITE_OK)
    steps = [0]
    def progress():
        steps[0] += 1
        return 1 if steps[0] > 20000 else 0
    connection.set_progress_handler(progress, 1000)
    return connection


def format_answer(intent, columns, rows):
    if intent == "segment_mrr":
        top = rows[0]
        return f"{top[0]} had the highest ending MRR at ${top[1]:,.2f}."
    if intent == "monthly_mrr":
        return f"The series contains {len(rows)} monthly values, from ${rows[0][1]:,.2f} to ${rows[-1][1]:,.2f}."
    value = rows[0][0]
    if intent in {"mrr"}:
        return f"Ending MRR was ${value:,.2f}."
    if intent == "active_customers":
        return f"There were {value:,} active customers."
    return f"The result was {value:.2f}%."


def answer_question(question, database_path):
    intent, parameters, interpretation = classify_question(question)
    if intent == "clarification":
        return {"status": "clarification", "intent": None, "interpretation": interpretation, "sql": None, "parameters": [], "columns": [], "rows": [], "answer": "Please specify MRR, active customers, churn, NRR or invoice collection rate, plus a month or year.", "definition": None}
    if intent == "unsupported":
        return {"status": "unsupported", "intent": None, "interpretation": interpretation, "sql": None, "parameters": [], "columns": [], "rows": [], "answer": "I could not map this to an approved metric.", "definition": None}
    sql = SQL_TEMPLATES[intent]
    validate_sql(sql)
    connection = read_only_connection(database_path)
    cursor = connection.execute(sql, parameters)
    columns = [item[0] for item in cursor.description]
    rows = [list(row) for row in cursor.fetchmany(201)]
    connection.close()
    if len(rows) > 200:
        raise RuntimeError("Result exceeded the 200-row limit.")
    return {"status": "answered", "intent": intent, "interpretation": interpretation, "sql": sql, "parameters": list(parameters), "columns": columns, "rows": rows, "answer": format_answer(intent, columns, rows), "definition": DEFINITIONS[intent]}
