# Development Notes: Engineering Decisions & Trade-offs

This document details the architectural rationale, engineering trade-offs, and design choices made during the implementation of the Personal Expense Intelligence platform.

---

## 1. Architectural Philosophy: Local-First & Lightweight

### Decision: SQLite instead of PostgreSQL
- **Rationale:** For personal expense tracking, user data privacy is paramount. Many users abandon finance tools that require uploading bank credentials or hosting sensitive financial records on third-party cloud databases.
- **Trade-off:** SQLite lacks native client-server concurrent connection scaling; however, for single-user analytical queries ($< 1,000,000$ rows), SQLite is substantially faster than client-server relational databases due to zero network latency and in-process execution.
- **Implementation:** Enabled `check_same_thread=False` and connection row-factories to ensure seamless interaction with Streamlit's multi-threaded execution model. Added indices on `date` and `category` to guarantee $< 5\text{ms}$ query response times.

---

## 2. Categorization Engine: Hybrid Architecture

### Problem
Relying strictly on hard-coded regex rules causes brittle failures when encountering unseen merchants (e.g. `Boba Bliss Cafe`, `Zepto Mart`, `Apex Fitness Lab`). Conversely, relying purely on Machine Learning without seed data causes cold-start failures when an app is first initialized on a fresh system.

### Decision: Dual-Layer Fallback (TF-IDF + Logistic Regression + Regex)
1. **Layer 1 (ML Inference):** A `TfidfVectorizer` paired with a calibrated `LogisticRegression` pipeline processes the description. Sublinear term frequencies damp down repeated noisy tokens, while character and word n-grams (1, 2) capture merchant stems. If model confidence exceeds 35%, the ML label is accepted.
2. **Layer 2 (Rule-Based Regex Taxonomy):** If the description falls below the ML confidence threshold or the model is uninitialized, over 100 domain-specific regular expressions execute.
3. **Layer 3 (Fallback):** Inconclusive descriptions default to `Miscellaneous` rather than halting or throwing exceptions.

---

## 3. Anomaly Detection: Blending Statistics and Machine Learning

### Decision: Per-Category Z-Scores + Isolation Forest
- **Why not global Z-Score?** A \$1,200 charge in "Rent & Housing" is completely normal, but a \$1,200 charge in "Dining" or "Groceries" is an extreme outlier. Global thresholds fail because spending distributions across categories have wildly different scales and variances.
- **Why Isolation Forest?** While Z-scores detect scalar magnitude outliers, they miss multivariate temporal anomalies (e.g., unusual frequency of purchases on specific days or unusual spending cluster shifts). Isolation Forest constructs an ensemble of isolation trees to isolate anomalies in multi-dimensional feature space (`amount`, `day_of_month`, `day_of_week`, `category_freq`, `ratio_to_mean`).

---

## 4. Resilient CSV Ingestion

### Problem
Bank CSV statements vary wildly across financial institutions (Chase, Bank of America, Wells Fargo, Revolut, HDFC, ICICI). Column names differ (`Transaction Date` vs `Date` vs `Posted Date`; `Memo` vs `Merchant` vs `Description`).

### Solution
- Implemented heuristic fuzzy column detection (`guess_col()`) matching common stems (`date`, `time`, `merchant`, `desc`, `cost`, `amount`).
- Regex cleaning for monetary strings strips currency signs (`$`, `€`, `₹`, `,`).
- Interactive pre-commit preview allows users to verify predicted categories before anything is committed to the database.

---

## 5. Security & Privacy Considerations
- Zero external network requests during categorization or analytics.
- No API keys or paid external subscriptions required.
- SQLite database file (`expenses.db`) is strictly excluded from version control via `.gitignore`.
