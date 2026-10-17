# Troubleshooting Guide

Common issues, root causes, and verified solutions for the Personal Expense Intelligence platform.

---

## 1. Environment & Setup Issues

### Issue: `python` or `py` is not recognized
- **Symptom:** `setup.bat` fails with `"No compatible Python installation found on system PATH"`.
- **Cause:** Python is not added to the Windows system environment PATH during installation.
- **Fix:** 
  1. Re-run the Python installer from [python.org](https://www.python.org/downloads/).
  2. Ensure the checkbox **"Add python.exe to PATH"** is ticked.
  3. Re-open Command Prompt or PowerShell and re-run `setup.bat`.

### Issue: Execution policy restrictions in PowerShell
- **Symptom:** `cannot be loaded because running scripts is disabled on this system`.
- **Cause:** Windows PowerShell default execution policy blocks unsigned ps1 scripts.
- **Fix:** Run the provided batch files (`setup.bat`, `run.bat`, `test.bat`) directly via CMD or run:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```

---

## 2. Ingestion & CSV Issues

### Issue: "Error reading CSV: UnicodeDecodeError"
- **Symptom:** Upload fails when reading bank statements generated from certain spreadsheet editors.
- **Cause:** File was exported in `latin-1` or `utf-16` instead of `utf-8`.
- **Fix:** In Excel, choose **Save As** -> **CSV (Comma delimited) (*.csv)** with UTF-8 encoding.

### Issue: Categorization is marking everything as "Miscellaneous"
- **Symptom:** Ingested bank statements have all rows categorized as "Miscellaneous".
- **Cause:** The bank memo contains cryptic internal wire codes with no recognizable merchant tokens (e.g. `TRF DDB 998240`).
- **Fix:** Run the ML training script with labeled examples to teach the model your bank's specific wire format:
  ```powershell
  .\.venv\Scripts\python scripts/train_classifier.py
  ```

---

## 3. Database & Runtime Issues

### Issue: "database is locked" (SQLite)
- **Symptom:** SQLite operational error during high-frequency writes.
- **Cause:** Multiple concurrent processes attempting uncommitted write transactions simultaneously.
- **Fix:** Close any external SQLite GUI browsers (e.g., DB Browser for SQLite) that have opened `expenses.db` in exclusive lock mode.

### Issue: Streamlit port 8501 is already in use
- **Symptom:** Streamlit selects a higher port (e.g., 8502, 8503).
- **Fix:** Either access the higher port URL shown in the terminal or release port 8501:
  ```powershell
  Stop-Process -Id (Get-NetTCPConnection -LocalPort 8501).OwningProcess -Force
  ```
