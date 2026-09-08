"""
K-Means clustering analysis for customer segmentation.

This module evaluates different values of k using:
1. Elbow Method (Inertia)
2. Silhouette Score

The results are saved as PNG plots so that the final
choice of k can be documented and justified.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRANSFORMED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_features_transformed.csv"
)

PLOTS_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "plots"
)


# ============================================================
# CLUSTERING FEATURES
# ============================================================

FEATURE_COLUMNS = [
    "Recency",
    "Frequency",
    "Monetary",
    "TotalQuantity",
    "AverageOrderValue",
    "UniqueProducts",
]


# Values of k that will be evaluated
K_VALUES = range(2, 11)


# ============================================================
# LOAD DATA
# ============================================================

def load_transformed_data() -> pd.DataFrame:
    """
    Load the standardized customer-level feature dataset.
    """

    if not TRANSFORMED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Transformed dataset not found at: "
            f"{TRANSFORMED_DATA_PATH}"
        )

    df = pd.read_csv(TRANSFORMED_DATA_PATH)

    return df


# ============================================================
# VALIDATE DATA
# ============================================================

def validate_data(df: pd.DataFrame) -> None:
    """
    Validate that all required clustering features exist
    and contain no missing values.
    """

    missing_columns = [
        column
        for column in FEATURE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required clustering features are missing: "
            f"{missing_columns}"
        )

    if df[FEATURE_COLUMNS].isnull().any().any():
        raise ValueError(
            "Clustering features contain missing values."
        )


# ============================================================
# CALCULATE K-MEANS METRICS
# ============================================================

def evaluate_k_values(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Evaluate multiple k values using:

    - Inertia for the Elbow Method
    - Silhouette Score for cluster separation
    """

    X = df[FEATURE_COLUMNS]

    results = []

    print("\n" + "=" * 60)
    print("K-MEANS MODEL SELECTION")
    print("=" * 60)

    for k in K_VALUES:

        print(f"\nEvaluating k = {k}...")

        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        cluster_labels = model.fit_predict(X)

        inertia = model.inertia_

        silhouette = silhouette_score(
            X,
            cluster_labels
        )

        results.append(
            {
                "k": k,
                "inertia": inertia,
                "silhouette_score": silhouette,
            }
        )

        print(
            f"Inertia           : {inertia:,.2f}"
        )

        print(
            f"Silhouette Score  : {silhouette:.4f}"
        )

    results_df = pd.DataFrame(results)

    return results_df


# ============================================================
# CREATE ELBOW PLOT
# ============================================================

def create_elbow_plot(
    results_df: pd.DataFrame
) -> None:
    """
    Create and save the Elbow Method plot.
    """

    PLOTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        results_df["k"],
        results_df["inertia"],
        marker="o"
    )

    plt.title(
        "Elbow Method for Selecting Number of Clusters"
    )

    plt.xlabel(
        "Number of Clusters (k)"
    )

    plt.ylabel(
        "Inertia"
    )

    plt.xticks(
        results_df["k"]
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    output_path = (
        PLOTS_DIR
        / "elbow_curve.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nElbow plot saved: {output_path}"
    )


# ============================================================
# CREATE SILHOUETTE PLOT
# ============================================================

def create_silhouette_plot(
    results_df: pd.DataFrame
) -> None:
    """
    Create and save the Silhouette Score plot.
    """

    PLOTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        results_df["k"],
        results_df["silhouette_score"],
        marker="o"
    )

    plt.title(
        "Silhouette Score for Selecting Number of Clusters"
    )

    plt.xlabel(
        "Number of Clusters (k)"
    )

    plt.ylabel(
        "Silhouette Score"
    )

    plt.xticks(
        results_df["k"]
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()

    output_path = (
        PLOTS_DIR
        / "silhouette_scores.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Silhouette plot saved: {output_path}"
    )


# ============================================================
# SAVE METRICS
# ============================================================

def save_evaluation_results(
    results_df: pd.DataFrame
) -> None:
    """
    Save evaluated k values and their metrics.
    """

    output_path = (
        PROJECT_ROOT
        / "outputs"
        / "k_evaluation_results.csv"
    )

    results_df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Evaluation results saved: {output_path}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("K-MEANS CUSTOMER SEGMENTATION")
    print("CLUSTER NUMBER EVALUATION")
    print("=" * 60)

    # Load data
    df = load_transformed_data()

    print(
        f"\nCustomer dataset loaded: "
        f"{len(df):,} customers"
    )

    # Validate
    validate_data(df)

    print(
        "Data validation: PASSED"
    )

    print(
        "\nFeatures used for K-Means:"
    )

    for feature in FEATURE_COLUMNS:
        print(f"- {feature}")

    # Evaluate different k values
    results_df = evaluate_k_values(df)

    # Display summary
    print("\n" + "=" * 60)
    print("K EVALUATION SUMMARY")
    print("=" * 60)

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    # Create plots
    print("\n" + "=" * 60)
    print("CREATING MODEL-SELECTION PLOTS")
    print("=" * 60)

    create_elbow_plot(
        results_df
    )

    create_silhouette_plot(
        results_df
    )

    # Save metrics
    save_evaluation_results(
        results_df
    )

    print("\n" + "=" * 60)
    print("K EVALUATION COMPLETE")
    print("=" * 60)