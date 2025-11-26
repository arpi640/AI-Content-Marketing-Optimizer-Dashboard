# app/metrics_engine/metrics_hub2.py

import pandas as pd
import os

# Path to your training dataset
DATA_PATH = "data/historical_metrics3_1500.csv"


def get_ml_training_data():
    """
    Loads historical_metrics3.csv and validates required columns.
    Returns dataframe used for ML model training.
    """

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"CSV not found at: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    # Required columns for ML training
    required_cols = [
        "ctr",
        "sentiment",
        "polarity",
        "conversions",
        "trend_score"
    ]

    # Check missing columns
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}")

    return df
