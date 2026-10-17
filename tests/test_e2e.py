"""
End-to-End Workflow Integration Test.
Simulates:
1. Ingesting raw CSV with missing categories
2. Applying rule/ML auto-categorization
3. Storing into SQLite database
4. Executing analytics calculations & anomaly detection
5. Generating budget comparisons and export buffers
"""

import io
import os
import tempfile
import pandas as pd
import pytest
from src.database import (
    init_db,
    bulk_insert_transactions,
    get_all_transactions,
    get_budgets,
)
from src.categorizer import get_categorizer
from src.analytics import calculate_kpis, get_monthly_summary, get_budget_comparison
from src.anomaly_detector import ExpenseAnomalyDetector


def test_end_to_end_pipeline():
    # 1. Setup isolated database
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(db_path)

    try:
        # 2. Raw incoming statement with no categories
        raw_csv_data = """date,description,amount,payment_method
2026-08-01,Avalon Bay Apartment Rent,1250.00,Bank Transfer
2026-08-05,Trader Joe's,85.20,Card
2026-08-10,Starbucks Coffee,7.50,Card
2026-08-15,Netflix Premium,19.99,Card
2026-08-20,Shell Gas Station,45.00,Card
2026-08-21,Chevron Fuel Station,40.00,Card
2026-08-22,Metro Transit Pass,30.00,Card
2026-08-25,Trader Joe's,92.40,Card
2026-08-28,Whole Foods Market,110.00,Card
2026-08-30,Emergency Auto Transmission Repair,950.00,Card
"""
        df_raw = pd.read_csv(io.StringIO(raw_csv_data))

        # 3. Categorization step
        categorizer = get_categorizer()
        records = []
        for _, row in df_raw.iterrows():
            desc = str(row["description"])
            cat, method, conf = categorizer.predict(desc)
            records.append({
                "date": str(row["date"]),
                "description": desc,
                "category": cat,
                "amount": float(row["amount"]),
                "payment_method": str(row["payment_method"]),
                "notes": f"Auto-classified via {method}",
            })

        assert len(records) == 10
        assert records[0]["category"] == "Rent & Housing"
        assert records[1]["category"] == "Groceries"
        assert records[2]["category"] == "Dining"
        assert records[3]["category"] == "Subscriptions"
        assert records[4]["category"] == "Transportation"

        # 4. Insert into database
        count = bulk_insert_transactions(records, db_path=db_path)
        assert count == 10

        # 5. Query from database
        stored_df = get_all_transactions(db_path=db_path)
        assert len(stored_df) == 10

        # 6. Analytics computation
        kpis = calculate_kpis(stored_df)
        assert kpis["total_spend"] == 2630.09
        assert kpis["transaction_count"] == 10

        monthly_df = get_monthly_summary(stored_df)
        assert len(monthly_df) == 1
        assert monthly_df.iloc[0]["total_spend"] == 2630.09

        budgets = get_budgets(db_path=db_path)
        budget_comp = get_budget_comparison(stored_df, budgets, target_year_month="2026-08")
        assert not budget_comp.empty

        # 7. Anomaly detection
        detector = ExpenseAnomalyDetector(z_threshold=2.0)
        df_anom = detector.detect_anomalies(stored_df)
        anomalies = df_anom[df_anom["is_anomaly"] == True]

        # The $950 auto repair should be flagged
        flagged_descs = anomalies["description"].tolist()
        assert "Emergency Auto Transmission Repair" in flagged_descs

        # 8. Export check
        csv_out = io.StringIO()
        df_anom.to_csv(csv_out, index=False)
        assert len(csv_out.getvalue()) > 100

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
