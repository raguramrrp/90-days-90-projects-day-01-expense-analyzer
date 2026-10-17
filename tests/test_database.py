"""
Unit Tests for Database Module (SQLite).
"""

import os
import tempfile
import pytest
import pandas as pd
from src.database import (
    init_db,
    insert_transaction,
    bulk_insert_transactions,
    get_all_transactions,
    update_transaction,
    delete_transaction,
    clear_all_transactions,
    get_budgets,
    set_budget,
    get_transaction_stats,
)


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_init_db_creates_tables_and_budgets(temp_db):
    budgets = get_budgets(temp_db)
    assert len(budgets) > 0
    assert "Groceries" in budgets
    assert budgets["Groceries"] == 450.0


def test_insert_and_get_transaction(temp_db):
    tx_id = insert_transaction(
        date="2026-10-01",
        description="Whole Foods",
        category="Groceries",
        amount=84.50,
        payment_method="Card",
        notes="Organic vegetables",
        db_path=temp_db,
    )
    assert tx_id > 0

    df = get_all_transactions(temp_db)
    assert len(df) == 1
    assert df.iloc[0]["description"] == "Whole Foods"
    assert df.iloc[0]["amount"] == 84.50
    assert df.iloc[0]["category"] == "Groceries"


def test_bulk_insert_transactions(temp_db):
    records = [
        {"date": "2026-10-01", "description": "Starbucks", "category": "Dining", "amount": 6.50, "payment_method": "Card"},
        {"date": "2026-10-02", "description": "Trader Joe's", "category": "Groceries", "amount": 42.00, "payment_method": "Card"},
        {"date": "2026-10-03", "description": "Shell Gas", "category": "Transportation", "amount": 35.00, "payment_method": "Cash"},
    ]
    count = bulk_insert_transactions(records, temp_db)
    assert count == 3

    stats = get_transaction_stats(temp_db)
    assert stats["total_count"] == 3
    assert stats["total_spent"] == pytest.approx(83.50, rel=1e-2)


def test_filter_transactions(temp_db):
    insert_transaction("2026-09-15", "Apple Store", "Shopping", 199.0, db_path=temp_db)
    insert_transaction("2026-10-10", "Chipotle", "Dining", 15.5, db_path=temp_db)

    # Filter by category
    df_cat = get_all_transactions(temp_db, category="Dining")
    assert len(df_cat) == 1
    assert df_cat.iloc[0]["description"] == "Chipotle"

    # Filter by search
    df_search = get_all_transactions(temp_db, search="Apple")
    assert len(df_search) == 1
    assert df_search.iloc[0]["category"] == "Shopping"


def test_update_and_delete_transaction(temp_db):
    tx_id = insert_transaction("2026-10-05", "Cafe", "Dining", 10.0, db_path=temp_db)

    # Update
    updated = update_transaction(tx_id, "2026-10-05", "Bistro Cafe", "Dining", 15.0, db_path=temp_db)
    assert updated is True

    df = get_all_transactions(temp_db)
    assert df.iloc[0]["description"] == "Bistro Cafe"
    assert df.iloc[0]["amount"] == 15.0

    # Delete
    deleted = delete_transaction(tx_id, db_path=temp_db)
    assert deleted is True
    assert len(get_all_transactions(temp_db)) == 0


def test_budget_upsert(temp_db):
    set_budget("Entertainment", 275.0, db_path=temp_db)
    budgets = get_budgets(temp_db)
    assert budgets["Entertainment"] == 275.0
