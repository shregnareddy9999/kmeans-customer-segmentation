# Customer Segmentation Dashboard

Optional presentation layer for the completed K-Means results. It does not retrain the model.

The app reads static CSVs from `public/data/`:

- `public/data/customer_segments.csv`
- `public/data/k_evaluation_results.csv`

Those files should match the analysis outputs in `../outputs/`.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite (typically `http://localhost:5173`).

## Pages

- **Dashboard** — overall counts and k-evaluation charts
- **Segments** — comparison of the three customer groups
- **Customers** — lookup and inspection of individual customers
- **Insights** — business recommendations

## Note

Task 3 deliverables are the notebook, scripts, PNG plots, and CSV artifacts in the project root. This frontend is an extra demo of the same results.
