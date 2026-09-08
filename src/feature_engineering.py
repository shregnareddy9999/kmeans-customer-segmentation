"""
Customer-level feature engineering for K-Means Customer Segmentation.

This module transforms cleaned transaction-level retail data into
customer-level behavioral features suitable for clustering.

The generated features include:
- Recency
- Frequency
- Monetary
- TotalQuantity
- AverageOrderValue
- UniqueProducts
"""

from pathlib import Path

import pandas as pd


# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_online_retail.csv"
)

SAMPLES_DIR = (
    PROJECT_ROOT
    / "data"
    / "samples"
)

CUSTOMER_FEATURES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_features.csv"
)

SAMPLE_PATH = (
    SAMPLES_DIR
    / "customer_features_sample.csv"
)


# ============================================================
# Data Loading
# ============================================================

def load_cleaned_data() -> pd.DataFrame:
    """
    Load the cleaned transaction dataset.

    InvoiceDate is explicitly converted using the known
    DD-MM-YYYY HH:MM format.
    """

    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at: "
            f"{PROCESSED_DATA_PATH}"
        )

    df = pd.read_csv(
        PROCESSED_DATA_PATH
    )

    # The Online Retail dataset stores dates as:
    # DD-MM-YYYY HH:MM
    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        format="%d-%m-%Y %H:%M",
        errors="coerce"
    )

    return df


# ============================================================
# Data Validation
# ============================================================

def validate_input_data(df: pd.DataFrame) -> None:
    """
    Validate the cleaned transaction dataset before
    feature engineering.
    """

    required_columns = [
        "InvoiceNo",
        "StockCode",
        "InvoiceDate",
        "Quantity",
        "UnitPrice",
        "CustomerID",
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

    if not pd.api.types.is_datetime64_any_dtype(
        df["InvoiceDate"]
    ):
        raise TypeError(
            "InvoiceDate must be a datetime column."
        )

    if df["CustomerID"].isnull().any():
        raise ValueError(
            "CustomerID contains missing values."
        )

    if df["InvoiceDate"].isnull().any():
        raise ValueError(
            "InvoiceDate contains invalid or missing dates."
        )

    if df["Quantity"].isnull().any():
        raise ValueError(
            "Quantity contains missing values."
        )

    if df["UnitPrice"].isnull().any():
        raise ValueError(
            "UnitPrice contains missing values."
        )


# ============================================================
# Monetary Value
# ============================================================

def calculate_monetary_value(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate the monetary value of each transaction.

    Formula:

        TotalAmount = Quantity × UnitPrice
    """

    df = df.copy()

    df["TotalAmount"] = (
        df["Quantity"] * df["UnitPrice"]
    )

    return df


# ============================================================
# Customer Feature Engineering
# ============================================================

def create_customer_features(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Create customer-level behavioral features.

    Features:
    - Recency
    - Frequency
    - Monetary
    - TotalQuantity
    - AverageOrderValue
    - UniqueProducts

    CustomerID is retained only as an identifier and must not
    be used as a clustering feature.
    """

    df = calculate_monetary_value(df)

    # --------------------------------------------------------
    # Reference date for Recency
    # --------------------------------------------------------

    reference_date = (
        df["InvoiceDate"].max()
        + pd.Timedelta(days=1)
    )

    # --------------------------------------------------------
    # Customer-level aggregation
    # --------------------------------------------------------

    customer_features = (
        df.groupby("CustomerID")
        .agg(
            Recency=(
                "InvoiceDate",
                lambda x: (
                    reference_date - x.max()
                ).days
            ),
            Frequency=(
                "InvoiceNo",
                "nunique"
            ),
            Monetary=(
                "TotalAmount",
                "sum"
            ),
            TotalQuantity=(
                "Quantity",
                "sum"
            ),
            AverageOrderValue=(
                "TotalAmount",
                lambda x: (
                    x.sum()
                    / df.loc[
                        x.index,
                        "InvoiceNo"
                    ].nunique()
                )
            ),
            UniqueProducts=(
                "StockCode",
                "nunique"
            ),
        )
        .reset_index()
    )

    return customer_features


# ============================================================
# Feature Validation
# ============================================================

def validate_features(
    customer_features: pd.DataFrame
) -> None:
    """
    Validate the generated customer-level features.
    """

    print("\n" + "=" * 60)
    print("CUSTOMER FEATURE VALIDATION")
    print("=" * 60)

    print(
        f"Number of customers : "
        f"{len(customer_features):,}"
    )

    print(
        f"Number of columns   : "
        f"{customer_features.shape[1]}"
    )

    print("\nColumns:")

    for column in customer_features.columns:
        print(f"- {column}")

    print("\nMissing values:")

    print(
        customer_features.isnull().sum()
    )

    print("\nDuplicate customers:")

    duplicate_customers = (
        customer_features["CustomerID"]
        .duplicated()
        .sum()
    )

    print(duplicate_customers)

    print("\nFeature summary:")

    print(
        customer_features.describe()
    )


# ============================================================
# Save Features
# ============================================================

def save_customer_features(
    customer_features: pd.DataFrame
) -> None:
    """
    Save customer-level features and a sample dataset.
    """

    CUSTOMER_FEATURES_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    SAMPLES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save complete customer feature dataset
    # --------------------------------------------------------

    customer_features.to_csv(
        CUSTOMER_FEATURES_PATH,
        index=False
    )

    # --------------------------------------------------------
    # Save sample dataset
    # --------------------------------------------------------

    customer_features.head(20).to_csv(
        SAMPLE_PATH,
        index=False
    )

    print("\n" + "=" * 60)
    print("CUSTOMER FEATURES SAVED")
    print("=" * 60)

    print(
        f"Full dataset : "
        f"{CUSTOMER_FEATURES_PATH}"
    )

    print(
        f"Sample       : "
        f"{SAMPLE_PATH}"
    )


# ============================================================
# Main Execution
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("K-MEANS CUSTOMER SEGMENTATION")
    print("CUSTOMER FEATURE ENGINEERING")
    print("=" * 60)

    # --------------------------------------------------------
    # Load cleaned transaction data
    # --------------------------------------------------------

    df = load_cleaned_data()

    print(
        f"\nCleaned transactions loaded: "
        f"{len(df):,}"
    )

    # --------------------------------------------------------
    # Validate input data
    # --------------------------------------------------------

    validate_input_data(df)

    print(
        "\nInput data validation: PASSED"
    )

    # --------------------------------------------------------
    # Create customer-level features
    # --------------------------------------------------------

    customer_features = create_customer_features(df)

    # --------------------------------------------------------
    # Validate generated features
    # --------------------------------------------------------

    validate_features(customer_features)

    # --------------------------------------------------------
    # Save customer-level features
    # --------------------------------------------------------

    save_customer_features(customer_features)

    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 60)