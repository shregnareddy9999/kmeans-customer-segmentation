"""
Data preprocessing module for the K-Means Customer Segmentation project.

This module is responsible for:
1. Loading the Online Retail dataset.
2. Inspecting the raw dataset.
3. Cleaning invalid and unusable transactions.
4. Saving the cleaned transaction dataset.

The cleaned transaction data will later be used for
customer-level feature engineering and K-Means clustering.
"""

from pathlib import Path

import pandas as pd


# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Online Retail.xlsx"

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DATA_PATH = (
    PROCESSED_DATA_DIR / "cleaned_online_retail.csv"
)


# ============================================================
# Data Loading
# ============================================================

def load_data() -> pd.DataFrame:
    """
    Load the Online Retail dataset.

    Returns
    -------
    pd.DataFrame
        Raw transaction-level retail dataset.
    """

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {RAW_DATA_PATH}"
        )

    df = pd.read_excel(RAW_DATA_PATH)

    return df


# ============================================================
# Data Inspection
# ============================================================

def inspect_data(df: pd.DataFrame) -> None:
    """
    Display basic information about the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset to inspect.
    """

    print("\n" + "=" * 60)
    print("DATASET INFORMATION")
    print("=" * 60)

    df.info()

    print("\n" + "=" * 60)
    print("DATASET SHAPE")
    print("=" * 60)

    print(f"Rows    : {df.shape[0]:,}")
    print(f"Columns : {df.shape[1]}")


    print("\n" + "=" * 60)
    print("COLUMN NAMES")
    print("=" * 60)

    for column in df.columns:
        print(f"- {column}")


    print("\n" + "=" * 60)
    print("MISSING VALUES")
    print("=" * 60)

    missing_values = df.isnull().sum()

    missing_summary = pd.DataFrame(
        {
            "Missing Values": missing_values,
            "Missing Percentage": (
                missing_values / len(df) * 100
            ).round(2),
        }
    )

    print(missing_summary)


    print("\n" + "=" * 60)
    print("DUPLICATE ROWS")
    print("=" * 60)

    duplicate_count = df.duplicated().sum()

    print(f"Duplicate rows: {duplicate_count:,}")


    print("\n" + "=" * 60)
    print("NUMERICAL SUMMARY")
    print("=" * 60)

    print(
        df[["Quantity", "UnitPrice"]].describe()
    )


    print("\n" + "=" * 60)
    print("DATA TYPES")
    print("=" * 60)

    print(df.dtypes)


# ============================================================
# Data Cleaning
# ============================================================

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw Online Retail transaction dataset.

    Cleaning steps:
    1. Remove duplicate transactions.
    2. Remove transactions without CustomerID.
    3. Remove transactions without Description.
    4. Remove cancelled invoices.
    5. Remove non-positive quantities.
    6. Remove non-positive unit prices.
    7. Convert CustomerID to integer.
    8. Reset the dataframe index.

    Parameters
    ----------
    df : pd.DataFrame
        Raw transaction dataset.

    Returns
    -------
    pd.DataFrame
        Cleaned transaction dataset.
    """

    cleaned_df = df.copy()

    original_rows = len(cleaned_df)

    print("\n" + "=" * 60)
    print("DATA CLEANING")
    print("=" * 60)


    # --------------------------------------------------------
    # 1. Remove duplicate rows
    # --------------------------------------------------------

    before = len(cleaned_df)

    cleaned_df = cleaned_df.drop_duplicates()

    removed = before - len(cleaned_df)

    print(
        f"Duplicate rows removed       : {removed:,}"
    )


    # --------------------------------------------------------
    # 2. Remove rows without CustomerID
    # --------------------------------------------------------

    before = len(cleaned_df)

    cleaned_df = cleaned_df.dropna(
        subset=["CustomerID"]
    )

    removed = before - len(cleaned_df)

    print(
        f"Missing CustomerID removed   : {removed:,}"
    )


    # --------------------------------------------------------
    # 3. Remove rows without Description
    # --------------------------------------------------------

    before = len(cleaned_df)

    cleaned_df = cleaned_df.dropna(
        subset=["Description"]
    )

    removed = before - len(cleaned_df)

    print(
        f"Missing Description removed  : {removed:,}"
    )


    # --------------------------------------------------------
    # 4. Remove cancelled invoices
    # --------------------------------------------------------

    before = len(cleaned_df)

    cancelled_mask = (
        cleaned_df["InvoiceNo"]
        .astype(str)
        .str.startswith("C")
    )

    cleaned_df = cleaned_df.loc[
        ~cancelled_mask
    ]

    removed = before - len(cleaned_df)

    print(
        f"Cancelled invoices removed   : {removed:,}"
    )


    # --------------------------------------------------------
    # 5. Remove non-positive quantities
    # --------------------------------------------------------

    before = len(cleaned_df)

    cleaned_df = cleaned_df.loc[
        cleaned_df["Quantity"] > 0
    ]

    removed = before - len(cleaned_df)

    print(
        f"Non-positive quantities removed : {removed:,}"
    )


    # --------------------------------------------------------
    # 6. Remove non-positive unit prices
    # --------------------------------------------------------

    before = len(cleaned_df)

    cleaned_df = cleaned_df.loc[
        cleaned_df["UnitPrice"] > 0
    ]

    removed = before - len(cleaned_df)

    print(
        f"Non-positive prices removed   : {removed:,}"
    )


    # --------------------------------------------------------
    # 7. Convert CustomerID to integer
    # --------------------------------------------------------

    cleaned_df["CustomerID"] = (
        cleaned_df["CustomerID"]
        .astype(int)
    )


    # --------------------------------------------------------
    # 8. Reset index
    # --------------------------------------------------------

    cleaned_df = cleaned_df.reset_index(
        drop=True
    )


    # --------------------------------------------------------
    # Cleaning summary
    # --------------------------------------------------------

    final_rows = len(cleaned_df)

    print("\n" + "-" * 60)
    print("CLEANING SUMMARY")
    print("-" * 60)

    print(
        f"Original rows : {original_rows:,}"
    )

    print(
        f"Final rows    : {final_rows:,}"
    )

    print(
        f"Rows removed  : "
        f"{original_rows - final_rows:,}"
    )

    print(
        f"Rows retained : "
        f"{(final_rows / original_rows) * 100:.2f}%"
    )


    return cleaned_df


# ============================================================
# Save Cleaned Data
# ============================================================

def save_cleaned_data(df: pd.DataFrame) -> None:
    """
    Save the cleaned transaction dataset as CSV.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned transaction dataset.
    """

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        PROCESSED_DATA_PATH,
        index=False
    )

    print("\n" + "=" * 60)
    print("CLEANED DATA SAVED")
    print("=" * 60)

    print(
        f"File: {PROCESSED_DATA_PATH}"
    )


# ============================================================
# Main Execution
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("K-MEANS CUSTOMER SEGMENTATION")
    print("DATA PREPROCESSING PIPELINE")
    print("=" * 60)


    # --------------------------------------------------------
    # Load raw data
    # --------------------------------------------------------

    df = load_data()

    print(
        f"\nRaw dataset loaded: "
        f"{df.shape[0]:,} rows × {df.shape[1]} columns"
    )


    # --------------------------------------------------------
    # Inspect raw data
    # --------------------------------------------------------

    inspect_data(df)


    # --------------------------------------------------------
    # Clean data
    # --------------------------------------------------------

    cleaned_df = clean_data(df)


    # --------------------------------------------------------
    # Save cleaned data
    # --------------------------------------------------------

    save_cleaned_data(cleaned_df)


    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)