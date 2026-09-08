# Cluster Profiles — K-Means Customer Segmentation

## 1. Overview

The final K-Means model uses **k = 3** customer segments.

The segmentation is based on customer-level behavioral features derived
from the Online Retail transaction dataset:

- Recency
- Frequency
- Monetary
- Total Quantity
- Average Order Value
- Unique Products

The profiles below use the **original business-scale feature values**
rather than the standardized values used internally by K-Means.

Supporting tables:

- `outputs/cluster_sizes.csv`
- `outputs/cluster_centroids_original_scale.csv`
- `outputs/cluster_profile.csv`

---

## 2. Final Cluster Summary

| Cluster | Business Segment | Customers | Percentage |
|---|---|---:|---:|
| 0 | At-Risk / Low-Value | 1,221 | 28.15% |
| 1 | High-Value Loyal | 1,188 | 27.39% |
| 2 | Regular / Growth | 1,929 | 44.47% |

---

## 3. Cluster 0 — At-Risk / Low-Value Customers

### Size

- Customers: **1,221**
- Customer share: **28.15%**

### Behavioral Profile

| Feature | Average |
|---|---:|
| Recency | 163.83 days |
| Frequency | 1.39 |
| Monetary | 215.00 |
| Total Quantity | 117.24 |
| Average Order Value | 170.62 |
| Unique Products | 13.71 |

### Interpretation

Cluster 0 represents customers with relatively low purchasing
engagement.

They have the highest average recency among the three clusters,
meaning their most recent purchase occurred considerably earlier.
They also have the lowest purchasing frequency, monetary value,
total quantity, average order value, and product variety.

These characteristics indicate a customer group with relatively
weak recent engagement and low purchasing activity.

### Business Characteristics

- Low purchase frequency
- Low monetary contribution
- Low product variety
- High recency
- Lower average transaction value

---

## 4. Cluster 1 — High-Value Loyal Customers

### Size

- Customers: **1,188**
- Customer share: **27.39%**

### Behavioral Profile

| Feature | Average |
|---|---:|
| Recency | 25.13 days |
| Frequency | 10.28 |
| Monetary | 5,918.11 |
| Total Quantity | 3,423.36 |
| Average Order Value | 679.84 |
| Unique Products | 137.67 |

### Interpretation

Cluster 1 represents the strongest customer segment in the final
segmentation.

These customers have the lowest recency value, indicating that they
purchased most recently. They also have substantially higher
purchasing frequency, monetary value, total quantity, average order
value, and product variety than the other segments.

This combination indicates a highly engaged and commercially valuable
customer group.

### Business Characteristics

- Very recent purchasing activity
- High purchase frequency
- Highest monetary contribution
- Highest total quantity
- Highest average order value
- Highest product variety

---

## 5. Cluster 2 — Regular / Growth Customers

### Size

- Customers: **1,929**
- Customer share: **44.47%**

### Behavioral Profile

| Feature | Average |
|---|---:|
| Recency | 88.92 days |
| Frequency | 2.40 |
| Monetary | 826.33 |
| Total Quantity | 488.29 |
| Average Order Value | 412.53 |
| Unique Products | 44.84 |

### Interpretation

Cluster 2 is the largest customer segment and represents customers
with intermediate purchasing behavior.

Their recency, frequency, monetary value, total quantity, average
order value, and product variety generally fall between Cluster 0
and Cluster 1.

This makes the segment a potential growth group because customers
already demonstrate purchasing activity but do not yet exhibit the
strong engagement characteristics observed in Cluster 1.

### Business Characteristics

- Moderate purchasing activity
- Moderate monetary contribution
- Moderate product variety
- Intermediate recency
- Largest customer population

---

## 6. Comparative Interpretation

The three clusters form a useful behavioral progression:

**Cluster 0 → Cluster 2 → Cluster 1**

From lower to higher overall customer engagement:

- Cluster 0 has the weakest purchasing activity.
- Cluster 2 represents the intermediate customer population.
- Cluster 1 demonstrates the strongest purchasing engagement and
  monetary contribution.

The segmentation therefore provides three distinguishable
customer groups that can support differentiated business strategies.

---

## 7. Model Context

The final model was selected after evaluating k values from 2 through 10
using the Elbow Method and Silhouette Score.

The final k = 3 solution achieved a Silhouette Score of **0.2609**.

Although k = 2 achieved a higher Silhouette Score of **0.3560**, the
three-cluster solution provides a more useful business segmentation
by separating customers into low-value, intermediate, and
high-value behavioral groups.

Higher values of k did not provide sufficient improvement in
silhouette-based separation to justify additional segmentation
complexity.