\# Task Context — K-Means Customer Segmentation



\## 1. Project Overview



This project implements customer segmentation using the K-Means

clustering algorithm.



The objective is to identify groups of customers with similar

purchasing behavior and translate the resulting clusters into

business-oriented customer segments.



The project is developed as a professional machine learning project

with reproducible analysis, documented methodology, generated

artifacts, and an optional interactive dashboard.



\---



\## 2. Internship Task



\*\*Task:\*\* Task 3 — K-Means Customer Segmentation



\### Required Outcomes



The project must satisfy the following requirements:



\- Dataset source must be documented.

\- A sample of the cleaned/used dataset must be included.

\- K-Means clustering must be executed.

\- The selected value of `k` must be documented and justified.

\- The justification must use the Elbow Method, Silhouette Score,

&#x20; or a similar appropriate evaluation approach.

\- Cluster centroids must be provided.

\- Cluster sizes must be provided.

\- Cluster visualizations must be provided.

\- Each cluster must have a concise business-oriented profile.

\- The project must provide 2–3 actionable business recommendations.



\---



\## 3. Required Deliverables



The final project must contain:



1\. GitHub repository

2\. Jupyter notebook and/or Python scripts

3\. Dataset source documentation

4\. Cleaned/used dataset sample

5\. K-Means clustering results

6\. K selection analysis

7\. Cluster plots in PNG format

8\. Cluster centroids in CSV format

9\. Cluster sizes

10\. Cluster profiling summary

11\. 2–3 actionable business recommendations

12\. Project documentation



\---



\## 4. Dataset



\### Selected Dataset



\*\*Online Retail Dataset\*\*



The working dataset was obtained from Kaggle and references the

UCI Machine Learning Repository as its original source.



\### Original Data Type



The dataset contains retail transaction records rather than

customer-level records.



Therefore, customer-level features will be derived from the

transaction data before applying K-Means.



The exact preprocessing decisions and final feature set will be

documented in `docs/dataset.md`.



\---



\## 5. Intended Machine Learning Approach



The project will follow this general pipeline:



Raw transaction data

&#x20;       ↓

Data validation and cleaning

&#x20;       ↓

Transaction filtering

&#x20;       ↓

Customer-level feature engineering

&#x20;       ↓

Exploratory Data Analysis

&#x20;       ↓

Feature preprocessing/scaling

&#x20;       ↓

K selection

&#x20;       ↓

K-Means clustering

&#x20;       ↓

Cluster evaluation

&#x20;       ↓

Cluster interpretation

&#x20;       ↓

Business recommendations



The final value of `k` will be determined from the analysis rather

than being predetermined.



\---



\## 6. Professional Development Goals



The project will follow software-development practices in addition

to machine learning practices.



These include:



\- Version control using Git and GitHub

\- Clear project structure

\- Reproducible Python environment

\- Dependency management

\- Separation of source code and generated outputs

\- Documentation

\- Reusable Python modules where appropriate

\- Clean and meaningful Git commits

\- Final requirement-by-requirement quality check



\---



\## 7. Optional Application Layer



An interactive customer segmentation dashboard may be developed as

an additional project layer.



The dashboard is not a replacement for the required notebook,

analysis, or deliverables.



Its purpose is to present the clustering results in a more

professional and user-friendly manner.



\---



\## 8. Definition of Done



Task 3 will be considered complete only when:



\- The dataset source is documented.

\- The data preparation process is documented.

\- The final customer-level features are explained.

\- K-Means has been executed successfully.

\- The selected `k` has a documented justification.

\- Cluster centroids have been generated.

\- Cluster sizes have been generated.

\- Required visualizations have been generated as PNG files.

\- Each cluster has been profiled.

\- 2–3 actionable recommendations have been documented.

\- Required CSV/PNG artifacts exist.

\- The notebook/script can be reproduced from the documented setup.

\- The GitHub repository is clean and organized.

\- The final project has been checked against every Task 3 requirement.

