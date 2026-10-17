# Project Overview: Personal Expense Intelligence & Spending Analyzer

**Day 1 — 90 Days 90 Projects Challenge**  
**Domain:** Financial Technology (FinTech) & Data Analytics  
**Target User:** Individuals seeking automated clarity, discipline, and actionable insights over their personal cash outflows.

---

## 1. Executive Summary

Personal Expense Intelligence & Spending Analyzer (**ExpenseIQ**) is an interactive, local-first personal finance platform built with Python, SQLite, Pandas, Scikit-learn, and Streamlit.

While many individuals track transactions or download monthly bank CSV statements, they rarely extract actionable intelligence. Raw bank transaction logs are fragmented with cryptic merchant strings (`SQ *TRADER JOE 481`, `AMZN Mktp US*2K3`, `WTR/SWR CITY UTIL`), lack unified taxonomy, provide zero automatic anomaly detection, and fail to track burn rate or budget variances over time.

ExpenseIQ solves this problem end-to-end:
1. **Automated Ingestion & Normalization:** Intelligently maps arbitrary bank/credit card CSV schemas and parses cryptic transactions.
2. **Hybrid Categorization Engine:** Combines instant regex/keyword taxonomy rules with a trained TF-IDF + Logistic Regression Machine Learning text classifier.
3. **Multi-Horizon Financial Analytics:** Computes daily burn rates, Month-over-Month (MoM) growth rates, category distributions, and top merchant velocity.
4. **AI-Powered Anomaly Detection:** Detects irregular spending spikes and atypical transactions using both category Z-score/IQR statistical thresholds and unsupervised Scikit-learn `IsolationForest`.
5. **Budget Variance Management:** Tracks actual category spend against customizable monthly budget caps, highlighting nearing limits (>85%) and overspending breaches.

---

## 2. Core Problem & Value Proposition

| Pain Point | Traditional Method | ExpenseIQ Solution |
|------------|--------------------|---------------------|
| Cryptic merchant descriptions | Manual manual categorization row by row in Excel | Hybrid Rule + TF-IDF ML categorizer auto-classifies transactions with high confidence |
| Unnoticed spending leaks | Only reviewed at end of year during taxes | Real-time outlier detection (Isolation Forest + Z-score) alerts user to atypical charges |
| Budget variance blind spots | Fixed mental budget with no visibility | Dynamic budget vs. actual tracking with warning thresholds |
| Data privacy risks | Cloud apps demanding bank credentials & selling data | 100% local-first SQLite database running on the user's machine; zero data egress |

---

## 3. System Scope & MVP Boundaries

### In Scope (MVP)
- Single-user local-first SQLite database with automatic table creation and default category budgets.
- CSV statement upload with heuristic column mapping and pre-commit preview.
- Manual transaction recording with real-time category suggestion.
- Hybrid rule-based and ML categorization engine (TF-IDF + Logistic Regression).
- Anomaly detection using per-category Z-scores and Isolation Forest clustering.
- Interactive Plotly visualizations (monthly trends, category donuts, moving averages, top merchants).
- Budget configuration editor and budget health tracking.
- Filterable and searchable transaction ledger with CSV and JSON exports.

### Out of Scope (Future Phases)
- Direct OAuth Open Banking sync (e.g. Plaid API) requiring paid compliance licenses.
- Multi-currency conversion with live forex rates.
- Multi-user authentication and cloud PostgreSQL synchronization.
