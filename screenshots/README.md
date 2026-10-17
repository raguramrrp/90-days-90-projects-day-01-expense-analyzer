# Application Screenshots Guide

This directory holds visual demonstration assets for **ExpenseIQ (Personal Expense Intelligence & Spending Analyzer)**.

---

## Capturing Genuine Screenshots

To capture clean, presentation-ready portfolio screenshots:

1. **Launch the Application:**
   ```cmd
   run.bat
   ```
   Open `http://localhost:8501` in your browser.

2. **Capture Key Screens (Windows Shortcut: `Win + Shift + S` or browser developer tools):**

   - **`dashboard.png`**:
     - Navigate to **"📊 Dashboard"**.
     - Capture full-width viewport displaying KPI metric cards (Total Spending, Daily Burn Rate, Top Category, Anomaly Count), the Monthly Spending Trend bar chart, Category Distribution donut chart, and 7-Day Rolling Average.
     - Save as `screenshots/dashboard.png`.

   - **`upload_preview.png`**:
     - Navigate to **"📥 Upload & Ingest"**.
     - Choose `data/sample_expenses.csv`.
     - Click **"🔍 Preview & Auto-Categorize Ingestion"**.
     - Capture the column selection dropdowns and the preview table showing predicted categories.
     - Save as `screenshots/upload_preview.png`.

   - **`transactions.png`**:
     - Navigate to **"📑 Transactions"**.
     - Set filter to **"Flagged Anomalies Only"** to show anomaly badges (e.g. `High`, `Medium`), outlier scores, and AI diagnostic notes.
     - Save as `screenshots/transactions.png`.

   - **`budget_variance.png`**:
     - Navigate to **"📈 Reports & Budgets"**.
     - Capture the **"Budget vs Actual Variance"** grouped bar chart and the **"Budget Health Table"** showing category utilization progress bars.
     - Save as `screenshots/budget_variance.png`.
