# Dataset Documentation — K-Means Customer Segmentation

## 1. Dataset Overview

The project uses the Online Retail Dataset for customer segmentation.

The dataset contains transaction-level records from a UK-based online retail business. Each row is an invoice line with product, quantity, price, customer, date, and country information.

The original file is not customer-level. Transactions were cleaned and aggregated into one row per customer before K-Means.

---

## 2. Dataset Source

**Primary dataset:** Online Retail Dataset

The working copy was obtained from Kaggle. The original source is the UCI Machine Learning Repository.

**Original source:** [https://archive.ics.uci.edu/ml/datasets/online+retail](https://archive.ics.uci.edu/ml/datasets/online+retail)

---

## 3. Dataset File

The downloaded file is:

```text
Online Retail.xlsx
```

It is stored locally in `data/raw/` and is excluded from Git through `.gitignore`.

A representative sample of the **customer-level features used for clustering** is stored in:

```text
data/samples/customer_features_sample.csv
```

---

## 4. Dataset Structure

| Column | Description |
| --- | --- |
| InvoiceNo | Invoice number identifying a transaction |
| StockCode | Product/item code |
| Description | Product description |
| Quantity | Number of units purchased |
| InvoiceDate | Date and time of the transaction |
| UnitPrice | Price per unit |
| CustomerID | Unique customer identifier |
| Country | Customer's country |

---

## 5. Initial Dataset Characteristics

The original dataset contains **541,909** transaction records and 8 columns.

It includes approximately **4,372** unique customer IDs before cleaning. Transaction dates run from December 2010 to December 2011.

The file contains missing values, cancelled transactions, negative quantities, and non-positive unit prices. Those issues were handled during preprocessing.

---

## 6. Data Quality Issues

**Missing Customer IDs.** Records without a CustomerID cannot be assigned to a customer-level segment and were excluded.

**Missing product descriptions.** Clustering uses purchasing behavior, not product text, so missing descriptions did not change the final feature set.

**Cancelled transactions.** Invoices starting with `C` represent cancellations rather than purchases and were excluded.

**Negative quantities.** These records are associated with returns or cancellations and were excluded from the purchase-behavior dataset.

**Non-positive unit prices.** Zero or negative prices do not represent normal purchases and were excluded.

---

## 7. Data Cleaning Results

Cleaning was applied in a fixed order: load the Excel file, inspect structure and types, drop missing CustomerIDs, remove cancelled invoices, keep positive Quantity and UnitPrice, and drop duplicate rows.

| Stage | Count |
| --- | ---: |
| Original transactions | 541,909 |
| Cleaned transactions | 392,692 |
| Customers after aggregation | 4,338 |

Approximately **72.46%** of original transaction records were retained.

---

## 8. Feature Engineering

After cleaning, transactions were aggregated by CustomerID.

The final clustering features are:

| Feature | Definition |
| --- | --- |
| Recency | Days between the last purchase and the day after the latest invoice in the dataset |
| Frequency | Number of unique invoices |
| Monetary | Sum of Quantity × UnitPrice |
| TotalQuantity | Sum of Quantity |
| AverageOrderValue | Monetary / Frequency |
| UniqueProducts | Number of distinct StockCodes |

`CustomerID` is retained as an identifier only.

---

## 9. RFM Analysis

RFM features are the core of the segmentation:

- **Recency** — lower values mean more recent activity.
- **Frequency** — higher values mean more repeated orders.
- **Monetary** — higher values mean greater spend.

TotalQuantity, AverageOrderValue, and UniqueProducts add volume, basket value, and assortment information.

---

## 10. Feature Preprocessing

K-Means is distance-based. Features were inspected for scale and skew, then transformed with `log1p` and standardized with `StandardScaler`. Details are in [docs/methodology.md](methodology.md).

---

## 11. Dataset Sample

The repository sample is:

```text
data/samples/customer_features_sample.csv
```

This file shows the structure of the customer-level data used for clustering without including the full raw Excel file.

---

## 12. Data Validation

Before training, the processed customer table was checked for missing values, invalid numbers, duplicate CustomerIDs, unexpected ranges, and infinite values. One row per customer was required.

---

## 13. Final Dataset for Clustering

The matrix passed to K-Means contains **4,338 rows** (customers) and **6 numeric features**.

```text
CustomerID
    ↓
Customer-level behavioral features
    ↓
log1p + StandardScaler
    ↓
K-Means (k = 3)
```
