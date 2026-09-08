"""
Preprocessing pipeline for K-Means Customer Segmentation.

This module prepares customer-level behavioral features for
K-Means clustering by:

1. Loading customer-level features.
2. Selecting clustering features.
3. Applying log1p transformation to reduce skewness.
4. Standardizing features using StandardScaler.
5. Saving the transformed features.
6. Saving the fitted scaler for reproducibility.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CUSTOMER_FEATURES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_features.csv"
)

PROCESSED_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

TRANSFORMED_DATA_PATH = (
    PROCESSED_DATA_DIR
    / "customer_features_transformed.csv"
)

SCALER_PATH = (
    PROCESSED_DATA_DIR
    / "customer_feature_scaler.joblib"
)


# ============================================================
# Feature Configuration
# ============================================================

ID_COLUMN = "CustomerID"

FEATURE_COLUMNS = [
    "Recency",
    "Frequency",
    "Monetary",
    "TotalQuantity",
    "AverageOrderValue",
    "UniqueProducts",
]


# ============================================================
# Data Loading
# ============================================================

def load_customer_features() -> pd.DataFrame:
    """
    Load the customer-level feature dataset.
    """

    if not CUSTOMER_FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Customer feature dataset not found at: "
            f"{CUSTOMER_FEATURES_PATH}"
        )

    df = pd.read_csv(
        CUSTOMER_FEATURES_PATH
    )

    return df


# ============================================================
# Input Validation
# ============================================================

def validate_input_data(
    df: pd.DataFrame
) -> None:
    """
    Validate the customer-level feature dataset.
    """

    required_columns = [
        ID_COLUMN,
        *FEATURE_COLUMNS,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required columns are missing: "
            f"{missing_columns}"
        )

    if df[FEATURE_COLUMNS].isnull().any().any():
        raise ValueError(
            "Clustering features contain missing values."
        )

    if (
        df[FEATURE_COLUMNS] < 0
    ).any().any():
        raise ValueError(
            "Clustering features contain negative values. "
            "The log1p transformation requires values >= 0."
        )


# ============================================================
# Log Transformation
# ============================================================

def apply_log_transformation(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Apply log1p transformation to clustering features.

    log1p(x) = log(1 + x)

    This reduces the influence of extreme values and
    decreases positive skewness.
    """

    transformed_df = df.copy()

    transformed_df[FEATURE_COLUMNS] = np.log1p(
        transformed_df[FEATURE_COLUMNS]
    )

    return transformed_df


# ============================================================
# Standardization
# ============================================================

def apply_standard_scaling(
    df: pd.DataFrame
):
    """
    Standardize the clustering features using StandardScaler.

    Returns
    -------
    transformed_df : pd.DataFrame
        Standardized customer features.

    scaler : StandardScaler
        Fitted scaler object.
    """

    scaler = StandardScaler()

    scaled_values = scaler.fit_transform(
        df[FEATURE_COLUMNS]
    )

    transformed_df = df.copy()

    transformed_df[FEATURE_COLUMNS] = (
        scaled_values
    )

    return transformed_df, scaler


# ============================================================
# Validation of Transformed Data
# ============================================================

def validate_transformed_data(
    df: pd.DataFrame
) -> None:
    """
    Validate the standardized feature dataset.
    """

    means = (
        df[FEATURE_COLUMNS]
        .mean()
    )

    standard_deviations = (
        df[FEATURE_COLUMNS]
        .std()
    )

    print("\n" + "=" * 60)
    print("TRANSFORMED FEATURE VALIDATION")
    print("=" * 60)

    print("\nFeature means:")

    print(
        means.round(4)
    )

    print("\nFeature standard deviations:")

    print(
        standard_deviations.round(4)
    )

    print("\nMissing values:")

    print(
        df[FEATURE_COLUMNS]
        .isnull()
        .sum()
    )


# ============================================================
# Save Processed Data
# ============================================================

def save_processed_data(
    df: pd.DataFrame,
    scaler: StandardScaler
) -> None:
    """
    Save transformed customer features and fitted scaler.
    """

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save transformed customer features
    df.to_csv(
        TRANSFORMED_DATA_PATH,
        index=False
    )

    # Save fitted scaler
    joblib.dump(
        scaler,
        SCALER_PATH
    )

    print("\n" + "=" * 60)
    print("PREPROCESSED DATA SAVED")
    print("=" * 60)

    print(
        f"Transformed data : "
        f"{TRANSFORMED_DATA_PATH}"
    )

    print(
        f"Scaler           : "
        f"{SCALER_PATH}"
    )


# ============================================================
# Main Execution
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("K-MEANS CUSTOMER SEGMENTATION")
    print("FEATURE PREPROCESSING")
    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    df = load_customer_features()

    print(
        f"\nCustomer dataset loaded: "
        f"{len(df):,} customers"
    )

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    validate_input_data(df)

    print(
        "Input validation: PASSED"
    )

    print("\nClustering features:")

    for feature in FEATURE_COLUMNS:
        print(f"- {feature}")

    print(
        "\nCustomerID will be retained as an identifier "
        "but excluded from clustering."
    )

    # --------------------------------------------------------
    # Apply log transformation
    # --------------------------------------------------------

    log_df = apply_log_transformation(df)

    print(
        "\nLog1p transformation: APPLIED"
    )

    # --------------------------------------------------------
    # Apply standard scaling
    # --------------------------------------------------------

    transformed_df, scaler = (
        apply_standard_scaling(log_df)
    )

    print(
        "StandardScaler: APPLIED"
    )

    # --------------------------------------------------------
    # Validate transformed data
    # --------------------------------------------------------

    validate_transformed_data(
        transformed_df
    )

    # --------------------------------------------------------
    # Save processed data
    # --------------------------------------------------------

    save_processed_data(
        transformed_df,
        scaler
    )

    # --------------------------------------------------------
    # Completion
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)