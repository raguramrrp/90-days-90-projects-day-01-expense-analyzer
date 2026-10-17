"""
Anomaly Detection Module for Personal Expense Intelligence.
Identifies unusual expenses, spending spikes, and atypical patterns using:
1. Category-specific statistical Z-scores and IQR thresholds.
2. Unsupervised Machine Learning via Scikit-Learn IsolationForest.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


class ExpenseAnomalyDetector:
    """Detects statistical outliers and atypical spending behaviors in transactions."""

    def __init__(self, contamination: float = 0.05, z_threshold: float = 2.0):
        self.contamination = contamination
        self.z_threshold = z_threshold

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze a DataFrame of transactions and append anomaly indicators.
        Expected columns: ['id', 'date', 'description', 'category', 'amount']
        Returns a DataFrame augmented with:
          - is_anomaly (bool)
          - anomaly_score (float, 0 to 100)
          - anomaly_reason (str)
          - severity (str: 'Normal', 'Low', 'Medium', 'High')
        """
        if df.empty:
            result = df.copy()
            result["is_anomaly"] = False
            result["anomaly_score"] = 0.0
            result["anomaly_reason"] = "No transactions"
            result["severity"] = "Normal"
            return result

        result = df.copy()
        result["is_anomaly"] = False
        result["anomaly_score"] = 0.0
        result["anomaly_reason"] = "Normal spending"
        result["severity"] = "Normal"

        if len(result) < 3:
            return result

        # Ensure datetime and numeric columns
        result["parsed_date"] = pd.to_datetime(result["date"], errors="coerce")
        result["numeric_amount"] = pd.to_numeric(result["amount"], errors="coerce").fillna(0.0)

        # 1. Statistical Per-Category Outlier Detection
        category_stats = (
            result.groupby("category")["numeric_amount"]
            .agg(mean="mean", std="std", count="count", median="median", q25=lambda x: x.quantile(0.25), q75=lambda x: x.quantile(0.75))
            .reset_index()
        )
        cat_stats_map = {row["category"]: row for _, row in category_stats.iterrows()}

        reasons = []
        scores = []
        is_anom_list = []
        severities = []

        for _, row in result.iterrows():
            cat = row["category"]
            amt = row["numeric_amount"]
            stat = cat_stats_map.get(cat)

            is_outlier = False
            reason_text = "Within expected range"
            score = 10.0
            sev = "Normal"

            if stat is not None and stat["count"] >= 3:
                mean = stat["mean"]
                std = stat["std"] if stat["std"] > 0 else 1.0
                z = (amt - mean) / std
                iqr = stat["q75"] - stat["q25"]
                upper_bound = stat["q75"] + (1.5 * iqr) if iqr > 0 else mean + (2 * std)

                # Check if unusually high
                if amt > upper_bound and z >= self.z_threshold:
                    is_outlier = True
                    ratio = amt / mean if mean > 0 else 1.0
                    reason_text = f"Amount is {ratio:.1f}x higher than the {cat} average of ${mean:.2f}"
                    score = min(99.0, 50.0 + (z * 15.0))

                    if z > 3.5:
                        sev = "High"
                    elif z > 2.5:
                        sev = "Medium"
                    else:
                        sev = "Low"
                elif amt <= 0.0:
                    is_outlier = True
                    reason_text = "Zero or negative amount recorded"
                    score = 80.0
                    sev = "Medium"

            is_anom_list.append(is_outlier)
            reasons.append(reason_text)
            scores.append(round(score, 1))
            severities.append(sev)

        result["is_anomaly"] = is_anom_list
        result["anomaly_score"] = scores
        result["anomaly_reason"] = reasons
        result["severity"] = severities

        # 2. Unsupervised Isolation Forest for multi-feature pattern outliers
        if len(result) >= 10:
            try:
                features = pd.DataFrame()
                features["amount"] = result["numeric_amount"]
                features["day_of_month"] = result["parsed_date"].dt.day.fillna(1)
                features["day_of_week"] = result["parsed_date"].dt.dayofweek.fillna(0)

                # Category frequency encoding
                cat_counts = result["category"].value_counts()
                features["category_freq"] = result["category"].map(cat_counts).fillna(1)

                # Ratio to category average
                cat_means = result.groupby("category")["numeric_amount"].transform("mean")
                features["ratio_to_mean"] = (result["numeric_amount"] / cat_means.replace(0, 1)).fillna(1.0)

                iso = IsolationForest(
                    contamination=min(0.15, max(0.02, self.contamination)),
                    random_state=42,
                    n_estimators=100,
                )
                preds = iso.fit_predict(features)
                raw_scores = iso.decision_function(features)

                # IsolationForest returns -1 for outliers
                for idx, (pred, raw_s) in enumerate(zip(preds, raw_scores)):
                    if pred == -1:
                        # If not already flagged by Z-score, flag with IsolationForest detection
                        if not result.iloc[idx]["is_anomaly"]:
                            result.iat[idx, result.columns.get_loc("is_anomaly")] = True
                            computed_score = round(min(95.0, max(60.0, (0.5 - raw_s) * 100.0)), 1)
                            result.iat[idx, result.columns.get_loc("anomaly_score")] = computed_score
                            result.iat[idx, result.columns.get_loc("anomaly_reason")] = (
                                "Atypical spending cluster flagged by ML Isolation Forest"
                            )
                            result.iat[idx, result.columns.get_loc("severity")] = (
                                "Medium" if computed_score > 75 else "Low"
                            )
            except Exception:
                # Graceful fallback to statistical checks only
                pass

        # Cleanup internal temporary columns
        if "parsed_date" in result.columns:
            result.drop(columns=["parsed_date"], inplace=True)
        if "numeric_amount" in result.columns:
            result.drop(columns=["numeric_amount"], inplace=True)

        return result


def get_anomalies_summary(df: pd.DataFrame) -> Dict[str, any]:
    """Provide executive summary of detected anomalies."""
    if df.empty or "is_anomaly" not in df.columns:
        return {"anomaly_count": 0, "total_anomaly_amount": 0.0, "high_severity_count": 0}

    anomalies = df[df["is_anomaly"] == True]
    return {
        "anomaly_count": len(anomalies),
        "total_anomaly_amount": float(anomalies["amount"].sum()),
        "high_severity_count": len(anomalies[anomalies["severity"] == "High"]),
        "medium_severity_count": len(anomalies[anomalies["severity"] == "Medium"]),
    }
