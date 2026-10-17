# Personal Expense Intelligence — User Guide

A step-by-step walkthrough to get the most out of your expense tracking, categorization, and financial intelligence platform.

---

## 1. Quick Launch
Double-click `run.bat` or run:
```powershell
.\.venv\Scripts\streamlit run src/app.py
```
Open your browser at `http://localhost:8501`.

---

## 2. Navigating the Application

The sidebar on the left gives you access to the 4 main modules and instant database controls:

```
├── 📊 Dashboard          (KPIs, Monthly trends, Category breakdown, Burn rate)
├── 📥 Upload & Ingest    (CSV statement importer & manual expense logger)
├── 📑 Transactions       (Ledger table, search, filters, anomaly tags, exports)
└── 📈 Reports & Budgets  (Budget variance, MoM analysis, AI anomaly inspector)
```

### Instant Demo Setup
If you are starting with an empty database:
1. Locate the sidebar.
2. Click the **"🚀 Load Sample Dataset"** button.
3. The system will populate 140 realistic transactions across 4 months with pre-configured categories and realistic spending anomalies.

---

## 3. Ingesting Your Bank Statement (CSV)

1. Navigate to **"📥 Upload & Ingest"** -> **"📂 CSV Statement Upload"**.
2. Drag and drop your bank or credit card `.csv` file.
3. Use the intelligent column selector to confirm your columns:
   - **Date Column:** Choose the date header (e.g. `Date`, `Transaction Date`).
   - **Description Column:** Choose the merchant or memo header (e.g. `Description`, `Merchant`).
   - **Amount Column:** Choose the monetary value column.
   - **Category Column:** Select `(Auto-Detect with AI/Rules)` if your bank statement lacks categories.
4. Click **"🔍 Preview & Auto-Categorize Ingestion"**.
5. Inspect the preview table showing predicted categories.
6. Click **"💾 Confirm & Commit to Database"**.

---

## 4. Logging a Single Expense

1. Navigate to **"📥 Upload & Ingest"** -> **"✍️ Manual Transaction Entry"**.
2. Enter the date, merchant description (e.g. `Trader Joe's`), and amount.
3. Notice that ExpenseIQ dynamically suggests the category based on your input.
4. Select payment method (`Card`, `Cash`, `UPI`, `Bank Transfer`, `Other`).
5. Click **"➕ Save Transaction"**.

---

## 5. Analyzing the Executive Dashboard

The **"📊 Dashboard"** view provides real-time updates:
- **Total Spending & Daily Burn Rate:** Understand your overall burn velocity.
- **Top Expense Category:** Identify where the largest portion of your income goes.
- **Monthly Trend Chart:** Compare spending across months with average transaction line overlays.
- **Category Donut:** Click on categories to isolate percentages.
- **7-Day Rolling Average:** Smooth out erratic daily purchases to see real underlying spending velocity.
- **Top Outflow Merchants:** Identify repeat vendors draining cash.

---

## 6. Inspecting Anomalies & Outliers

In **"📈 Reports & Budgets"** -> **"🚨 AI Anomaly Inspector"**:
- Review transactions flagged as unusual by the combined Z-score and Isolation Forest engine.
- Each anomaly displays:
  - **Severity:** `High`, `Medium`, or `Low`.
  - **Anomaly Score:** 0–100 scale indicating deviation intensity.
  - **AI Diagnostic Note:** Clear explanation (e.g., *"Amount is 4.2x higher than the Groceries average of $64.20"*).

---

## 7. Budget Tracking & Allocation

In **"📈 Reports & Budgets"** -> **"🎯 Budget vs Actual Variance"**:
- Select the target month from the dropdown.
- Check the **Utilization %** progress bar:
  - Green / Normal: Spending is under 85% of budget.
  - Orange / Near Limit: Spending is between 85% and 100%.
  - Red / Over Budget: Spending has exceeded the monthly cap.
- To adjust budget limits, expand **"⚙️ Edit Monthly Category Budgets"**, choose the category, enter the new limit, and click **"💾 Update Budget"**.

---

## 8. Exporting Your Data

In **"📑 Transactions"**:
- Apply any search, category, amount, or anomaly filters.
- Click **"📥 Export Filtered to CSV"** or **"📥 Export to JSON"** to download your structured, cleaned data for external reporting or tax filings.
