"""
Save the final K-Means customer segmentation model.

This module:
1. Loads the preprocessed customer features.
2. Trains the final K-Means model with k=3.
3. Validates the model.
4. Saves the trained model using joblib.

The saved model can later be loaded for assigning clusters
to new customer-level feature data.
"""

from pathlib import Path

import joblib
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

MODEL_DIR = (
    PROJECT_ROOT
    / "outputs"
)

MODEL_PATH = (
    MODEL_DIR
    / "kmeans_customer_segmentation.joblib"
)


# ============================================================
# MODEL CONFIGURATION
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

def load_data() -> pd.DataFrame:
    """
    Load the standardized customer-level features.
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
    Validate the input data before model training.
    """

    missing_columns = [
        column
        for column in FEATURE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required features: "
            f"{missing_columns}"
        )

    if df[FEATURE_COLUMNS].isnull().any().any():
        raise ValueError(
            "Clustering features contain missing values."
        )


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(
    df: pd.DataFrame
) -> KMeans:
    """
    Train the final K-Means model.
    """

    X = df[FEATURE_COLUMNS]

    model = KMeans(
        n_clusters=FINAL_K,
        random_state=RANDOM_STATE,
        n_init=10
    )

    model.fit(X)

    return model


# ============================================================
# VALIDATE MODEL
# ============================================================

def validate_model(
    model: KMeans,
    df: pd.DataFrame
) -> float:
    """
    Validate the trained model using the Silhouette Score.
    """

    X = df[FEATURE_COLUMNS]

    labels = model.labels_

    unique_clusters = len(
        set(labels)
    )

    if unique_clusters != FINAL_K:
        raise ValueError(
            f"Expected {FINAL_K} clusters, "
            f"but found {unique_clusters}."
        )

    silhouette = silhouette_score(
        X,
        labels
    )

    return silhouette


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(
    model: KMeans
) -> None:
    """
    Save the trained K-Means model.
    """

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    print(
        f"\nModel saved to:\n{MODEL_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("K-MEANS CUSTOMER SEGMENTATION")
    print("FINAL MODEL ARTIFACT")
    print("=" * 60)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    df = load_data()

    print(
        f"\nCustomers loaded: "
        f"{len(df):,}"
    )

    # --------------------------------------------------------
    # Validate data
    # --------------------------------------------------------

    validate_data(df)

    print(
        "Data validation: PASSED"
    )

    # --------------------------------------------------------
    # Train final model
    # --------------------------------------------------------

    model = train_model(
        df
    )

    print(
        f"\nK-Means model trained "
        f"with k={FINAL_K}"
    )

    # --------------------------------------------------------
    # Validate model
    # --------------------------------------------------------

    silhouette = validate_model(
        model,
        df
    )

    print(
        f"Silhouette Score: "
        f"{silhouette:.4f}"
    )

    print(
        f"Number of clusters: "
        f"{model.n_clusters}"
    )

    print(
        f"Number of iterations: "
        f"{model.n_iter_}"
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    save_model(
        model
    )

    print("\n" + "=" * 60)
    print("MODEL ARTIFACT COMPLETE")
    print("=" * 60)