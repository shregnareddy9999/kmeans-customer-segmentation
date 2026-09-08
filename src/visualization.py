"""
Visualization module for the final K-Means customer segmentation.

Creates:
1. Cluster distribution chart
2. Customer segmentation scatter plot (Recency vs Monetary)
3. PCA cluster map of the scaled features used by K-Means
4. Cluster profile comparison chart

All visualizations are based on the validated k=3 model.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SEGMENTATION_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "customer_segments.csv"
)

PROFILE_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "cluster_profile.csv"
)

TRANSFORMED_FEATURES_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customer_features_transformed.csv"
)

FEATURE_COLUMNS = [
    "Recency",
    "Frequency",
    "Monetary",
    "TotalQuantity",
    "AverageOrderValue",
    "UniqueProducts",
]

PLOTS_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "plots"
)


# ============================================================
# CLUSTER INFORMATION
# ============================================================

CLUSTER_NAMES = {
    0: "At-Risk / Low-Value",
    1: "High-Value Loyal",
    2: "Regular / Growth",
}


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """
    Load final customer segmentation and cluster profiles.
    """

    if not SEGMENTATION_PATH.exists():
        raise FileNotFoundError(
            f"Customer segmentation file not found: "
            f"{SEGMENTATION_PATH}"
        )

    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            f"Cluster profile file not found: "
            f"{PROFILE_PATH}"
        )

    segmented_df = pd.read_csv(
        SEGMENTATION_PATH
    )

    profile_df = pd.read_csv(
        PROFILE_PATH
    )

    return segmented_df, profile_df


# ============================================================
# VALIDATION
# ============================================================

def validate_data(
    segmented_df,
    profile_df
):
    """
    Validate final segmentation data.
    """

    required_segmentation_columns = [
        "CustomerID",
        "Recency",
        "Frequency",
        "Monetary",
        "TotalQuantity",
        "AverageOrderValue",
        "UniqueProducts",
        "Cluster",
    ]

    for column in required_segmentation_columns:

        if column not in segmented_df.columns:
            raise ValueError(
                f"Missing column: {column}"
            )

    if segmented_df["Cluster"].nunique() != 3:
        raise ValueError(
            "Expected exactly 3 clusters."
        )

    if segmented_df["Cluster"].isnull().any():
        raise ValueError(
            "Cluster assignments contain missing values."
        )

    if len(profile_df) != 3:
        raise ValueError(
            "Expected exactly 3 cluster profiles."
        )


# ============================================================
# CLUSTER DISTRIBUTION
# ============================================================

def create_cluster_distribution(
    segmented_df
):
    """
    Create a bar chart showing the number of customers
    in each cluster.
    """

    cluster_counts = (
        segmented_df["Cluster"]
        .value_counts()
        .sort_index()
    )

    labels = [
        CLUSTER_NAMES[cluster]
        for cluster in cluster_counts.index
    ]

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        labels,
        cluster_counts.values
    )

    plt.title(
        "Customer Distribution by Segment"
    )

    plt.xlabel(
        "Customer Segment"
    )

    plt.ylabel(
        "Number of Customers"
    )

    plt.xticks(
        rotation=15
    )

    # Add values above bars
    for bar, value in zip(
        bars,
        cluster_counts.values
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height(),
            f"{value:,}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    output_path = (
        PLOTS_DIR
        / "cluster_distribution.png"
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
# CUSTOMER SEGMENTATION SCATTER PLOT
# ============================================================

def create_segmentation_scatter(
    segmented_df
):
    """
    Create a scatter plot showing customer segmentation
    using Monetary Value and Recency.
    """

    plt.figure(figsize=(10, 7))

    sns.scatterplot(
        data=segmented_df,
        x="Recency",
        y="Monetary",
        hue="Cluster",
        palette="viridis",
        alpha=0.65,
        s=45
    )

    plt.title(
        "Customer Segmentation: Recency vs Monetary Value"
    )

    plt.xlabel(
        "Recency (Days)"
    )

    plt.ylabel(
        "Monetary Value"
    )

    plt.legend(
        title="Cluster"
    )

    plt.tight_layout()

    output_path = (
        PLOTS_DIR
        / "customer_clusters.png"
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
# PCA CLUSTER MAP
# ============================================================

def load_scaled_features(segmented_df):
    """
    Load the scaled clustering matrix used by K-Means.

    Prefer the saved transformed table. If it is not present,
    reconstruct log1p + StandardScaler from original features.
    """

    if TRANSFORMED_FEATURES_PATH.exists():
        transformed_df = pd.read_csv(
            TRANSFORMED_FEATURES_PATH
        )

        scaled = transformed_df[FEATURE_COLUMNS].to_numpy()

        return scaled

    original = segmented_df[FEATURE_COLUMNS].to_numpy(
        dtype=float
    )

    log_features = np.log1p(original)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(log_features)

    return scaled


def create_pca_cluster_map(segmented_df):
    """
    Project scaled clustering features to 2D with PCA.

    PCA is used only for visualization. The K-Means model is
    trained on the six scaled features, not on PCA components.
    """

    scaled = load_scaled_features(segmented_df)

    pca = PCA(n_components=2, random_state=42)
    components = pca.fit_transform(scaled)

    plot_df = segmented_df.copy()
    plot_df["PC1"] = components[:, 0]
    plot_df["PC2"] = components[:, 1]

    plt.figure(figsize=(10, 7))

    sns.scatterplot(
        data=plot_df,
        x="PC1",
        y="PC2",
        hue="Cluster",
        palette="viridis",
        alpha=0.65,
        s=45
    )

    explained = pca.explained_variance_ratio_

    plt.title(
        "Customer Segments — PCA Projection"
    )

    plt.xlabel(
        f"PC1 ({explained[0] * 100:.1f}% variance)"
    )

    plt.ylabel(
        f"PC2 ({explained[1] * 100:.1f}% variance)"
    )

    plt.legend(
        title="Cluster"
    )

    plt.tight_layout()

    output_path = (
        PLOTS_DIR
        / "customer_clusters_pca.png"
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
# CLUSTER PROFILE HEATMAP
# ============================================================

def create_cluster_profile_heatmap(
    profile_df
):
    """
    Create a heatmap comparing behavioral characteristics
    of the three customer segments.

    The behavioral features are standardized only for
    visualization so that features with different numerical
    scales can be compared fairly.
    """

    profile_features = [
        "Recency",
        "Frequency",
        "Monetary",
        "TotalQuantity",
        "AverageOrderValue",
        "UniqueProducts",
    ]

    profile_matrix = (
        profile_df[
            profile_features
        ]
        .copy()
    )

    profile_matrix.index = [
        CLUSTER_NAMES[int(cluster)]
        for cluster in profile_df["Cluster"]
    ]

    # Standardize each feature across the three clusters
    profile_matrix = (
        profile_matrix
        - profile_matrix.mean()
    ) / profile_matrix.std()

    plt.figure(
        figsize=(11, 6)
    )

    sns.heatmap(
        profile_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0
    )

    plt.title(
        "Relative Customer Segment Profile"
    )

    plt.xlabel(
        "Customer Behavior Feature"
    )

    plt.ylabel(
        "Customer Segment"
    )

    plt.tight_layout()

    output_path = (
        PLOTS_DIR
        / "cluster_profile_heatmap.png"
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
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("K-MEANS CUSTOMER SEGMENTATION")
    print("FINAL VISUALIZATION")
    print("=" * 60)

    # Load
    segmented_df, profile_df = load_data()

    print(
        f"\nCustomers loaded: "
        f"{len(segmented_df):,}"
    )

    # Validate
    validate_data(
        segmented_df,
        profile_df
    )

    print(
        "Data validation: PASSED"
    )

    # Create directory
    PLOTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create visualizations
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)

    create_cluster_distribution(
        segmented_df
    )

    create_segmentation_scatter(
        segmented_df
    )

    create_pca_cluster_map(
        segmented_df
    )

    create_cluster_profile_heatmap(
        profile_df
    )

    print("\n" + "=" * 60)
    print("VISUALIZATION COMPLETE")
    print("=" * 60)