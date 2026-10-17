# Data Assets & Schema Reference

This directory contains benchmark and demonstration datasets for the **Personal Expense Intelligence & Spending Analyzer**.

---

## 1. Dataset Overview

### `sample_expenses.csv`
- **Rows:** 140 records
- **Time Span:** ~4 months leading up to today
- **Origin:** Synthetic anonymized transaction generator (`scripts/generate_sample_data.py`)
- **License:** Open Source / Public Domain (CC0)
- **Description:** Realistic personal expense ledger simulating typical household cash flows, including recurring fixed expenses (rent, utilities, subscriptions), daily variable expenses (groceries, dining, transportation, shopping), and atypical spending spikes for testing the AI anomaly detection engine.

---

## 2. Schema Specification

| Column Name | Type | Nullable | Description / Examples |
|-------------|------|----------|------------------------|
| `date` | String (ISO 8601 `YYYY-MM-DD`) | No | Transaction transaction date, e.g. `2026-09-15` |
| `description` | String | No | Merchant name or description, e.g. `Trader Joe's`, `Uber Ride Downtown` |
| `category` | String | Yes | Expense classification tag, e.g. `Groceries`, `Dining`, `Utilities` |
| `amount` | Float | No | Total transaction cost in USD, e.g. `45.50` |
| `payment_method` | String | Yes | Instrument used: `Card`, `Cash`, `UPI`, `Bank Transfer` |
| `notes` | String | Yes | Optional memo or breakdown notes |

---

## 3. Included Expense Categories

1. **Groceries**: Supermarkets, grocery stores, food marts.
2. **Dining**: Cafes, restaurants, food delivery apps (Zomato, Swiggy, Uber Eats).
3. **Rent & Housing**: Monthly apartment rent, mortgage, maintenance fees.
4. **Utilities**: Electric, water, gas, home fiber internet.
5. **Transportation**: Fuel, public transit passes, Uber/rideshares, parking.
6. **Entertainment**: Movies, gaming platforms (Steam, PlayStation), concert tickets.
7. **Shopping**: Electronics, apparel, home goods (Amazon, Target, Nike).
8. **Healthcare**: Pharmacy prescriptions, dental care, clinic consultations.
9. **Subscriptions**: Streaming services (Netflix, Spotify, YouTube), SaaS, gym dues.
10. **Education**: Online courses, textbooks, certifications.
11. **Travel**: Flights, hotels, car rentals.
12. **Miscellaneous**: Unclassified or infrequent outflows.

---

## 4. Benchmark Anomalies

For evaluating the anomaly detection system (`src/anomaly_detector.py`), `sample_expenses.csv` embeds 4 specific high-impact outliers:
- **Emergency Auto Transmission Repair**: $950.00 (`Transportation`)
- **Apple MacBook Pro M3 Repair Lab**: $780.00 (`Shopping`)
- **Specialty ER Medical Co-insurance**: $850.00 (`Healthcare`)
- **Luxury Fine Dining Gala Celebration**: $420.00 (`Dining`)

---

## 5. Generating Fresh Datasets

To regenerate this dataset with a new seed or different time horizon:
```powershell
python scripts/generate_sample_data.py
```
