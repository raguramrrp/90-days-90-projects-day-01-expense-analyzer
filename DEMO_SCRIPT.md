# 90-Second Demonstration Script

Use this script for recorded video walkthroughs, recruiter presentations, or live hackathon demos.

---

## Demo Overview
- **Project Title:** Personal Expense Intelligence & Spending Analyzer (ExpenseIQ)
- **Target Duration:** 90 seconds
- **Primary Goal:** Showcase real-world problem resolution, automated ML categorization, interactive visual analytics, and AI anomaly detection.

---

## Scene-by-Scene Walkthrough

### 0:00 – 0:15 | The Problem & Architecture Hook
> *"Hi everyone! Most people track their expenses in spreadsheets or banking apps, but raw bank statements are messy, cryptic, and rarely tell you where your money is actually leaking.  
> This is ExpenseIQ — an autonomous, privacy-first personal expense intelligence engine built with Streamlit, Python, SQLite, and Scikit-learn."*

- **Visual:** Show terminal running `run.bat`, then transition smoothly to the browser dashboard at `http://localhost:8501`.

### 0:15 – 0:35 | Automated Ingestion & Hybrid ML Categorization
> *"Let's head over to 'Upload & Ingest'. Instead of manually labeling rows, I can drag and drop any bank statement CSV.  
> ExpenseIQ automatically detects columns and runs a hybrid categorization engine: blending over 100 domain regex rules with a TF-IDF Logistic Regression text classifier.  
> Notice how cryptic strings like 'SQ *TRADER JOE' and 'UBR* PENDING TRIP' are instantly classified into Groceries and Transportation with high confidence. One click commits them atomically to our local SQLite database."*

- **Visual:** Navigate to `Upload & Ingest`, preview the sample CSV, show predicted categories, and click `Confirm & Commit`.

### 0:35 – 0:55 | Financial Intelligence Dashboard
> *"Back on the Dashboard, our financial health is instantly computed:  
> - We see our total spend and real-time daily burn rate.  
> - The interactive Plotly charts break down Month-over-Month outflow and category distribution.  
> - The 7-day moving average reveals underlying spending velocity without daily noise.  
> - And our top merchants show us exactly who we pay most frequently."*

- **Visual:** Hover over the Monthly Trend bars, interact with the Category Donut chart, and point to the Daily Burn Rate KPI.

### 0:55 – 1:15 | AI Anomaly Inspector & Budget Comparison
> *"Now for the core AI feature: Anomaly Detection.  
> Under 'Reports & Budgets', ExpenseIQ combines category-specific Z-scores and unsupervised Isolation Forest to catch unusual spending spikes.  
> Here it flagged an emergency auto repair and a hospital visit that were 4.5x higher than typical category averages.  
> Alongside that, our Budget Variance tracker monitors our monthly caps, showing utilization bars in green, warning at 85%, and alerting in red when a budget is breached."*

- **Visual:** Switch to `Reports & Budgets`, open `AI Anomaly Inspector`, show the outlier table, then scroll to the `Budget vs Actual` variance chart.

### 1:15 – 1:30 | Filtering, Exports & Conclusion
> *"Finally, in the Transactions ledger, we can filter by anomaly tags, search merchants in milliseconds, and export clean, audit-ready CSV or JSON files.  
> The entire project is fully tested with Pytest, packaged for one-click Windows execution, and built as Day 1 of my 90 Days – 90 Projects Challenge. Thank you!"*

- **Visual:** Filter by `Flagged Anomalies Only`, click `Export to CSV`, and show the clean downloaded file.
