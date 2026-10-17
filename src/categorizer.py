"""
Categorization Engine for Personal Expense Intelligence.
Combines rule-based keyword matching and a genuine Machine Learning text classifier
(TF-IDF + Logistic Regression / SGDClassifier) with cold-start baseline training.
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Optional, Tuple
import joblib
import numpy as np

# Taxonomy of Categories
CATEGORIES = [
    "Groceries",
    "Dining",
    "Rent & Housing",
    "Utilities",
    "Transportation",
    "Entertainment",
    "Shopping",
    "Healthcare",
    "Subscriptions",
    "Education",
    "Travel",
    "Miscellaneous",
]

# Rule-based keyword mapping
RULE_PATTERNS: Dict[str, List[str]] = {
    "Groceries": [
        r"walmart", r"kroger", r"trader joe", r"whole foods", r"safeway",
        r"costco", r"aldi", r"target grocery", r"supermarket", r"grocery",
        r"market basket", r"sprouts", r"heb", r"food lion", r"instacart",
        r"big basket", r"blinkit", r"zepto", r"dmart", r"vegetable", r"fruits"
    ],
    "Dining": [
        r"starbucks", r"mcdonald", r"chipotle", r"subway", r"burger king",
        r"domino", r"pizza", r"restaurant", r"cafe", r"diner", r"taco bell",
        r"wendy", r"panera", r"dunkin", r"swiggy", r"zomato", r"doordash",
        r"uber eats", r"grubhub", r"kfc", r"bakery", r"bistro", r"bar & grill",
        r"coffee"
    ],
    "Rent & Housing": [
        r"rent", r"landlord", r"mortgage", r"property management",
        r"hoa fee", r"apartment", r"lease", r"housing", r"condo fee"
    ],
    "Utilities": [
        r"electric", r"water bill", r"power company", r"gas & electric",
        r"pge", r"conedison", r"national grid", r"internet", r"wifi",
        r"broadband", r"comcast", r"xfinity", r"verizon fios", r"spectrum",
        r"sewer", r"trash", r"utility"
    ],
    "Transportation": [
        r"uber", r"lyft", r"gas station", r"shell", r"chevron", r"exxon",
        r"bp", r"mobil", r"parking", r"metro", r"subway ticket", r"bus pass",
        r"transit", r"amtrak", r"toll", r"ezpass", r"fuel", r"petrol", r"ola"
    ],
    "Entertainment": [
        r"cinema", r"movie", r"amc", r"regal", r"concert", r"ticketmaster",
        r"bowling", r"museum", r"zoo", r"golf", r"steam games", r"playstation",
        r"xbox", r"nintendo", r"eventbrite", r"theater", r"stadium"
    ],
    "Shopping": [
        r"amazon", r"ebay", r"best buy", r"apple store", r"ikea", r"zara",
        r"h&m", r"nike", r"adidas", r"clothing", r"shoes", r"department store",
        r"home depot", r"lowe's", r"sephora", r"ulta", r"etsy", r"flipkart",
        r"myntra", r"electronics"
    ],
    "Healthcare": [
        r"pharmacy", r"cvs", r"walgreens", r"hospital", r"clinic", r"doctor",
        r"dental", r"dentist", r"optometry", r"glasses", r"lenscrafters",
        r"health insurance", r"prescription", r"medicine", r"labcorp", r"quest diagnostics"
    ],
    "Subscriptions": [
        r"netflix", r"spotify", r"hulu", r"disney", r"apple music",
        r"youtube premium", r"amazon prime", r"hbo", r"patreon", r"audible",
        r"chatgpt", r"github copilot", r"medium", r"nytimes", r"gym membership"
    ],
    "Education": [
        r"tuition", r"coursera", r"udemy", r"books", r"textbook", r"university",
        r"college", r"campus store", r"edx", r"chegg", r"datacamp", r"duolingo"
    ],
    "Travel": [
        r"airline", r"delta", r"united airlines", r"american airlines",
        r"southwest", r"hotel", r"airbnb", r"booking\.com", r"expedia",
        r"hilton", r"marriott", r"car rental", r"hertz", r"enterprise rent-a-car",
        r"flight"
    ],
}

# Baseline labeled seed dataset to guarantee reproducible ML training out-of-the-box
BASELINE_SEED_DATA: List[Tuple[str, str]] = [
    # Groceries
    ("Walmart Supercenter grocery items", "Groceries"),
    ("Trader Joe's organic vegetables and bread", "Groceries"),
    ("Kroger supermarket food purchase", "Groceries"),
    ("Whole Foods fresh produce market", "Groceries"),
    ("Safeway bakery and dairy", "Groceries"),
    ("Costco wholesale bulk groceries", "Groceries"),
    ("Aldi budget grocery shopping", "Groceries"),
    ("Blinkit 10-minute grocery delivery", "Groceries"),
    ("Zepto fresh milk and eggs", "Groceries"),
    ("Local farmer market fruit stall", "Groceries"),
    # Dining
    ("Starbucks iced latte and croissant", "Dining"),
    ("Chipotle Mexican grill bowl", "Dining"),
    ("McDonalds drive-thru combo meal", "Dining"),
    ("Subway footlong sandwich lunch", "Dining"),
    ("Domino's pizza delivery dinner", "Dining"),
    ("Zomato restaurant food order", "Dining"),
    ("Swiggy biryani express lunch", "Dining"),
    ("Uber Eats late night noodles", "Dining"),
    ("Local Italian trattoria dinner", "Dining"),
    ("Downtown espresso bar coffee", "Dining"),
    # Rent & Housing
    ("Monthly apartment lease payment to landlord", "Rent & Housing"),
    ("Residential rent transfer property management", "Rent & Housing"),
    ("Mortgage payment loan servicing bank", "Rent & Housing"),
    ("HOA monthly condominium community fee", "Rent & Housing"),
    # Utilities
    ("City electric and power utility bill", "Utilities"),
    ("Water sewer and waste drainage utility", "Utilities"),
    ("Xfinity high speed broadband internet", "Utilities"),
    ("ConEdison residential gas heating", "Utilities"),
    ("Verizon home fiber optic monthly bill", "Utilities"),
    # Transportation
    ("Uber trip ride from downtown office", "Transportation"),
    ("Lyft airport ride shared transit", "Transportation"),
    ("Shell gas station petrol fuel refill", "Transportation"),
    ("Chevron highway fuel service", "Transportation"),
    ("Metro transit card monthly pass refill", "Transportation"),
    ("City parking garage meter payment", "Transportation"),
    ("Highway tollway express EZPass toll", "Transportation"),
    # Entertainment
    ("AMC cinema movie tickets popcorn IMAX", "Entertainment"),
    ("Ticketmaster concert live band tickets", "Entertainment"),
    ("Steam summer sale PC video games", "Entertainment"),
    ("PlayStation network digital game store", "Entertainment"),
    ("City museum and art gallery entry ticket", "Entertainment"),
    ("Bowling alley and arcade game tokens", "Entertainment"),
    # Shopping
    ("Amazon marketplace electronics order", "Shopping"),
    ("Nike online official sneakers shoes", "Shopping"),
    ("Zara clothing retail shopping jacket", "Shopping"),
    ("Best Buy computer accessories and cables", "Shopping"),
    ("IKEA furniture home decor bedroom desk", "Shopping"),
    ("Target department store clothing and supplies", "Shopping"),
    ("Apple store replacement charging cable", "Shopping"),
    # Healthcare
    ("CVS pharmacy prescription antibiotics", "Healthcare"),
    ("Walgreens over-the-counter medicine pills", "Healthcare"),
    ("City health clinic doctor consultation co-pay", "Healthcare"),
    ("Dental care clinic routine teeth cleaning", "Healthcare"),
    ("Quest Diagnostics blood test lab work", "Healthcare"),
    # Subscriptions
    ("Netflix 4K streaming family plan subscription", "Subscriptions"),
    ("Spotify premium individual audio stream", "Subscriptions"),
    ("YouTube premium ad-free video subscription", "Subscriptions"),
    ("Apple iCloud storage monthly cloud backup", "Subscriptions"),
    ("ChatGPT Plus OpenAI monthly recurring fee", "Subscriptions"),
    ("Gym fitness center monthly membership dues", "Subscriptions"),
    # Education
    ("Coursera online certificate course specialization", "Education"),
    ("Udemy data science and python bootcamp", "Education"),
    ("University campus bookstore textbook purchase", "Education"),
    ("DataCamp annual learning platform subscription", "Education"),
    # Travel
    ("United Airlines roundtrip flight booking", "Travel"),
    ("Airbnb vacation rental weekend beach cottage", "Travel"),
    ("Marriott international hotel room booking", "Travel"),
    ("Delta Airlines domestic flight ticket", "Travel"),
    ("Enterprise car rental 3-day reservation", "Travel"),
]

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "expense_classifier.joblib")


class HybridExpenseCategorizer:
    """
    Hybrid categorizer that prioritizes high-confidence ML predictions
    and uses compiled regex taxonomy as an exact fallback.
    """

    def __init__(self, model_file: str = MODEL_PATH):
        self.model_file = model_file
        self.pipeline = None
        self._compiled_rules: Dict[str, List[re.Pattern]] = {
            cat: [re.compile(p, re.IGNORECASE) for p in patterns]
            for cat, patterns in RULE_PATTERNS.items()
        }
        self.load_or_train_baseline()

    def load_or_train_baseline(self) -> None:
        """Load trained model if present, otherwise train on baseline seed data."""
        if os.path.exists(self.model_file):
            try:
                self.pipeline = joblib.load(self.model_file)
                return
            except Exception:
                pass

        # If model doesn't exist or failed to load, train baseline
        self.train_baseline()

    def train_baseline(self, additional_samples: Optional[List[Tuple[str, str]]] = None) -> None:
        """Train a Scikit-Learn TF-IDF + LogisticRegression / SGD model on baseline data."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline

        samples = list(BASELINE_SEED_DATA)
        if additional_samples:
            samples.extend(additional_samples)

        texts = [s[0] for s in samples]
        labels = [s[1] for s in samples]

        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
            ("clf", LogisticRegression(max_iter=1000, random_state=42, C=10.0)),
        ])

        pipeline.fit(texts, labels)
        self.pipeline = pipeline

        # Save to disk
        try:
            os.makedirs(os.path.dirname(self.model_file), exist_ok=True)
            joblib.dump(pipeline, self.model_file)
        except Exception:
            pass

    def match_rules(self, description: str) -> Optional[str]:
        """Apply rule-based regex patterns against the transaction description."""
        cleaned = description.strip()
        for cat, patterns in self._compiled_rules.items():
            for pat in patterns:
                if pat.search(cleaned):
                    return cat
        return None

    def predict(self, description: str, confidence_threshold: float = 0.35) -> Tuple[str, str, float]:
        """
        Classify a transaction description.
        Returns: (predicted_category, method_used, confidence)
        method_used is 'ml' or 'rule' or 'fallback'.
        """
        if not description or not description.strip():
            return "Miscellaneous", "fallback", 1.0

        # Try ML prediction first if pipeline is trained
        if self.pipeline is not None:
            try:
                probs = self.pipeline.predict_proba([description])[0]
                classes = self.pipeline.classes_
                top_idx = int(np.argmax(probs))
                confidence = float(probs[top_idx])
                top_class = str(classes[top_idx])

                if confidence >= confidence_threshold:
                    return top_class, "ml", round(confidence, 3)
            except Exception:
                pass

        # Fallback to rule matching
        rule_cat = self.match_rules(description)
        if rule_cat:
            return rule_cat, "rule", 0.90

        return "Miscellaneous", "fallback", 0.0

    def categorize_dataframe(self, df, description_col: str = "description") -> List[str]:
        """Categorize an entire DataFrame column of descriptions."""
        if description_col not in df.columns:
            return ["Miscellaneous"] * len(df)

        results = []
        for desc in df[description_col].fillna(""):
            cat, _, _ = self.predict(str(desc))
            results.append(cat)
        return results


# Module-level singleton instance for convenience
_default_categorizer: Optional[HybridExpenseCategorizer] = None


def get_categorizer() -> HybridExpenseCategorizer:
    global _default_categorizer
    if _default_categorizer is None:
        _default_categorizer = HybridExpenseCategorizer()
    return _default_categorizer


def categorize_transaction(description: str) -> str:
    """Helper function to classify a single transaction description."""
    cat, _, _ = get_categorizer().predict(description)
    return cat
