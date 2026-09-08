"""
Exploratory Data Analysis for K-Means Customer Segmentation.

This module analyzes customer-level behavioral features before
preprocessing and K-Means clustering.

The analysis includes:
- Descriptive statistics
- Feature skewness
- Distribution plots
- Correlation analysis
- IQR-based outlier analysis
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


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

PLOTS_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "plots"
)


# ============================================================
# Configuration
# ============================================================

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
# Data Validation
# ============================================================

def validate_data(
    df: pd.DataFrame
) -> None:
    """
    Validate that all required customer features exist.
    """

    missing_columns = [
        column
        for column in FEATURE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required feature columns are missing: "
            f"{missing_columns}"
        )

    if df[FEATURE_COLUMNS].isnull().any().any():
        raise ValueError(
            "Customer feature dataset contains missing values."
        )


# ============================================================
# Descriptive Statistics
# ============================================================

def display_descriptive_statistics(
    df: pd.DataFrame
) -> None:
    """
    Display descriptive statistics for customer features.
    """

    print("\n" + "=" * 60)
    print("DESCRIPTIVE STATISTICS")
    print("=" * 60)

    print(
        df[FEATURE_COLUMNS].describe().round(2)
    )


# ============================================================
# Skewness Analysis
# ============================================================

def display_skewness(
    df: pd.DataFrame
) -> None:
    """
    Calculate and display feature skewness.
    """

    skewness = (
        df[FEATURE_COLUMNS]
        .skew()
        .sort_values(
            ascending=False
        )
    )

    print("\n" + "=" * 60)
    print("FEATURE SKEWNESS")
    print("=" * 60)

    for feature, value in skewness.items():

        if abs(value) < 0.5:
            interpretation = "Low skewness"

        elif abs(value) < 1:
            interpretation = "Moderate skewness"

        else:
            interpretation = "High skewness"

        print(
            f"{feature:<20} "
            f"{value:>10.3f}   "
            f"{interpretation}"
        )


# ============================================================
# Distribution Plots
# ============================================================

def create_distribution_plots(
    df: pd.DataFrame
) -> None:
    """
    Create and save distribution plots for each feature.
    """

    PLOTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for feature in FEATURE_COLUMNS:

        plt.figure(
            figsize=(10, 6)
        )

        sns.histplot(
            data=df,
            x=feature,
            kde=True
        )

        plt.title(
            f"Distribution of {feature}"
        )

        plt.xlabel(feature)
        plt.ylabel("Number of Customers")

        plt.tight_layout()

        output_path = (
            PLOTS_DIR
            / f"distribution_{feature.lower()}.png"
        )

        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(
            f"Saved: {output_path}"
        )


# ============================================================
# Correlation Analysis
# ============================================================

def create_correlation_heatmap(
    df: pd.DataFrame
) -> None:
    """
    Create and save a correlation heatmap.
    """

    correlation_matrix = (
        df[FEATURE_COLUMNS]
        .corr()
    )

    plt.figure(
        figsize=(10, 8)
    )

    sns.heatmap(
        correlation_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        square=True
    )

    plt.title(
        "Customer Feature Correlation Matrix"
    )

    plt.tight_layout()

    output_path = (
        PLOTS_DIR
        / "feature_correlation_heatmap.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_path}"
    )


# ============================================================
# Outlier Analysis
# ============================================================

def calculate_outlier_summary(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate IQR-based outlier counts and percentages.
    """

    results = []

    for feature in FEATURE_COLUMNS:

        q1 = df[feature].quantile(0.25)
        q3 = df[feature].quantile(0.75)

        iqr = q3 - q1

        lower_bound = (
            q1 - 1.5 * iqr
        )

        upper_bound = (
            q3 + 1.5 * iqr
        )

        outlier_mask = (
            (df[feature] < lower_bound)
            | (df[feature] > upper_bound)
        )

        outlier_count = (
            outlier_mask.sum()
        )

        outlier_percentage = (
            outlier_count
            / len(df)
            * 100
        )

        results.append(
            {
                "Feature": feature,
                "Lower Bound": lower_bound,
                "Upper Bound": upper_bound,
                "Outlier Count": outlier_count,
                "Outlier Percentage": (
                    outlier_percentage
                ),
            }
        )

    return pd.DataFrame(results)


def display_outlier_summary(
    df: pd.DataFrame
) -> None:
    """
    Display the IQR-based outlier summary.
    """

    outlier_summary = (
        calculate_outlier_summary(df)
    )

    print("\n" + "=" * 60)
    print("OUTLIER ANALYSIS — IQR METHOD")
    print("=" * 60)

    print(
        outlier_summary.to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}"
        )
    )


# ============================================================
# Main Execution
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("K-MEANS CUSTOMER SEGMENTATION")
    print("EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    # --------------------------------------------------------
    # Load customer-level features
    # --------------------------------------------------------

    df = load_customer_features()

    print(
        f"\nCustomer dataset loaded: "
        f"{len(df):,} customers"
    )

    # --------------------------------------------------------
    # Validate data
    # --------------------------------------------------------

    validate_data(df)

    print(
        "Data validation: PASSED"
    )

    # --------------------------------------------------------
    # Descriptive statistics
    # --------------------------------------------------------

    display_descriptive_statistics(df)

    # --------------------------------------------------------
    # Skewness
    # --------------------------------------------------------

    display_skewness(df)

    # --------------------------------------------------------
    # Distribution plots
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("CREATING DISTRIBUTION PLOTS")
    print("=" * 60)

    create_distribution_plots(df)

    # --------------------------------------------------------
    # Correlation heatmap
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("CREATING CORRELATION HEATMAP")
    print("=" * 60)

    create_correlation_heatmap(df)

    # --------------------------------------------------------
    # Outlier analysis
    # --------------------------------------------------------

    display_outlier_summary(df)

    # --------------------------------------------------------
    # Completion
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("EDA COMPLETE")
    print("=" * 60)

    print(
        f"Plots saved to: {PLOTS_DIR}"
    )