"""
Training Script for Machine Learning Expense Categorizer.
Trains a TF-IDF + Logistic Regression classification pipeline on merchant descriptions.
Evaluates accuracy, macro F1, and per-class performance before saving model weights.
"""

from __future__ import annotations

import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.categorizer import BASELINE_SEED_DATA, MODEL_PATH, MODEL_DIR


def get_training_data() -> Tuple[List[str], List[str]]:
    """Aggregate training samples from baseline seeds and sample expenses CSV if present."""
    texts = [s[0] for s in BASELINE_SEED_DATA]
    labels = [s[1] for s in BASELINE_SEED_DATA]

    sample_csv = os.path.join(PROJECT_ROOT, "data", "sample_expenses.csv")
    if os.path.exists(sample_csv):
        df = pd.read_csv(sample_csv)
        if "description" in df.columns and "category" in df.columns:
            valid = df.dropna(subset=["description", "category"])
            texts.extend(valid["description"].astype(str).tolist())
            labels.extend(valid["category"].astype(str).tolist())

    return texts, labels


def train_and_evaluate():
    print("=" * 60)
    print("ExpenseIQ: Training Machine Learning Categorization Model")
    print("=" * 60)

    X_raw, y_raw = get_training_data()
    print(f"Total training instances collected: {len(X_raw)}")

    # Stratified Train/Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X_raw, y_raw, test_size=0.20, random_state=42, stratify=y_raw
    )
    print(f"Training split: {len(X_train)} | Test split: {len(X_test)}")

    # Build Pipeline
    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=1,
                token_pattern=r"(?u)\b\w+\b",
            ),
        ),
        (
            "clf",
            LogisticRegression(
                max_iter=1000,
                C=10.0,
                random_state=42,
                class_weight="balanced",
            ),
        ),
    ])

    print("Fitting model...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

    print("\n--- Model Evaluation Results ---")
    print(f"Overall Accuracy:  {acc * 100:.2f}%")
    print(f"Macro F1-Score:    {f1:.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    # Save artifact
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nModel artifact successfully saved to:\n  {MODEL_PATH}")
    print("=" * 60)

    return acc, f1


if __name__ == "__main__":
    train_and_evaluate()
