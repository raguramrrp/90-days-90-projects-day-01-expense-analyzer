# Quickstart Guide: Personal Expense Intelligence

Get Personal Expense Intelligence & Spending Analyzer (**ExpenseIQ**) running on your local Windows machine in less than 2 minutes.

---

## Method 1: One-Click Automated Setup (Recommended)

1. **Clone or Download** this repository:
   ```cmd
   git clone https://github.com/raguramrrp/90-days-90-projects-day-01-expense-analyzer.git
   cd 90-days-90-projects-day-01-expense-analyzer
   ```

2. **Run Automated Setup:**
   Double-click `setup.bat` (or run in Command Prompt):
   ```cmd
   setup.bat
   ```
   *This automatically detects Python 3.12/3.11, creates `.venv`, installs all pinned dependencies, initializes the SQLite database schema, generates sample data, and trains the baseline ML model.*

3. **Launch the Application:**
   Double-click `run.bat` (or run in Command Prompt):
   ```cmd
   run.bat
   ```
   *Your browser will automatically open to `http://localhost:8501`.*

4. **Run the Test Suite:**
   Double-click `test.bat`:
   ```cmd
   test.bat
   ```

---

## Method 2: Manual Setup (Terminal / PowerShell)

If you prefer full control via command line:

```powershell
# 1. Navigate to the project root
cd "d:\90 days\90-days-90-projects-day-01-expense-analyzer"

# 2. Create Python virtual environment (Python 3.10, 3.11, or 3.12)
py -3.12 -m venv .venv

# 3. Activate virtual environment
.\.venv\Scripts\Activate.ps1
# (Or in standard Command Prompt: .venv\Scripts\activate.bat)

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize configuration
copy .env.example .env

# 6. Initialize database and generate sample data
python -c "from src.database import init_db; init_db()"
python scripts/generate_sample_data.py

# 7. Train Machine Learning classifier
python scripts/train_classifier.py

# 8. Run unit and integration tests
pytest -v

# 9. Launch Streamlit application
streamlit run src/app.py
```

---

## 3. Instant Verification Checklist

- [ ] Web dashboard opens at `http://localhost:8501`.
- [ ] Sidebar displays **"Total Records: 140"** and total spend metrics.
- [ ] Monthly trends and Category donut charts render interactively.
- [ ] **"📑 Transactions"** page displays table with green and red anomaly tags.
- [ ] Filter search works instantaneously when typing `Uber` or `Whole Foods`.
- [ ] Data exports to CSV and JSON function with one click.
