"""
Analytics Module for Personal Expense Intelligence.
Computes financial KPIs, monthly aggregations, category breakdowns,
time-series spending trends, and budget variance comparisons.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np


def ensure_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure DataFrame has a parsed datetime column and valid numeric amount."""
    data = df.copy()
    if data.empty:
        return data
    if not pd.api.types.is_datetime64_any_dtype(data["date"]):
        data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0.0)
    data["year_month"] = data["date"].dt.strftime("%Y-%m")
    data["month_name"] = data["date"].dt.strftime("%b %Y")
    return data


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute high-level executive financial metrics."""
    if df.empty:
        return {
            "total_spend": 0.0,
            "transaction_count": 0,
            "avg_transaction": 0.0,
            "max_expense": 0.0,
            "max_expense_desc": "N/A",
            "active_days": 0,
            "daily_burn_rate": 0.0,
            "top_category": "N/A",
            "top_category_spend": 0.0,
        }

    data = ensure_datetime(df)
    total_spend = float(data["amount"].sum())
    tx_count = len(data)
    avg_tx = float(data["amount"].mean())

    max_idx = data["amount"].idxmax()
    max_row = data.loc[max_idx]
    max_expense = float(max_row["amount"])
    max_expense_desc = f"{max_row['description']} ({max_row['category']})"

    date_span = (data["date"].max() - data["date"].min()).days + 1
    daily_burn_rate = float(total_spend / max(1, date_span))

    cat_totals = data.groupby("category")["amount"].sum()
    top_cat = cat_totals.idxmax() if not cat_totals.empty else "N/A"
    top_cat_spend = float(cat_totals.max()) if not cat_totals.empty else 0.0

    return {
        "total_spend": round(total_spend, 2),
        "transaction_count": tx_count,
        "avg_transaction": round(avg_tx, 2),
        "max_expense": round(max_expense, 2),
        "max_expense_desc": max_expense_desc,
        "active_days": max(1, date_span),
        "daily_burn_rate": round(daily_burn_rate, 2),
        "top_category": top_cat,
        "top_category_spend": round(top_cat_spend, 2),
    }


def get_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate spending by month with Month-over-Month (MoM) growth calculations.
    Returns DataFrame with columns: ['year_month', 'total_spend', 'tx_count', 'avg_spend', 'mom_change', 'mom_growth_pct']
    """
    if df.empty:
        return pd.DataFrame(columns=["year_month", "total_spend", "tx_count", "avg_spend", "mom_change", "mom_growth_pct"])

    data = ensure_datetime(df)
    monthly = (
        data.groupby("year_month")
        .agg(
            total_spend=("amount", "sum"),
            tx_count=("amount", "count"),
            avg_spend=("amount", "mean"),
        )
        .reset_index()
        .sort_values("year_month")
    )

    monthly["mom_change"] = monthly["total_spend"].diff().fillna(0.0)
    monthly["mom_growth_pct"] = (
        (monthly["mom_change"] / monthly["total_spend"].shift(1).replace(0, np.nan)) * 100.0
    ).fillna(0.0)

    monthly["total_spend"] = monthly["total_spend"].round(2)
    monthly["avg_spend"] = monthly["avg_spend"].round(2)
    monthly["mom_change"] = monthly["mom_change"].round(2)
    monthly["mom_growth_pct"] = monthly["mom_growth_pct"].round(1)

    return monthly


def get_category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total and percentage spending grouped by category."""
    if df.empty:
        return pd.DataFrame(columns=["category", "total_spend", "tx_count", "percentage"])

    data = ensure_datetime(df)
    total_all = data["amount"].sum()

    cat_df = (
        data.groupby("category")
        .agg(
            total_spend=("amount", "sum"),
            tx_count=("amount", "count"),
            avg_spend=("amount", "mean"),
        )
        .reset_index()
        .sort_values("total_spend", ascending=False)
    )

    if total_all > 0:
        cat_df["percentage"] = ((cat_df["total_spend"] / total_all) * 100.0).round(1)
    else:
        cat_df["percentage"] = 0.0

    cat_df["total_spend"] = cat_df["total_spend"].round(2)
    cat_df["avg_spend"] = cat_df["avg_spend"].round(2)

    return cat_df


def get_daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Generate daily spending timeline with a 7-day rolling average."""
    if df.empty:
        return pd.DataFrame(columns=["date", "daily_spend", "rolling_7d_avg"])

    data = ensure_datetime(df)
    daily = (
        data.groupby(data["date"].dt.date)
        .agg(daily_spend=("amount", "sum"), tx_count=("amount", "count"))
        .reset_index()
        .sort_values("date")
    )

    daily["date"] = pd.to_datetime(daily["date"])
    # Reindex to full continuous date range
    full_idx = pd.date_range(daily["date"].min(), daily["date"].max(), freq="D")
    daily = daily.set_index("date").reindex(full_idx, fill_value=0.0).rename_axis("date").reset_index()

    daily["rolling_7d_avg"] = daily["daily_spend"].rolling(window=7, min_periods=1).mean().round(2)
    daily["daily_spend"] = daily["daily_spend"].round(2)

    return daily


def get_budget_comparison(
    df: pd.DataFrame, budgets: Dict[str, float], target_year_month: Optional[str] = None
) -> pd.DataFrame:
    """
    Compare actual monthly category spend against target budget thresholds.
    Flags:
      - 'Within Budget' (<85%)
      - 'Near Limit' (85% - 100%)
      - 'Over Budget' (>100%)
    """
    if df.empty:
        rows = []
        for cat, bgt in budgets.items():
            rows.append({
                "category": cat,
                "budget": bgt,
                "actual_spend": 0.0,
                "remaining": bgt,
                "utilization_pct": 0.0,
                "status": "Within Budget",
            })
        return pd.DataFrame(rows)

    data = ensure_datetime(df)

    # Filter to specific month if requested, else default to latest month
    if target_year_month:
        month_data = data[data["year_month"] == target_year_month]
    else:
        latest_month = data["year_month"].max()
        month_data = data[data["year_month"] == latest_month]

    actual_by_cat = month_data.groupby("category")["amount"].sum().to_dict()

    comparison_records = []
    all_categories = sorted(set(list(budgets.keys()) + list(actual_by_cat.keys())))

    for cat in all_categories:
        bgt = float(budgets.get(cat, 0.0))
        actual = float(actual_by_cat.get(cat, 0.0))
        remaining = bgt - actual
        utilization = (actual / bgt * 100.0) if bgt > 0 else (100.0 if actual > 0 else 0.0)

        if bgt > 0:
            if actual > bgt:
                status = "Over Budget"
            elif actual >= 0.85 * bgt:
                status = "Near Limit"
            else:
                status = "Within Budget"
        else:
            status = "No Budget Set"

        comparison_records.append({
            "category": cat,
            "budget": round(bgt, 2),
            "actual_spend": round(actual, 2),
            "remaining": round(remaining, 2),
            "utilization_pct": round(utilization, 1),
            "status": status,
        })

    comp_df = pd.DataFrame(comparison_records)
    return comp_df.sort_values("actual_spend", ascending=False).reset_index(drop=True)


def get_top_merchants(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Identify top merchants/descriptions by spending volume."""
    if df.empty:
        return pd.DataFrame(columns=["description", "category", "total_spend", "tx_count"])

    data = ensure_datetime(df)
    merchants = (
        data.groupby(["description", "category"])
        .agg(total_spend=("amount", "sum"), tx_count=("amount", "count"))
        .reset_index()
        .sort_values("total_spend", ascending=False)
        .head(n)
    )

    merchants["total_spend"] = merchants["total_spend"].round(2)
    return merchants
