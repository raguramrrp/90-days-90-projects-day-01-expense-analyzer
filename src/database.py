"""
Database Module for Personal Expense Intelligence.
Handles SQLite schema setup, CRUD operations, budget tracking, and batch ingestion.
"""

from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict, List, Optional
import pandas as pd

DEFAULT_DB_PATH = os.environ.get("EXPENSE_DB_PATH", "expenses.db")

DEFAULT_BUDGETS = {
    "Groceries": 450.0,
    "Dining": 250.0,
    "Rent & Housing": 1200.0,
    "Utilities": 200.0,
    "Transportation": 180.0,
    "Entertainment": 150.0,
    "Shopping": 200.0,
    "Healthcare": 100.0,
    "Subscriptions": 60.0,
    "Education": 100.0,
    "Travel": 150.0,
    "Miscellaneous": 100.0,
}


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Return a thread-safe connection to SQLite with row-factory enabled."""
    target_path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(target_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables and default budget limits."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Create transactions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'Card',
            notes TEXT DEFAULT ''
        )
        """
    )

    # Create budgets table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            monthly_budget REAL NOT NULL
        )
        """
    )

    # Seed default budgets if table is empty
    cursor.execute("SELECT COUNT(*) AS count FROM budgets")
    if cursor.fetchone()["count"] == 0:
        cursor.executemany(
            "INSERT INTO budgets (category, monthly_budget) VALUES (?, ?)",
            list(DEFAULT_BUDGETS.items()),
        )

    # Create indices for fast filtering
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_cat ON transactions(category)")

    conn.commit()
    conn.close()


def insert_transaction(
    date: str,
    description: str,
    category: str,
    amount: float,
    payment_method: str = "Card",
    notes: str = "",
    db_path: Optional[str] = None,
) -> int:
    """Insert a single transaction into the database."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transactions (date, description, category, amount, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (date.strip(), description.strip(), category.strip(), float(amount), payment_method.strip(), notes.strip()),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def bulk_insert_transactions(
    records: List[Dict[str, Any]], db_path: Optional[str] = None
) -> int:
    """Insert multiple transactions within a single transaction block."""
    if not records:
        return 0

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    payload = [
        (
            str(r["date"]).strip(),
            str(r["description"]).strip(),
            str(r.get("category", "Miscellaneous")).strip(),
            float(r["amount"]),
            str(r.get("payment_method", "Card")).strip(),
            str(r.get("notes", "")).strip(),
        )
        for r in records
    ]

    cursor.executemany(
        """
        INSERT INTO transactions (date, description, category, amount, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        payload,
    )
    conn.commit()
    inserted_count = cursor.rowcount
    conn.close()
    return inserted_count


def get_all_transactions(
    db_path: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> pd.DataFrame:
    """Retrieve filtered transactions as a pandas DataFrame."""
    conn = get_db_connection(db_path)
    query = "SELECT id, date, description, category, amount, payment_method, notes FROM transactions WHERE 1=1"
    params: List[Any] = []

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (description LIKE ? OR notes LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term])

    query += " ORDER BY date DESC, id DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

    return df


def update_transaction(
    transaction_id: int,
    date: str,
    description: str,
    category: str,
    amount: float,
    payment_method: str = "Card",
    notes: str = "",
    db_path: Optional[str] = None,
) -> bool:
    """Update an existing transaction record by ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE transactions
        SET date = ?, description = ?, category = ?, amount = ?, payment_method = ?, notes = ?
        WHERE id = ?
        """,
        (date, description, category, float(amount), payment_method, notes, int(transaction_id)),
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_transaction(transaction_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a transaction by ID."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (int(transaction_id),))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def clear_all_transactions(db_path: Optional[str] = None) -> int:
    """Delete all transactions from the database."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted


def get_budgets(db_path: Optional[str] = None) -> Dict[str, float]:
    """Retrieve all monthly category budgets."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT category, monthly_budget FROM budgets ORDER BY category ASC")
    rows = cursor.fetchall()
    conn.close()
    return {row["category"]: float(row["monthly_budget"]) for row in rows}


def set_budget(category: str, monthly_budget: float, db_path: Optional[str] = None) -> None:
    """Upsert monthly budget for a specific category."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO budgets (category, monthly_budget)
        VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET monthly_budget=excluded.monthly_budget
        """,
        (category.strip(), float(monthly_budget)),
    )
    conn.commit()
    conn.close()


def get_transaction_stats(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Calculate aggregate summary stats directly from SQLite."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            COUNT(*) AS total_count,
            COALESCE(SUM(amount), 0.0) AS total_spent,
            COALESCE(AVG(amount), 0.0) AS avg_amount,
            COALESCE(MIN(date), '') AS min_date,
            COALESCE(MAX(date), '') AS max_date,
            COUNT(DISTINCT category) AS category_count
        FROM transactions
        """
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row)
