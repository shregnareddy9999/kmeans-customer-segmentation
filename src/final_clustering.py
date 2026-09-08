"""
Final K-Means customer segmentation.

This module:
1. Fits the final K-Means model with k=3.
2. Validates the clustering result.
3. Assigns every customer to a cluster.
4. Converts cluster results back to original business-scale metrics.
5. Generates the final cluster profile table.
6. Saves the final customer segmentation and cluster profiles.
"""

from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ORIGINAL_FEATURES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_features.csv"
)

TRANSFORMED_FEATURES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_features_transformed.csv"
)

OUTPUTS_DIR = (
    PROJECT_ROOT
    / "outputs"
)

FINAL_SEGMENTATION_PATH = (
    OUTPUTS_DIR
    / "customer_segments.csv"
)

CLUSTER_PROFILE_PATH = (
    OUTPUTS_DIR
    / "cluster_profile.csv"
)

FINAL_CENTROIDS_PATH = (
    OUTPUTS_DIR
    / "cluster_centroids.csv"
)

ORIGINAL_SCALE_CENTROIDS_PATH = (
    OUTPUTS_DIR
    / "cluster_centroids_original_scale.csv"
)

CLUSTER_SIZES_PATH = (
    OUTPUTS_DIR
    / "cluster_sizes.csv"
)

SEGMENT_NAMES = {
    0: "At-Risk / Low-Value",
    1: "High-Value Loyal",
    2: "Regular / Growth",
}


# ============================================================
# FINAL MODEL CONFIGURATION
# ============================================================

FINAL_K = 3

RANDOM_STATE = 42

FEATURE_COLUMNS = [
    "Recency",
    "Frequency",
    "Monetary",
    "TotalQuantity",
    "AverageOrderValue",
    "UniqueProducts",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """
    Load both:

    1. Original customer-level features.
    2. Standardized features used by K-Means.
    """

    if not ORIGINAL_FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Original feature dataset not found at: "
            f"{ORIGINAL_FEATURES_PATH}"
        )

    if not TRANSFORMED_FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Transformed feature dataset not found at: "
            f"{TRANSFORMED_FEATURES_PATH}"
        )

    original_df = pd.read_csv(
        ORIGINAL_FEATURES_PATH
    )

    transformed_df = pd.read_csv(
        TRANSFORMED_FEATURES_PATH
    )

    return original_df, transformed_df


# ============================================================
# VALIDATION
# ============================================================

def validate_input_data(
    original_df,
    transformed_df
):
    """
    Validate that the original and transformed datasets
    are aligned correctly.
    """

    required_columns = [
        "CustomerID",
        *FEATURE_COLUMNS
    ]

    # Check original dataset
    missing_original = [
        column
        for column in required_columns
        if column not in original_df.columns
    ]

    if missing_original:
        raise ValueError(
            "Original dataset is missing columns: "
            f"{missing_original}"
        )

    # Check transformed dataset
    missing_transformed = [
        column
        for column in required_columns
        if column not in transformed_df.columns
    ]

    if missing_transformed:
        raise ValueError(
            "Transformed dataset is missing columns: "
            f"{missing_transformed}"
        )

    # Check row counts
    if len(original_df) != len(transformed_df):
        raise ValueError(
            "Original and transformed datasets "
            "have different numbers of rows."
        )

    # Check customer alignment
    if not original_df["CustomerID"].equals(
        transformed_df["CustomerID"]
    ):
        raise ValueError(
            "CustomerID order does not match between "
            "original and transformed datasets."
        )

    # Check missing values
    if original_df[FEATURE_COLUMNS].isnull().any().any():
        raise ValueError(
            "Original customer features contain missing values."
        )

    if transformed_df[FEATURE_COLUMNS].isnull().any().any():
        raise ValueError(
            "Transformed customer features contain missing values."
        )


# ============================================================
# FIT FINAL MODEL
# ============================================================

def fit_final_model(
    transformed_df
):
    """
    Fit the final K-Means model using k=3.
    """

    X = transformed_df[
        FEATURE_COLUMNS
    ]

    model = KMeans(
        n_clusters=FINAL_K,
        random_state=RANDOM_STATE,
        n_init=10
    )

    labels = model.fit_predict(X)

    return model, labels


# ============================================================
# VALIDATE FINAL CLUSTERS
# ============================================================

def validate_final_clustering(
    transformed_df,
    labels
):
    """
    Validate the final clustering solution.

    Checks:
    - Number of clusters
    - Missing labels
    - Cluster sizes
    - Silhouette score
    """

    X = transformed_df[
        FEATURE_COLUMNS
    ]

    print("\n" + "=" * 60)
    print("FINAL MODEL VALIDATION")
    print("=" * 60)

    unique_clusters = sorted(
        set(labels)
    )

    print(
        f"\nExpected clusters : "
        f"{FINAL_K}"
    )

    print(
        f"Actual clusters   : "
        f"{len(unique_clusters)}"
    )

    if len(unique_clusters) != FINAL_K:
        raise ValueError(
            "Final model did not produce the expected "
            f"{FINAL_K} clusters."
        )

    if pd.isnull(labels).any():
        raise ValueError(
            "Cluster labels contain missing values."
        )

    print(
        "\nCluster labels: PASSED"
    )

    cluster_counts = (
        pd.Series(labels)
        .value_counts()
        .sort_index()
    )

    print("\nCluster sizes:")

    for cluster, count in cluster_counts.items():

        percentage = (
            count
            / len(labels)
            * 100
        )

        print(
            f"Cluster {cluster}: "
            f"{count:,} customers "
            f"({percentage:.2f}%)"
        )

    if (cluster_counts == 0).any():
        raise ValueError(
            "At least one cluster contains zero customers."
        )

    silhouette = silhouette_score(
        X,
        labels
    )

    print(
        f"\nSilhouette Score: "
        f"{silhouette:.4f}"
    )

    print(
        "\nFinal clustering validation: PASSED"
    )

    return cluster_counts, silhouette


# ============================================================
# CREATE CUSTOMER SEGMENTATION
# ============================================================

def create_customer_segments(
    original_df,
    labels
):
    """
    Add cluster assignments to the original
    business-scale customer features.
    """

    segmented_df = original_df.copy()

    segmented_df["Cluster"] = labels

    return segmented_df


# ============================================================
# CREATE ORIGINAL-SCALE CLUSTER PROFILE
# ============================================================

def create_cluster_profile(
    segmented_df
):
    """
    Create cluster-level business profiles using
    the original, human-readable feature values.
    """

    profile = (
        segmented_df
        .groupby("Cluster")[FEATURE_COLUMNS]
        .mean()
        .round(2)
    )

    profile["CustomerCount"] = (
        segmented_df
        .groupby("Cluster")
        .size()
    )

    profile["CustomerPercentage"] = (
        profile["CustomerCount"]
        / len(segmented_df)
        * 100
    ).round(2)

    # Put customer count and percentage first
    profile = profile[
        [
            "CustomerCount",
            "CustomerPercentage",
            *FEATURE_COLUMNS,
        ]
    ]

    return profile


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(
    segmented_df,
    profile,
    model
):
    """
    Save final clustering outputs.
    """

    OUTPUTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Customer-level segmentation
    segmented_df.to_csv(
        FINAL_SEGMENTATION_PATH,
        index=False
    )

    # Cluster profile
    profile.to_csv(
        CLUSTER_PROFILE_PATH
    )

    # Final model centroids in scaled feature space
    centroid_df = pd.DataFrame(
        model.cluster_centers_,
        columns=FEATURE_COLUMNS
    )

    centroid_df.index.name = "Cluster"

    centroid_df.to_csv(
        FINAL_CENTROIDS_PATH
    )

    # Original-scale cluster means for business review
    original_centroids = (
        segmented_df
        .groupby("Cluster")[FEATURE_COLUMNS]
        .mean()
        .round(2)
        .reset_index()
    )

    original_centroids.to_csv(
        ORIGINAL_SCALE_CENTROIDS_PATH,
        index=False
    )

    # Dedicated cluster-size table
    cluster_sizes = (
        segmented_df
        .groupby("Cluster")
        .size()
        .reset_index(name="CustomerCount")
    )

    cluster_sizes["Segment"] = (
        cluster_sizes["Cluster"].map(SEGMENT_NAMES)
    )

    cluster_sizes["CustomerPercentage"] = (
        cluster_sizes["CustomerCount"]
        / len(segmented_df)
        * 100
    ).round(2)

    cluster_sizes = cluster_sizes[
        [
            "Cluster",
            "Segment",
            "CustomerCount",
            "CustomerPercentage",
        ]
    ]

    cluster_sizes.to_csv(
        CLUSTER_SIZES_PATH,
        index=False
    )

    print("\n" + "=" * 60)
    print("FINAL OUTPUTS SAVED")
    print("=" * 60)

    print(
        f"\nCustomer segmentation:"
        f"\n{FINAL_SEGMENTATION_PATH}"
    )

    print(
        f"\nCluster profile:"
        f"\n{CLUSTER_PROFILE_PATH}"
    )

    print(
        f"\nCluster centroids (scaled):"
        f"\n{FINAL_CENTROIDS_PATH}"
    )

    print(
        f"\nCluster centroids (original scale):"
        f"\n{ORIGINAL_SCALE_CENTROIDS_PATH}"
    )

    print(
        f"\nCluster sizes:"
        f"\n{CLUSTER_SIZES_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("K-MEANS CUSTOMER SEGMENTATION")
    print("FINAL MODEL — k=3")
    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    original_df, transformed_df = load_data()

    print(
        f"\nCustomers loaded: "
        f"{len(original_df):,}"
    )

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    validate_input_data(
        original_df,
        transformed_df
    )

    print(
        "Input data validation: PASSED"
    )

    # --------------------------------------------------------
    # Fit final model
    # --------------------------------------------------------

    model, labels = fit_final_model(
        transformed_df
    )

    print(
        f"\nFinal K-Means model fitted "
        f"with k={FINAL_K}"
    )

    # --------------------------------------------------------
    # Validate final clustering
    # --------------------------------------------------------

    cluster_counts, silhouette = (
        validate_final_clustering(
            transformed_df,
            labels
        )
    )

    # --------------------------------------------------------
    # Create customer-level segments
    # --------------------------------------------------------

    segmented_df = create_customer_segments(
        original_df,
        labels
    )

    # --------------------------------------------------------
    # Create business-scale profile
    # --------------------------------------------------------

    profile = create_cluster_profile(
        segmented_df
    )

    print("\n" + "=" * 60)
    print("ORIGINAL-SCALE CLUSTER PROFILE")
    print("=" * 60)

    print(
        profile.to_string(
            float_format=lambda x: f"{x:,.2f}"
        )
    )

    # --------------------------------------------------------
    # Save outputs
    # --------------------------------------------------------

    save_results(
        segmented_df,
        profile,
        model
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL CLUSTERING COMPLETE")
    print("=" * 60)

    print(
        f"\nFinal k          : {FINAL_K}"
    )

    print(
        f"Silhouette Score : {silhouette:.4f}"
    )

    print(
        f"Customers        : {len(segmented_df):,}"
    )