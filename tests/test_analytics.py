"""
Unit Tests for Financial Analytics Engine.
Tests KPI calculations, monthly summaries, MoM growth, trends, and budget comparisons.
"""

import pandas as pd
import pytest
from src.analytics import (
    calculate_kpis,
    get_monthly_summary,
    get_category_breakdown,
    get_daily_trend,
    get_budget_comparison,
    get_top_merchants,
)


@pytest.fixture
def sample_tx_df():
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "date": ["2026-08-15", "2026-08-20", "2026-09-01", "2026-09-10", "2026-09-15"],
        "description": ["Whole Foods", "Starbucks", "Rent", "Whole Foods", "Best Buy"],
        "category": ["Groceries", "Dining", "Rent & Housing", "Groceries", "Shopping"],
        "amount": [140.0, 15.0, 1200.0, 80.0, 200.0],
        "payment_method": ["Card", "Card", "Bank Transfer", "Card", "Card"],
        "notes": ["", "", "Monthly rent", "", "Monitor"],
    })


def test_calculate_kpis(sample_tx_df):
    kpis = calculate_kpis(sample_tx_df)
    assert kpis["total_spend"] == 1635.0
    assert kpis["transaction_count"] == 5
    assert kpis["avg_transaction"] == 327.0
    assert kpis["max_expense"] == 1200.0
    assert kpis["top_category"] == "Rent & Housing"


def test_calculate_kpis_empty():
    kpis = calculate_kpis(pd.DataFrame())
    assert kpis["total_spend"] == 0.0
    assert kpis["transaction_count"] == 0


def test_get_monthly_summary(sample_tx_df):
    monthly = get_monthly_summary(sample_tx_df)
    assert len(monthly) == 2
    assert "2026-08" in monthly["year_month"].values
    assert "2026-09" in monthly["year_month"].values

    aug = monthly[monthly["year_month"] == "2026-08"].iloc[0]
    assert aug["total_spend"] == 155.0

    sep = monthly[monthly["year_month"] == "2026-09"].iloc[0]
    assert sep["total_spend"] == 1480.0
    assert sep["mom_change"] == 1325.0


def test_get_category_breakdown(sample_tx_df):
    cat_df = get_category_breakdown(sample_tx_df)
    assert len(cat_df) == 4
    assert cat_df.iloc[0]["category"] == "Rent & Housing"
    assert cat_df["percentage"].sum() == pytest.approx(100.0, rel=1e-1)


def test_get_budget_comparison(sample_tx_df):
    budgets = {"Groceries": 250.0, "Dining": 50.0, "Rent & Housing": 1000.0}
    comp = get_budget_comparison(sample_tx_df, budgets, target_year_month="2026-09")

    # In 2026-09: Rent is 1200, budget is 1000 -> Over Budget
    rent_row = comp[comp["category"] == "Rent & Housing"].iloc[0]
    assert rent_row["status"] == "Over Budget"
    assert rent_row["remaining"] == -200.0

    # In 2026-09: Groceries is 80, budget is 250 -> Within Budget
    groc_row = comp[comp["category"] == "Groceries"].iloc[0]
    assert groc_row["status"] == "Within Budget"
    assert groc_row["remaining"] == 170.0


def test_get_top_merchants(sample_tx_df):
    top = get_top_merchants(sample_tx_df, n=2)
    assert len(top) == 2
    assert top.iloc[0]["description"] == "Rent"
    assert top.iloc[1]["description"] == "Whole Foods"
    assert top.iloc[1]["total_spend"] == 220.0
