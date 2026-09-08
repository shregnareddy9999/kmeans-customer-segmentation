# Customer Segmentation using K-Means Clustering

A machine learning project that segments customers from the Online Retail transaction dataset using K-Means clustering.

Transaction-level records are converted into customer-level behavioral features. K-Means is then used to identify three customer groups, which are profiled and translated into business recommendations.

The final model uses **k = 3** and analyzes **4,338 customers**.

---

## Task 3 Deliverables

| Requirement | Location |
| --- | --- |
| Dataset source | This README and [docs/dataset.md](docs/dataset.md) |
| Sample of cleaned/used dataset | [data/samples/customer_features_sample.csv](data/samples/customer_features_sample.csv) |
| Notebook | [notebooks/customer_segmentation.ipynb](notebooks/customer_segmentation.ipynb) |
| Scripts | [src/](src/) |
| Chosen k with justification | Elbow and silhouette plots plus [outputs/k_evaluation_results.csv](outputs/k_evaluation_results.csv) |
| Cluster centroids (scaled) | [outputs/cluster_centroids.csv](outputs/cluster_centroids.csv) |
| Cluster centroids (original units) | [outputs/cluster_centroids_original_scale.csv](outputs/cluster_centroids_original_scale.csv) |
| Cluster sizes | [outputs/cluster_sizes.csv](outputs/cluster_sizes.csv) |
| Cluster profile table | [outputs/cluster_profile.csv](outputs/cluster_profile.csv) |
| Cluster plots (PNG) | [outputs/plots/](outputs/plots/) |
| Business cluster profiles | [docs/cluster_profiles.md](docs/cluster_profiles.md) |
| Actionable recommendations | [docs/business_recommendations.md](docs/business_recommendations.md) |
| Saved model | [outputs/kmeans_customer_segmentation.joblib](outputs/kmeans_customer_segmentation.joblib) |

---

## Internship Task

**Arithmatrix Virtual Internship Program (AVIP) 2026**

### Task 3 — K-Means Customer Segmentation

This repository includes:

- Dataset source documentation
- Data cleaning and customer-level feature engineering
- K-Means clustering with Elbow Method and Silhouette Score
- Cluster centroids, cluster sizes, and PNG visualizations
- Concise business-oriented cluster profiles
- Three actionable recommendations
- Optional interactive frontend for presenting the results

---

## Dataset

### Online Retail Dataset

The source data is a UK-based online retail transaction extract. Each row is a line item, not a customer.

Columns include InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, and Country.

**Source:** [UCI Machine Learning Repository — Online Retail](https://archive.ics.uci.edu/ml/datasets/online+retail)

A Kaggle-hosted copy of the same UCI dataset was used for local analysis. Full dataset documentation is in [docs/dataset.md](docs/dataset.md).

### Data preparation

Unusable records were removed before aggregation, including missing CustomerID values, cancelled invoices, non-positive quantities, and non-positive unit prices.

| Metric | Value |
| --- | ---: |
| Original transactions | 541,909 |
| Cleaned transactions | 392,692 |
| Customers analyzed | 4,338 |

Approximately **72.46%** of original transaction records were retained.

---

## Features

Transactions were aggregated to one row per `CustomerID`. Clustering uses these features:

| Feature | Meaning |
| --- | --- |
| Recency | Days since the customer's most recent purchase |
| Frequency | Number of unique orders |
| Monetary | Total customer spending |
| TotalQuantity | Total quantity purchased |
| AverageOrderValue | Average spending per order |
| UniqueProducts | Number of unique products purchased |

`CustomerID` is an identifier only and is not a clustering feature.

---

## Preprocessing

Customer features are positively skewed, especially Monetary, Total Quantity, Average Order Value, and Frequency. K-Means is distance-based, so raw values are not used directly.

```text
Customer Features
       ↓
Log1p Transformation
       ↓
StandardScaler
       ↓
K-Means
```

---

## Clustering Method

K-Means was evaluated for **k = 2 to 10** using inertia (Elbow Method) and Silhouette Score.

### Model selection

| k | Silhouette Score | Inertia |
| ---: | ---: | ---: |
| 2 | 0.3560 | 15,009 |
| 3 | 0.2609 | 11,948 |
| 4 | 0.2261 | 10,456 |
| 5 | 0.2270 | 9,296 |

**k = 2** has the highest silhouette score. The elbow curve is gradual rather than a sharp kink; the largest inertia drops occur from k = 2 to k = 5.

**k = 3** was selected as the final solution because it keeps an acceptable clustering structure while producing three usable business segments: at-risk / low-value, regular / growth, and high-value loyal customers. Higher values of k add complexity without a meaningful silhouette improvement.

### Final model

| Setting | Value |
| --- | --- |
| Algorithm | K-Means |
| Number of clusters | 3 |
| Silhouette Score | 0.2609 |
| Random state | 42 |

---

## Final Customer Segments

### Cluster 0 — At-Risk / Low-Value

**1,221 customers (28.15%)**

Highest recency, lowest frequency, lowest monetary value, and lowest product diversity. These customers show weak recent engagement.

Suggested actions: re-engagement campaigns, personalized offers, product recommendations, and limited-time promotions.

### Cluster 1 — High-Value Loyal

**1,188 customers (27.39%)**

Lowest recency with the highest frequency, monetary value, product diversity, and average order value. This is the strongest commercial segment.

Suggested actions: loyalty rewards, early access, premium offers, personalized recommendations, and cross-selling.

### Cluster 2 — Regular / Growth

**1,929 customers (44.47%)**

Moderate recency, frequency, monetary value, and product diversity. This is the largest segment and the main growth opportunity.

Suggested actions: cross-selling, product bundles, personalized promotions, and repeat-purchase campaigns.

Full profiles: [docs/cluster_profiles.md](docs/cluster_profiles.md)

---

## Business Recommendations

1. **Retain high-value customers (Cluster 1)** through loyalty programs, personalized experiences, and premium engagement.
2. **Grow regular customers (Cluster 2)** by increasing purchase frequency and spending through recommendations and cross-selling.
3. **Re-engage at-risk customers (Cluster 0)** with targeted campaigns that encourage another purchase.

These recommendations are interpretations of clustering patterns and should be validated with campaign performance data. Details: [docs/business_recommendations.md](docs/business_recommendations.md)

---

## Project Outputs

```text
data/
├── raw/                          # Online Retail.xlsx (local; not committed)
├── processed/                    # generated locally after running the pipeline
└── samples/
    └── customer_features_sample.csv

outputs/
├── cluster_centroids.csv
├── cluster_centroids_original_scale.csv
├── cluster_sizes.csv
├── cluster_profile.csv
├── customer_segments.csv
├── k_evaluation_results.csv
├── kmeans_customer_segmentation.joblib
└── plots/
    ├── elbow_curve.png
    ├── silhouette_scores.png
    ├── cluster_distribution.png
    ├── customer_clusters.png
    ├── customer_clusters_pca.png
    ├── cluster_profile_heatmap.png
    ├── feature_correlation_heatmap.png
    └── distribution_*.png
```

- `cluster_centroids.csv` stores K-Means centers in **scaled** feature space.
- `cluster_centroids_original_scale.csv` stores cluster means in **original business units** (days, orders, spend).
- `customer_clusters.png` is Recency vs Monetary.
- `customer_clusters_pca.png` is a 2D PCA cluster map of the scaled features used by K-Means.

---

## Interactive Frontend

The optional React dashboard presents the completed clustering results. It is a presentation layer, not a substitute for the notebook, CSVs, or PNG plots.

It covers overall statistics, segment comparison, customer lookup, and business recommendations.

See [frontend/README.md](frontend/README.md).

---

## Jupyter Notebook

[notebooks/customer_segmentation.ipynb](notebooks/customer_segmentation.ipynb) walks through loading, cleaning, feature construction, EDA, transformation, k selection, K-Means, evaluation, profiling, visualization, and business interpretation.

---

## Project Structure

```text
kmeans-customer-segmentation/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
├── docs/
│   ├── task_context.md
│   ├── architecture.md
│   ├── dataset.md
│   ├── methodology.md
│   ├── cluster_profiles.md
│   └── business_recommendations.md
├── notebooks/
│   └── customer_segmentation.ipynb
├── src/
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── eda.py
│   ├── preprocessing.py
│   ├── clustering.py
│   ├── cluster_analysis.py
│   ├── final_clustering.py
│   ├── visualization.py
│   └── save_model.py
├── outputs/
│   └── plots/
└── frontend/
```

---

## Technologies

Python, pandas, NumPy, matplotlib, seaborn, scikit-learn, joblib, Jupyter, React, Vite, Recharts.

---

## Reproduction

1. Clone or copy the project folder and enter it:

```bash
cd kmeans-customer-segmentation
```

2. Create and activate a virtual environment.

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Place `Online Retail.xlsx` in `data/raw/`.

5. Run the pipeline in order:

```bash
python src/data_preprocessing.py
python src/feature_engineering.py
python src/eda.py
python src/preprocessing.py
python src/clustering.py
python src/final_clustering.py
python src/visualization.py
python src/save_model.py
```

To view the dashboard:

```bash
cd frontend
npm install
npm run dev
```

---

## Evaluation

The primary clustering metric is Silhouette Score. The final model score is **0.2609**.

Additional checks include inertia, cluster sizes, centroid analysis, behavioral separation, and business interpretability.

---

## Limitations

- The dataset is historical retail transactions from 2010–2011.
- Results depend on feature selection and preprocessing.
- K-Means assumes relatively spherical clusters in the scaled space.
- Recommendations are not causal conclusions.
- Customer behavior can change; campaigns should be tested before rollout.

---

## Future Improvements

Possible extensions include customer lifetime value modeling, segment migration tracking, alternative clustering algorithms, and campaign-response measurement.
