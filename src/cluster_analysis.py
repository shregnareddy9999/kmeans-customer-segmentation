"""
Candidate cluster analysis for K-Means Customer Segmentation.

This module compares candidate values of k and analyzes:
- Cluster sizes
- Cluster centroids
- Silhouette scores

The purpose is to help select a final k based on both
technical quality and business interpretability.
"""

from pathlib import Path

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

OUTPUTS_DIR = (
    PROJECT_ROOT
    / "outputs"
)


# ============================================================
# FEATURES
# ============================================================

FEATURE_COLUMNS = [
    "Recency",
    "Frequency",
    "Monetary",
    "TotalQuantity",
    "AverageOrderValue",
    "UniqueProducts",
]


# Candidate values selected for deeper analysis
CANDIDATE_K_VALUES = [2, 3, 4, 5]


# ============================================================
# LOAD DATA
# ============================================================

def load_data() -> pd.DataFrame:
    """
    Load the standardized customer feature dataset.
    """

    if not TRANSFORMED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Transformed dataset not found at: "
            f"{TRANSFORMED_DATA_PATH}"
        )

    return pd.read_csv(
        TRANSFORMED_DATA_PATH
    )


# ============================================================
# VALIDATE DATA
# ============================================================

def validate_data(
    df: pd.DataFrame
) -> None:
    """
    Validate required columns and missing values.
    """

    required_columns = [
        "CustomerID",
        *FEATURE_COLUMNS
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{missing_columns}"
        )

    if df[FEATURE_COLUMNS].isnull().any().any():
        raise ValueError(
            "Clustering features contain missing values."
        )


# ============================================================
# ANALYZE A SINGLE K
# ============================================================

def analyze_k(
    df: pd.DataFrame,
    k: int
):
    """
    Fit K-Means for a given k and return:
    - Model
    - Cluster labels
    - Silhouette score
    - Cluster sizes
    - Cluster centroids
    """

    X = df[FEATURE_COLUMNS]

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(X)

    silhouette = silhouette_score(
        X,
        labels
    )

    cluster_sizes = (
        pd.Series(labels)
        .value_counts()
        .sort_index()
    )

    centroids = pd.DataFrame(
        model.cluster_centers_,
        columns=FEATURE_COLUMNS
    )

    return (
        model,
        labels,
        silhouette,
        cluster_sizes,
        centroids
    )


# ============================================================
# MAIN ANALYSIS
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("K-MEANS CUSTOMER SEGMENTATION")
    print("CANDIDATE CLUSTER ANALYSIS")
    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    df = load_data()

    print(
        f"\nCustomer dataset loaded: "
        f"{len(df):,} customers"
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_data(df)

    print(
        "Data validation: PASSED"
    )

    # --------------------------------------------------------
    # Prepare output directory
    # --------------------------------------------------------

    OUTPUTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Compare candidate k values
    # --------------------------------------------------------

    comparison_results = []

    for k in CANDIDATE_K_VALUES:

        print("\n" + "=" * 60)
        print(f"ANALYSIS FOR k = {k}")
        print("=" * 60)

        (
            model,
            labels,
            silhouette,
            cluster_sizes,
            centroids
        ) = analyze_k(
            df,
            k
        )

        print(
            f"\nSilhouette Score: "
            f"{silhouette:.4f}"
        )

        print("\nCluster Sizes:")

        for cluster, size in cluster_sizes.items():

            percentage = (
                size
                / len(df)
                * 100
            )

            print(
                f"Cluster {cluster}: "
                f"{size:,} customers "
                f"({percentage:.2f}%)"
            )

        print("\nCluster Centroids:")

        print(
            centroids.round(3).to_string()
        )

        # Store summary
        comparison_results.append(
            {
                "k": k,
                "silhouette_score": silhouette,
                "minimum_cluster_size": cluster_sizes.min(),
                "maximum_cluster_size": cluster_sizes.max(),
            }
        )

        # ----------------------------------------------------
        # Save cluster sizes
        # ----------------------------------------------------

        cluster_size_df = pd.DataFrame(
            {
                "Cluster": cluster_sizes.index,
                "Customer_Count": cluster_sizes.values,
                "Percentage": (
                    cluster_sizes.values
                    / len(df)
                    * 100
                )
            }
        )

        cluster_size_path = (
            OUTPUTS_DIR
            / f"cluster_sizes_k{k}.csv"
        )

        cluster_size_df.to_csv(
            cluster_size_path,
            index=False
        )

        # ----------------------------------------------------
        # Save centroids
        # ----------------------------------------------------

        centroid_path = (
            OUTPUTS_DIR
            / f"cluster_centroids_k{k}.csv"
        )

        centroids.to_csv(
            centroid_path,
            index_label="Cluster"
        )

        print(
            f"\nSaved cluster sizes: "
            f"{cluster_size_path}"
        )

        print(
            f"Saved centroids: "
            f"{centroid_path}"
        )

    # --------------------------------------------------------
    # Save candidate comparison
    # --------------------------------------------------------

    comparison_df = pd.DataFrame(
        comparison_results
    )

    comparison_path = (
        OUTPUTS_DIR
        / "candidate_k_comparison.csv"
    )

    comparison_df.to_csv(
        comparison_path,
        index=False
    )

    # --------------------------------------------------------
    # Display final comparison
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("CANDIDATE K COMPARISON")
    print("=" * 60)

    print(
        comparison_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    print("\n" + "=" * 60)
    print("CANDIDATE ANALYSIS COMPLETE")
    print("=" * 60)

    print(
        f"\nComparison saved to: "
        f"{comparison_path}"
    )