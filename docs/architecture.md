# Architecture — K-Means Customer Segmentation

## 1. Architecture Overview

The project is a modular machine learning pipeline with a separate optional presentation layer.

It separates data storage, preprocessing, feature engineering, clustering, evaluation, visualization, documentation, and the frontend.

---

## 2. High-Level Data Flow

```text
Online Retail Dataset
       ↓
Data Validation and Cleaning
       ↓
Transaction-Level Clean Data
       ↓
Customer-Level Feature Engineering
       ↓
EDA
       ↓
log1p + StandardScaler
       ↓
K Selection (Elbow + Silhouette)
       ↓
K-Means (k = 3)
       ↓
Cluster Evaluation
       ↓
Cluster Profiling
       ├─ Cluster Centroids
       ├─ Cluster Sizes
       ├─ Visualizations
       └─ Business Recommendations
```

---

## 3. Project Components

### 3.1 Data Layer

```text
data/
├── raw/
├── processed/
└── samples/
```

- `raw/` holds `Online Retail.xlsx` locally (not committed).
- `processed/` holds generated cleaned transactions and feature tables when the pipeline is run.
- `samples/` holds `customer_features_sample.csv` for the repository.

### 3.2 Documentation Layer

```text
docs/
├── task_context.md
├── architecture.md
├── dataset.md
├── methodology.md
├── cluster_profiles.md
└── business_recommendations.md
```

### 3.3 Notebook Layer

`notebooks/customer_segmentation.ipynb` contains the end-to-end analysis with executed outputs.

### 3.4 Source Code Layer

```text
src/
├── data_preprocessing.py
├── feature_engineering.py
├── eda.py
├── preprocessing.py
├── clustering.py
├── cluster_analysis.py
├── final_clustering.py
├── visualization.py
└── save_model.py
```

Each module has a single stage of the pipeline.

### 3.5 Output Layer

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

### 3.6 Presentation Layer

```text
frontend/
```

The React dashboard is optional. It reads exported CSVs from `frontend/public/data/` and does not retrain the model. It is not a replacement for the notebook, PNG plots, or CSV artifacts.

---

## 4. Runtime Flow

1. Place the Excel file in `data/raw/`.
2. Run `src/` scripts in the order listed in the README.
3. Review CSVs and PNGs in `outputs/`.
4. Optionally start the frontend to present the same results.

---

## 5. Design Constraints

- Raw data stays out of Git.
- Generated processed tables can be rebuilt from the raw file.
- Clustering uses a fixed `random_state` of 42.
- Business profiles use original-scale averages; K-Means itself uses scaled features.
