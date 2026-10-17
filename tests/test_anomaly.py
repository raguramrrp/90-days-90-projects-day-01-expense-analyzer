"""
Unit Tests for Anomaly Detection Engine.
Tests statistical outlier detection and Isolation Forest behavior.
"""

import pandas as pd
import pytest
from src.anomaly_detector import ExpenseAnomalyDetector, get_anomalies_summary


def test_anomaly_detection_flags_outlier():
    # Build typical groceries dataset with 1 extreme spike
    dates = [f"2026-10-{i:02d}" for i in range(1, 15)]
    amounts = [25.0, 30.0, 28.0, 32.0, 24.0, 35.0, 29.0, 31.0, 27.0, 33.0, 26.0, 34.0, 30.0, 550.0]
    df = pd.DataFrame({
        "id": list(range(1, 15)),
        "date": dates,
        "description": ["Grocery Store"] * 13 + ["Massive Supermarket Order"],
        "category": ["Groceries"] * 14,
        "amount": amounts,
        "payment_method": ["Card"] * 14,
        "notes": [""] * 14,
    })

    detector = ExpenseAnomalyDetector(z_threshold=2.0)
    result = detector.detect_anomalies(df)

    assert "is_anomaly" in result.columns
    assert "severity" in result.columns

    # The 550.0 transaction must be flagged as anomaly
    spike_row = result[result["amount"] == 550.0].iloc[0]
    assert spike_row["is_anomaly"] is True or spike_row["is_anomaly"] == 1
    assert spike_row["severity"] in ["High", "Medium"]
    assert "higher than the Groceries average" in spike_row["anomaly_reason"]

    summary = get_anomalies_summary(result)
    assert summary["anomaly_count"] >= 1
    assert summary["total_anomaly_amount"] >= 550.0


def test_empty_dataframe_anomaly():
    detector = ExpenseAnomalyDetector()
    res = detector.detect_anomalies(pd.DataFrame())
    assert res.empty or len(res) == 0
