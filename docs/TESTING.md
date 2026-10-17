# Testing Strategy & Quality Assurance Report

This document details the test suites, execution commands, coverage areas, and quality checks established for the Personal Expense Intelligence platform.

---

## 1. Test Architecture & Directory Structure

```
tests/
├── test_database.py     # SQLite schema, indexing, CRUD, filtering, budgets, stats
├── test_categorizer.py  # Regex rules, ML text classification, fallback logic
├── test_analytics.py    # KPIs, MoM growth, trends, budget variance, top merchants
├── test_anomaly.py      # Statistical Z-score & Scikit-Learn IsolationForest outlier checks
└── test_e2e.py          # End-to-end integration: CSV parse -> DB commit -> Analytics -> Export
```

---

## 2. Test Execution Commands

### Automated Test Runner (Windows Batch Script)
```cmd
test.bat
```

### Direct Pytest Execution (Virtual Environment)
```powershell
.\.venv\Scripts\pytest -v --tb=short
```

---

## 3. Test Suites & Assertions Matrix

| Test Suite | Function Tested | Validation Objective | Expected Result |
|------------|-----------------|----------------------|-----------------|
| `test_database.py` | `init_db` | Table creation & default budget seeding | Tables exist, default categories initialized |
| `test_database.py` | `insert_transaction` | Single record insertion & retrieval | Correct fields stored & returned as DataFrame |
| `test_database.py` | `bulk_insert_transactions` | Atomic batch ingestion | All records inserted, count & stats match |
| `test_database.py` | `get_all_transactions` | Filtering by category, date, and query | Only matching records returned |
| `test_database.py` | `update_transaction` | In-place record update | Changes persisted accurately |
| `test_database.py` | `delete_transaction` | Deletion by primary key | Record removed safely |
| `test_categorizer.py` | `predict` | Rule-based regex pattern match | Accurately classifies groceries, dining, gas, etc. |
| `test_categorizer.py` | `predict` | Fallback classification | Unknown strings return valid taxonomy category |
| `test_categorizer.py` | `categorize_dataframe` | Batch column inference | Returns aligned array of predicted labels |
| `test_analytics.py` | `calculate_kpis` | Executive summary metrics | Correct total spend, count, max expense, burn rate |
| `test_analytics.py` | `get_monthly_summary` | MoM growth calculations | Correct monthly delta and percentage shifts |
| `test_analytics.py` | `get_budget_comparison` | Budget variance thresholds | Accurate classification (Within, Near Limit, Over) |
| `test_anomaly.py` | `detect_anomalies` | Statistical Z-score outlier flagging | Extreme spikes ($550 in $30 avg) flagged as High severity |
| `test_e2e.py` | Full Pipeline | End-to-end workflow verification | CSV parse -> DB insert -> Analytics -> Export passes cleanly |
