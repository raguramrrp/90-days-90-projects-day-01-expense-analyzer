"""
Unit Tests for Expense Categorizer Module.
Tests rule-based matching, ML model inference, and fallback behavior.
"""

import pandas as pd
import pytest
from src.categorizer import HybridExpenseCategorizer, get_categorizer, CATEGORIES


@pytest.fixture
def categorizer():
    return HybridExpenseCategorizer()


def test_rule_matching_patterns(categorizer):
    # Groceries
    cat, method, conf = categorizer.predict("Walmart Supercenter #1243")
    assert cat == "Groceries"

    # Dining
    cat, method, conf = categorizer.predict("Starbucks store #4812")
    assert cat == "Dining"

    # Utilities
    cat, method, conf = categorizer.predict("Xfinity Broadband Internet bill")
    assert cat == "Utilities"

    # Transportation
    cat, method, conf = categorizer.predict("Shell Oil fuel station")
    assert cat == "Transportation"

    # Subscriptions
    cat, method, conf = categorizer.predict("Netflix.com monthly recurring")
    assert cat == "Subscriptions"

    # Rent
    cat, method, conf = categorizer.predict("Monthly apartment rent check")
    assert cat == "Rent & Housing"


def test_fallback_miscellaneous(categorizer):
    cat, method, conf = categorizer.predict("XYZ9981UNKNOWNTRANSFER")
    assert cat in CATEGORIES


def test_categorize_dataframe(categorizer):
    df = pd.DataFrame({
        "description": [
            "Trader Joe's organic milk",
            "Chipotle lunch bowl",
            "Uber trip downtown",
        ]
    })
    results = categorizer.categorize_dataframe(df)
    assert len(results) == 3
    assert results[0] == "Groceries"
    assert results[1] == "Dining"
    assert results[2] == "Transportation"
