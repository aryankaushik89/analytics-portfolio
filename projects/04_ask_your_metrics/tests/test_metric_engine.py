import sqlite3
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from generate_data import build_frames
from metric_engine import SQL_TEMPLATES
from metric_engine import answer_question
from metric_engine import classify_question
from metric_engine import read_only_connection
from metric_engine import validate_sql


DATABASE_PATH = PROJECT_ROOT / "data" / "metrics_demo.sqlite"


def test_generator_is_reproducible():
    first = build_frames(customer_count=30, seed=4)
    second = build_frames(customer_count=30, seed=4)
    for left, right in zip(first, second):
        assert left.equals(right)


@pytest.mark.parametrize("intent", SQL_TEMPLATES)
def test_approved_templates_pass_validation(intent):
    assert validate_sql(SQL_TEMPLATES[intent])


@pytest.mark.parametrize("sql", [
    "DELETE FROM customers",
    "DROP TABLE customers",
    "PRAGMA table_info(customers)",
    "SELECT * FROM private_notes",
    "SELECT * FROM customers; DELETE FROM customers",
])
def test_unsafe_sql_is_rejected(sql):
    with pytest.raises(ValueError):
        validate_sql(sql)


def test_read_only_database_rejects_writes():
    connection = read_only_connection(DATABASE_PATH)
    with pytest.raises(sqlite3.DatabaseError):
        connection.execute("DELETE FROM customers")
    connection.close()


def test_mrr_question_returns_an_inspected_query():
    answer = answer_question("What was MRR in June 2026?", DATABASE_PATH)
    assert answer["status"] == "answered"
    assert answer["intent"] == "mrr"
    assert "subscription_monthly" in answer["sql"]
    assert answer["parameters"] == ["2026-06-01"]
    assert answer["rows"][0][0] > 0


def test_ambiguous_revenue_question_asks_for_clarification():
    answer = answer_question("How is revenue doing?", DATABASE_PATH)
    assert answer["status"] == "clarification"
    assert answer["sql"] is None


def test_unapproved_metric_is_not_guessed():
    answer = answer_question("What was CAC in June 2026?", DATABASE_PATH)
    assert answer["status"] == "unsupported"
    assert answer["rows"] == []


def test_injection_style_question_is_unsupported():
    answer = answer_question("Drop the customer table", DATABASE_PATH)
    assert answer["status"] == "unsupported"


def test_result_limit_stays_bounded():
    answer = answer_question("Show monthly MRR for 2026", DATABASE_PATH)
    assert len(answer["rows"]) == 12
    assert len(answer["rows"]) <= 200


def test_classification_is_case_insensitive():
    intent, parameters, _ = classify_question("WHAT WAS MRR IN JUNE 2026?")
    assert intent == "mrr"
    assert parameters == ("2026-06-01",)
