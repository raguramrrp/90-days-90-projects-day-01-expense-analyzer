"""
Reproducible Synthetic Expense Data Generator.
Creates realistic transaction logs with categories, payment methods,
cyclical spending patterns, and distinct anomalies for demonstration.
"""

import csv
import random
from datetime import date, timedelta

CATEGORIZED_MERCHANTS = {
    "Groceries": [
        ("Walmart Supercenter", 45.0, 160.0),
        ("Trader Joe's", 30.0, 95.0),
        ("Kroger Market", 25.0, 110.0),
        ("Whole Foods Market", 60.0, 210.0),
        ("Aldi Grocery", 20.0, 75.0),
        ("Costco Wholesale", 120.0, 320.0),
    ],
    "Dining": [
        ("Starbucks Coffee", 4.5, 12.0),
        ("Chipotle Mexican Grill", 12.0, 24.0),
        ("Subway Sandwiches", 8.0, 16.0),
        ("Domino's Pizza Delivery", 18.0, 42.0),
        ("Panera Bread Cafe", 11.0, 26.0),
        ("Local Bistro & Bar", 45.0, 110.0),
    ],
    "Rent & Housing": [
        ("Avalon Bay Apartment Rent", 1250.0, 1250.0),
    ],
    "Utilities": [
        ("City Electric & Power", 75.0, 140.0),
        ("Municipal Water & Sewer", 35.0, 65.0),
        ("Xfinity Broadband Internet", 70.0, 70.0),
    ],
    "Transportation": [
        ("Shell Gas Station Fuel", 35.0, 65.0),
        ("Chevron Fuel Station", 30.0, 60.0),
        ("Uber Ride Downtown", 14.0, 38.0),
        ("Metro Transit Monthly Pass", 45.0, 90.0),
    ],
    "Entertainment": [
        ("AMC Theatres Cinema", 16.0, 35.0),
        ("Steam Game Purchase", 15.0, 60.0),
        ("Live Concert Ticketmaster", 65.0, 150.0),
        ("City Bowl Arcade", 20.0, 45.0),
    ],
    "Shopping": [
        ("Amazon.com Marketplace", 18.0, 130.0),
        ("Target Department Store", 25.0, 85.0),
        ("Best Buy Tech Accessories", 35.0, 160.0),
        ("Nike Official Store", 60.0, 140.0),
        ("IKEA Furniture & Decor", 45.0, 180.0),
    ],
    "Healthcare": [
        ("CVS Pharmacy Rx", 12.0, 45.0),
        ("Walgreens Health & Meds", 15.0, 50.0),
        ("Dental Clinic Consultation Co-pay", 40.0, 75.0),
    ],
    "Subscriptions": [
        ("Netflix Premium Streaming", 19.99, 19.99),
        ("Spotify Premium Music", 10.99, 10.99),
        ("YouTube Premium Family", 22.99, 22.99),
        ("ChatGPT Plus OpenAI", 20.00, 20.00),
        ("Planet Fitness Gym Membership", 25.00, 25.00),
    ],
}

# Deliberate outliers for testing anomaly detection
ANOMALIES = [
    ("Emergency Auto Transmission Repair", "Transportation", 950.00, "Card", "Unexpected breakdown on interstate"),
    ("Apple MacBook Pro M3 Repair Lab", "Shopping", 780.00, "Card", "Screen crack replacement"),
    ("Specialty ER Medical Co-insurance", "Healthcare", 850.00, "Bank Transfer", "Urgent care visit"),
    ("Luxury Fine Dining Gala Celebration", "Dining", 420.00, "Card", "Anniversary group dinner party"),
]


def generate_dataset(output_path: str, days_back: int = 120, target_count: int = 140) -> None:
    random.seed(42)
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)

    rows = []

    # 1. Recurring Monthly Bills (Rent, Utilities, Subscriptions)
    current = start_date.replace(day=1)
    while current <= end_date:
        # Rent on 1st of month
        rows.append({
            "date": current.strftime("%Y-%m-%d"),
            "description": "Avalon Bay Apartment Rent",
            "category": "Rent & Housing",
            "amount": 1250.00,
            "payment_method": "Bank Transfer",
            "notes": "Monthly residential rent",
        })
        # Utilities on 5th
        u_date = (current + timedelta(days=4)).strftime("%Y-%m-%d")
        rows.append({
            "date": u_date,
            "description": "City Electric & Power",
            "category": "Utilities",
            "amount": round(random.uniform(80.0, 135.0), 2),
            "payment_method": "Bank Transfer",
            "notes": "Power utility bill",
        })
        rows.append({
            "date": u_date,
            "description": "Xfinity Broadband Internet",
            "category": "Utilities",
            "amount": 70.00,
            "payment_method": "Card",
            "notes": "Fiber gigabit plan",
        })
        # Subscriptions on 15th
        s_date = (current + timedelta(days=14)).strftime("%Y-%m-%d")
        for sub_name, min_p, _ in CATEGORIZED_MERCHANTS["Subscriptions"]:
            rows.append({
                "date": s_date,
                "description": sub_name,
                "category": "Subscriptions",
                "amount": min_p,
                "payment_method": "Card",
                "notes": "Recurring monthly membership",
            })
        # Increment month
        next_month = current.month + 1 if current.month < 12 else 1
        next_year = current.year if current.month < 12 else current.year + 1
        current = current.replace(year=next_year, month=next_month, day=1)

    # 2. Daily Variable Expenses (Groceries, Dining, Fuel, Shopping)
    categories_pool = ["Groceries", "Dining", "Transportation", "Shopping", "Entertainment", "Healthcare"]
    weights = [0.35, 0.25, 0.18, 0.12, 0.06, 0.04]

    while len(rows) < target_count - len(ANOMALIES):
        random_days = random.randint(0, days_back)
        tx_date = (end_date - timedelta(days=random_days)).strftime("%Y-%m-%d")

        cat = random.choices(categories_pool, weights=weights)[0]
        merchant_tpl = random.choice(CATEGORIZED_MERCHANTS[cat])
        merchant_name = merchant_tpl[0]
        amt = round(random.uniform(merchant_tpl[1], merchant_tpl[2]), 2)
        pm = random.choice(["Card", "Card", "Card", "Cash", "UPI"])

        rows.append({
            "date": tx_date,
            "description": merchant_name,
            "category": cat,
            "amount": amt,
            "payment_method": pm,
            "notes": "",
        })

    # 3. Add explicit Anomalies at spread-out dates
    for idx, anom in enumerate(ANOMALIES):
        anom_date = (end_date - timedelta(days=idx * 28 + 12)).strftime("%Y-%m-%d")
        rows.append({
            "date": anom_date,
            "description": anom[0],
            "category": anom[1],
            "amount": anom[2],
            "payment_method": anom[3],
            "notes": anom[4],
        })

    # Sort chronologically
    rows.sort(key=lambda x: x["date"])

    # Write CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "description", "category", "amount", "payment_method", "notes"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} realistic transactions saved to {output_path}")


if __name__ == "__main__":
    generate_dataset("data/sample_expenses.csv")
