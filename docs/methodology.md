# Methodology — K-Means Customer Segmentation

## 1. Objective

This project segments customers by purchasing behavior using K-Means.

Transaction-level retail data is converted into customer-level features. The resulting clusters are profiled and turned into business recommendations.

---

## 2. Overall Workflow

```text
Dataset Collection
       ↓
Data Understanding
       ↓
Data Cleaning
       ↓
Customer-Level Feature Engineering
       ↓
Exploratory Data Analysis
       ↓
Feature Preprocessing (log1p + StandardScaler)
       ↓
Determine Optimal k (Elbow + Silhouette)
       ↓
K-Means Model Training (k = 3)
       ↓
Cluster Evaluation
       ↓
Cluster Profiling
       ↓
Business Recommendations
```

---

## 3. Data Collection

The Online Retail Dataset was loaded from:

```text
data/raw/Online Retail.xlsx
```

Source documentation is in [docs/dataset.md](dataset.md). The raw file was left unchanged so preprocessing can be reproduced.

---

## 4. Data Understanding

Before cleaning, the file was inspected for row and column counts, dtypes, missing values, duplicates, unique customers and products, date range, quantity and unit-price distributions, and countries.

---

## 5. Data Cleaning

Records were removed when they could not support customer-level purchase analysis:

- Missing CustomerID
- Cancelled invoices
- Non-positive Quantity
- Non-positive UnitPrice
- Duplicate rows

Missing product descriptions were reviewed and did not affect the final numerical feature set.

**Result:** 541,909 transactions reduced to 392,692 cleaned transactions and 4,338 customers.

---

## 6. Exploratory Data Analysis

EDA covered feature distributions, skewness, correlation, and IQR-based outlier checks.

Monetary, TotalQuantity, AverageOrderValue, and Frequency are strongly right-skewed. That finding drove the log1p transformation before scaling.

Plots are stored in `outputs/plots/` (`distribution_*.png`, `feature_correlation_heatmap.png`).

---

## 7. Customer-Level Feature Engineering

K-Means operates on one row per customer. Transactions were grouped by CustomerID.

### RFM features

- **Recency:** days since the last purchase, using a reference date of one day after the latest invoice.
- **Frequency:** count of distinct invoices.
- **Monetary:** sum of Quantity × UnitPrice.

### Additional features

- TotalQuantity
- AverageOrderValue
- UniqueProducts

These six fields are the clustering feature set. CustomerID is not used as a feature.

---

## 8. Feature Preprocessing

Because K-Means uses Euclidean distance:

1. Apply `numpy.log1p` to the six clustering features.
2. Fit `StandardScaler` and transform the log features.
3. Keep CustomerID alongside the scaled matrix for later joins.

The transformed table is written to `data/processed/customer_features_transformed.csv` when the pipeline is run locally.

---

## 9. Determining the Number of Clusters

k was not chosen in advance. Values from **2 to 10** were evaluated.

**Elbow Method.** Inertia was plotted against k and saved as `outputs/plots/elbow_curve.png`. The curve declines smoothly; the steepest drops occur between k = 2 and k = 5. There is no single sharp elbow.

**Silhouette Score.** Scores were computed for the same range and saved as `outputs/plots/silhouette_scores.png` and `outputs/k_evaluation_results.csv`.

| k | Silhouette Score | Inertia |
| ---: | ---: | ---: |
| 2 | 0.3560 | 15,009.11 |
| 3 | 0.2609 | 11,948.01 |
| 4 | 0.2261 | 10,456.07 |
| 5 | 0.2270 | 9,295.80 |

k = 2 has the best silhouette. **k = 3** was selected because it remains structurally acceptable and splits the base into three actionable groups (low-value / at-risk, regular / growth, high-value loyal). Larger k did not improve silhouette enough to justify extra segments.

---

## 10. K-Means Clustering

The final model:

- Algorithm: K-Means
- k = 3
- `random_state = 42`
- Features: scaled log1p customer features

Each customer received a cluster label. Labels were joined back to the original-scale feature table.

---

## 11. Cluster Evaluation

Evaluation used:

- Silhouette Score of the final model: **0.2609**
- Cluster sizes
- Scaled centroids (`outputs/cluster_centroids.csv`)
- Original-scale means (`outputs/cluster_centroids_original_scale.csv`, `outputs/cluster_profile.csv`)
- Recency–Monetary scatter and PCA cluster map

---

## 12. Cluster Centroids

K-Means centroids are the mean of each cluster in the **scaled** space used for training. They are saved as:

```text
outputs/cluster_centroids.csv
```

Business interpretation uses original-scale means:

```text
outputs/cluster_centroids_original_scale.csv
```

---

## 13. Cluster Profiling

Each cluster was described by size and average Recency, Frequency, Monetary, TotalQuantity, AverageOrderValue, and UniqueProducts.

Assigned names from the observed pattern:

| Cluster | Segment | Customers | Share |
| ---: | --- | ---: | ---: |
| 0 | At-Risk / Low-Value | 1,221 | 28.15% |
| 1 | High-Value Loyal | 1,188 | 27.39% |
| 2 | Regular / Growth | 1,929 | 44.47% |

Full write-up: [docs/cluster_profiles.md](cluster_profiles.md)

---

## 14. Cluster Visualization

Saved plots include:

- `outputs/plots/elbow_curve.png`
- `outputs/plots/silhouette_scores.png`
- `outputs/plots/cluster_distribution.png`
- `outputs/plots/customer_clusters.png` (Recency vs Monetary)
- `outputs/plots/customer_clusters_pca.png` (PCA cluster map)
- `outputs/plots/cluster_profile_heatmap.png`

PCA is used only for visualization. The model is trained on the six scaled features, not on PCA components.

---

## 15. Business Interpretation and Recommendations

Technical results were translated into segment strategies: retain Cluster 1, grow Cluster 2, re-engage Cluster 0.

Write-up: [docs/business_recommendations.md](business_recommendations.md)

---

## 16. Saved Results

```text
outputs/
├── plots/
├── cluster_centroids.csv
├── cluster_centroids_original_scale.csv
├── cluster_sizes.csv
├── cluster_profile.csv
├── customer_segments.csv
├── k_evaluation_results.csv
└── kmeans_customer_segmentation.joblib
```

The customer-level sample is:

```text
data/samples/customer_features_sample.csv
```

---

## 17. Reproducibility

Reproducibility is supported by a documented dataset source, fixed preprocessing, `random_state = 42`, `requirements.txt`, modular scripts in `src/`, and the executed notebook `notebooks/customer_segmentation.ipynb`.

---

## 18. Principle

The data determined the segments. k, features, and labels were chosen from analysis and business interpretability, not from a predetermined story.
