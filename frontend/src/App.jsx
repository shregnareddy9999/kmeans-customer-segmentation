import { useEffect, useMemo, useState } from "react";

import {
  BarChart,
  Bar,
  CartesianGrid,
  Cell,
  LineChart,
  Line,
  PieChart,
  Pie,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import "./App.css";

const SEGMENTS = {
  0: {
    name: "At-Risk / Low-Value",
    short: "At-Risk",
    color: "#ef4444",
    icon: "↻",
    description:
      "Customers with low purchasing frequency and value who have not purchased recently.",
  },
  1: {
    name: "High-Value Loyal",
    short: "High-Value",
    color: "#10b981",
    icon: "◆",
    description:
      "Highly engaged customers with strong purchasing frequency, high spending, and broad product activity.",
  },
  2: {
    name: "Regular / Growth",
    short: "Growth",
    color: "#3b82f6",
    icon: "↗",
    description:
      "Moderately active customers with potential to increase purchase frequency and customer value.",
  },
};

const FEATURES = [
  "Recency",
  "Frequency",
  "Monetary",
  "TotalQuantity",
  "AverageOrderValue",
  "UniqueProducts",
];

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);

  if (!lines.length || !lines[0]) return [];

  const headers = lines[0]
    .split(",")
    .map((header) => header.trim().replace(/^"|"$/g, ""));

  return lines.slice(1).map((line) => {
    const values = line.split(",");
    const row = {};

    headers.forEach((header, index) => {
      const value = values[index]
        ?.trim()
        .replace(/^"|"$/g, "");

      const numericColumns = [
        "CustomerID",
        "Cluster",
        "Recency",
        "Frequency",
        "Monetary",
        "TotalQuantity",
        "AverageOrderValue",
        "UniqueProducts",
        "k",
        "inertia",
        "silhouette",
        "Silhouette Score",
        "Silhouette",
        "PC1",
        "PC2",
        "PC1Variance",
        "PC2Variance",
      ];

      if (numericColumns.includes(header)) {
        row[header] = Number(value);
      } else {
        row[header] = value;
      }
    });

    return row;
  });
}

function formatMoney(value) {
  return `£${Number(value || 0).toLocaleString("en-GB", {
    maximumFractionDigits: 0,
  })}`;
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString("en-GB", {
    maximumFractionDigits: 2,
  });
}

function sampleClusterPoints(points, maxPoints = 460) {
  if (points.length <= maxPoints) {
    return points;
  }

  const sampled = [];
  const step = points.length / maxPoints;

  for (let index = 0; index < maxPoints; index += 1) {
    sampled.push(points[Math.floor(index * step)]);
  }

  return sampled;
}

function ClusterMapTooltip({ active, payload, showPcaMap }) {
  if (!active || !payload?.length) {
    return null;
  }

  const point = payload[0].payload;
  const meta = SEGMENTS[point.cluster];

  if (!meta) {
    return null;
  }

  return (
    <div className="cluster-map-tooltip">
      <div
        className="cluster-map-tooltip-kicker"
        style={{ color: meta.color }}
      >
        {point.isCentroid ? "Cluster centroid" : "Customer"}
      </div>
      <strong>{meta.name}</strong>
      {!point.isCentroid && (
        <span>ID {point.customerId}</span>
      )}
      {showPcaMap ? (
        <>
          <span>PC1 {Number(point.x).toFixed(2)}</span>
          <span>PC2 {Number(point.y).toFixed(2)}</span>
        </>
      ) : (
        <>
          <span>
            Recency {Number(point.recency ?? point.x).toFixed(1)} days
          </span>
          <span>
            Monetary {formatMoney(point.monetary ?? point.y)}
          </span>
        </>
      )}
    </div>
  );
}

function renderClusterDot(props) {
  const { cx, cy, payload } = props;

  if (
    !Number.isFinite(cx) ||
    !Number.isFinite(cy) ||
    payload == null
  ) {
    return null;
  }

  const color = SEGMENTS[pointCluster(payload)].color;

  if (payload.isCentroid) {
    return (
      <g>
        <circle
          cx={cx}
          cy={cy}
          r={14}
          fill={color}
          opacity={0.16}
        />
        <circle
          cx={cx}
          cy={cy}
          r={7}
          fill={color}
          stroke="#ffffff"
          strokeWidth={2.4}
        />
      </g>
    );
  }

  return (
    <circle
      cx={cx}
      cy={cy}
      r={3.6}
      fill={color}
      fillOpacity={0.82}
      stroke="#ffffff"
      strokeWidth={0.7}
    />
  );
}

function pointCluster(payload) {
  return Number(payload.cluster);
}

function App() {
  const [customers, setCustomers] = useState([]);
  const [kResults, setKResults] = useState([]);
  const [pcaPoints, setPcaPoints] = useState([]);
  const [page, setPage] = useState("dashboard");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedFeature, setSelectedFeature] = useState("Recency");
  const [searchId, setSearchId] = useState("");
  const [clusterMapView, setClusterMapView] = useState("pca");

  useEffect(() => {
    async function loadData() {
      try {
        const customerResponse = await fetch(
          "/data/customer_segments.csv"
        );

        const kResponse = await fetch(
          "/data/k_evaluation_results.csv"
        );

        const pcaResponse = await fetch(
          "/data/customer_clusters_pca.csv"
        );

        if (!customerResponse.ok) {
          throw new Error(
            "customer_segments.csv could not be loaded."
          );
        }

        const customerText = await customerResponse.text();
        const customerData = parseCSV(customerText);

        setCustomers(customerData);

        if (kResponse.ok) {
          const kText = await kResponse.text();
          setKResults(parseCSV(kText));
        }

        if (pcaResponse.ok) {
          const pcaText = await pcaResponse.text();
          setPcaPoints(parseCSV(pcaText));
        }

        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const finalKResult = useMemo(() => {
    return kResults.find((row) => Number(row.k) === 3);
  }, [kResults]);

  const silhouette = finalKResult
    ? Number(
        finalKResult.silhouette ??
          finalKResult["Silhouette Score"] ??
          finalKResult.Silhouette ??
          0.2609
      )
    : 0.2609;

  const totalCustomers = customers.length;

  const clusterStats = useMemo(() => {
    return [0, 1, 2].map((cluster) => {
      const rows = customers.filter(
        (customer) => Number(customer.Cluster) === cluster
      );

      const count = rows.length;
      const averages = {};

      FEATURES.forEach((feature) => {
        averages[feature] =
          rows.length > 0
            ? rows.reduce(
                (sum, row) =>
                  sum + Number(row[feature] || 0),
                0
              ) / rows.length
            : 0;
      });

      return {
        cluster,
        count,
        percentage:
          totalCustomers > 0
            ? (count / totalCustomers) * 100
            : 0,
        ...averages,
      };
    });
  }, [customers, totalCustomers]);

  const distributionData = clusterStats.map((item) => ({
    name: SEGMENTS[item.cluster].short,
    fullName: SEGMENTS[item.cluster].name,
    customers: item.count,
    percentage: item.percentage,
    cluster: item.cluster,
  }));

  const featureData = clusterStats.map((item) => ({
    name: SEGMENTS[item.cluster].short,
    value: item[selectedFeature],
    cluster: item.cluster,
  }));

  const selectedCustomer = useMemo(() => {
    if (!searchId) return null;

    return customers.find(
      (customer) =>
        String(customer.CustomerID) === String(searchId)
    );
  }, [customers, searchId]);

  const kChartData = useMemo(() => {
    return kResults
      .map((row) => ({
        k: Number(row.k),
        inertia: Number(row.inertia || 0),
        silhouette: Number(
          row.silhouette ??
            row["Silhouette Score"] ??
            row.Silhouette ??
            0
        ),
      }))
      .filter((row) => Number.isFinite(row.k))
      .sort((a, b) => a.k - b.k);
  }, [kResults]);

  const pcaVariance = useMemo(() => {
    const row = pcaPoints[0];

    if (!row) {
      return { pc1: 65.8, pc2: 17.4 };
    }

    return {
      pc1: Number(row.PC1Variance || 0) * 100,
      pc2: Number(row.PC2Variance || 0) * 100,
    };
  }, [pcaPoints]);

  const clusterMapSeries = useMemo(() => {
    const buildSeries = (cluster, points) => {
      const valid = points.filter(
        (point) =>
          Number.isFinite(point.x) &&
          Number.isFinite(point.y)
      );

      const centroid =
        valid.length > 0
          ? {
              x:
                valid.reduce((sum, point) => sum + point.x, 0) /
                valid.length,
              y:
                valid.reduce((sum, point) => sum + point.y, 0) /
                valid.length,
              cluster,
              isCentroid: true,
            }
          : null;

      return {
        cluster,
        points: sampleClusterPoints(valid),
        centroid,
        total: valid.length,
      };
    };

    if (clusterMapView === "pca" && pcaPoints.length) {
      return [0, 1, 2].map((cluster) =>
        buildSeries(
          cluster,
          pcaPoints
            .filter((row) => Number(row.Cluster) === cluster)
            .map((row) => ({
              x: Number(row.PC1),
              y: Number(row.PC2),
              cluster,
              customerId: row.CustomerID,
            }))
        )
      );
    }

    return [0, 1, 2].map((cluster) =>
      buildSeries(
        cluster,
        customers
          .filter((row) => Number(row.Cluster) === cluster)
          .map((row) => {
            const recency = Number(row.Recency);
            const monetary = Number(row.Monetary);

            return {
              x: recency,
              y: Math.log1p(Math.max(monetary, 0)),
              recency,
              monetary,
              cluster,
              customerId: row.CustomerID,
            };
          })
      )
    );
  }, [clusterMapView, pcaPoints, customers]);

  const showPcaMap =
    clusterMapView === "pca" && pcaPoints.length > 0;

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-logo">◆</div>
        <div className="loading-title">CustomerIQ</div>
        <div className="loading-text">
          Loading segmentation results...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-screen">
        <div className="error-card">
          <div className="error-icon">!</div>

          <h2>Unable to load dashboard</h2>

          <p>{error}</p>

          <p>
            Make sure the CSV files exist inside{" "}
            <code>frontend/public/data/</code>.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">

      {/* ================= SIDEBAR ================= */}

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">◆</div>

          <div>
            <div className="brand-name">CustomerIQ</div>

            <div className="brand-subtitle">
              Customer Analytics
            </div>
          </div>
        </div>

        <nav className="navigation">

          <div className="nav-label">WORKSPACE</div>

          <button
            className={
              page === "dashboard"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setPage("dashboard")}
          >
            <span>▦</span>
            Dashboard
          </button>

          <button
            className={
              page === "segments"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setPage("segments")}
          >
            <span>◈</span>
            Segments
          </button>

          <button
            className={
              page === "customers"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setPage("customers")}
          >
            <span>◎</span>
            Customer Explorer
          </button>

          <button
            className={
              page === "insights"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setPage("insights")}
          >
            <span>✦</span>
            Business Insights
          </button>

          <div className="nav-label model-label">
            MODEL
          </div>

          <div className="model-card">

            <div className="model-card-top">
              <span className="status-dot"></span>
              Model Active
            </div>

            <div className="model-name">
              K-Means
            </div>

            <div className="model-detail">
              3 customer segments
            </div>

            <div className="model-detail">
              6 behavioral features
            </div>

          </div>
        </nav>

        <div className="sidebar-footer">
          <div>Task 3 · AVIP 2026</div>
          <div>Customer Segmentation</div>
        </div>

      </aside>

      {/* ================= MAIN ================= */}

      <main className="main-content">

        <header className="topbar">

          <div className="breadcrumb">
            Analytics
            <span>/</span>

            {page === "dashboard"
              ? "Dashboard"
              : page === "segments"
              ? "Segments"
              : page === "customers"
              ? "Customer Explorer"
              : "Business Insights"}
          </div>

          <div className="topbar-right">

            <div className="live-status">
              <span className="status-dot"></span>
              Analysis Ready
            </div>

            <div className="avatar">ML</div>

          </div>

        </header>

        {/* =====================================================
            DASHBOARD
        ===================================================== */}

        {page === "dashboard" && (
          <section className="page">

            <div className="page-header">

              <div>
                <div className="eyebrow">
                  CUSTOMER INTELLIGENCE
                </div>

                <h1>Customer Segmentation</h1>

                <p>
                  Understand customer behavior, identify
                  valuable segments, and turn data into
                  actionable business decisions.
                </p>
              </div>

              <div className="header-badge">
                <span>●</span>
                K-Means · k = 3
              </div>

            </div>

            {/* ================= KPI GRID ================= */}

            <div className="kpi-grid">

              <div className="kpi-card">

                <div className="kpi-top">
                  <span>Total Customers</span>

                  <div className="kpi-icon blue">
                    ◎
                  </div>
                </div>

                <div className="kpi-value">
                  {totalCustomers.toLocaleString()}
                </div>

                <div className="kpi-caption">
                  Customers analyzed
                </div>

              </div>

              <div className="kpi-card">

                <div className="kpi-top">
                  <span>Customer Segments</span>

                  <div className="kpi-icon purple">
                    ◈
                  </div>
                </div>

                <div className="kpi-value">3</div>

                <div className="kpi-caption">
                  Behavioral groups identified
                </div>

              </div>

              <div className="kpi-card">

                <div className="kpi-top">
                  <span>Silhouette Score</span>

                  <div className="kpi-icon green">
                    ✓
                  </div>
                </div>

                <div className="kpi-value">
                  {silhouette.toFixed(3)}
                </div>

                <div className="kpi-caption">
                  Final clustering evaluation
                </div>

              </div>

              <div className="kpi-card">

                <div className="kpi-top">
                  <span>Algorithm</span>

                  <div className="kpi-icon orange">
                    AI
                  </div>
                </div>

                <div className="kpi-value algorithm">
                  K-Means
                </div>

                <div className="kpi-caption">
                  Unsupervised learning
                </div>

              </div>

            </div>

            {/* =================================================
                ML EVIDENCE SECTION
            ================================================= */}

            <div className="section-heading ml-section-heading">

              <div>
                <div className="eyebrow">
                  MODEL TRANSPARENCY
                </div>

                <h2>
                  ML Pipeline & Model Evidence
                </h2>

                <p>
                  The complete journey from the original
                  Online Retail transactions to the final
                  customer segments.
                </p>
              </div>

              <div className="model-proof-badge">
                ✓ Trained on real transaction data
              </div>

            </div>

            {/* ================= DATASET EVIDENCE ================= */}

            <div className="evidence-grid">

              <div className="evidence-card">
                <span className="evidence-number">
                  541,909
                </span>

                <strong>
                  Raw transactions
                </strong>

                <p>
                  Original Online Retail dataset
                  records.
                </p>
              </div>

              <div className="evidence-card">
                <span className="evidence-number">
                  392,692
                </span>

                <strong>
                  Valid transactions
                </strong>

                <p>
                  Records retained after data cleaning.
                </p>
              </div>

              <div className="evidence-card">
                <span className="evidence-number">
                  4,338
                </span>

                <strong>
                  Customers
                </strong>

                <p>
                  Customer-level profiles generated
                  from transactions.
                </p>
              </div>

              <div className="evidence-card">
                <span className="evidence-number">
                  6
                </span>

                <strong>
                  Behavioral features
                </strong>

                <p>
                  Recency, Frequency, Monetary,
                  Quantity, AOV and Products.
                </p>
              </div>

            </div>

            {/* ================= PIPELINE ================= */}

            <div className="panel ml-pipeline-panel">

              <div className="panel-header">

                <div>
                  <h2>
                    Training Pipeline
                  </h2>

                  <p>
                    Reproducible machine-learning workflow
                    used for the final segmentation.
                  </p>
                </div>

                <div className="panel-chip">
                  K-Means
                </div>

              </div>

              <div className="pipeline">

                <div className="pipeline-step">
                  <div className="pipeline-icon">
                    01
                  </div>

                  <strong>
                    Online Retail Data
                  </strong>

                  <span>
                    541,909 transactions
                  </span>
                </div>

                <div className="pipeline-arrow">
                  →
                </div>

                <div className="pipeline-step">
                  <div className="pipeline-icon">
                    02
                  </div>

                  <strong>
                    Data Cleaning
                  </strong>

                  <span>
                    392,692 valid records
                  </span>
                </div>

                <div className="pipeline-arrow">
                  →
                </div>

                <div className="pipeline-step">
                  <div className="pipeline-icon">
                    03
                  </div>

                  <strong>
                    Feature Engineering
                  </strong>

                  <span>
                    4,338 customer profiles
                  </span>
                </div>

                <div className="pipeline-arrow">
                  →
                </div>

                <div className="pipeline-step">
                  <div className="pipeline-icon">
                    04
                  </div>

                  <strong>
                    Preprocessing
                  </strong>

                  <span>
                    Log1p + StandardScaler
                  </span>
                </div>

                <div className="pipeline-arrow">
                  →
                </div>

                <div className="pipeline-step">
                  <div className="pipeline-icon">
                    05
                  </div>

                  <strong>
                    K-Means Evaluation
                  </strong>

                  <span>
                    K = 2 through 10
                  </span>
                </div>

                <div className="pipeline-arrow">
                  →
                </div>

                <div className="pipeline-step final">
                  <div className="pipeline-icon">
                    06
                  </div>

                  <strong>
                    Final Model
                  </strong>

                  <span>
                    K = 3 · 0.2609 silhouette
                  </span>
                </div>

              </div>

            </div>

            {/* ================= MODEL SELECTION ================= */}

            <div className="chart-grid">

              <div className="panel large-panel">

                <div className="panel-header">

                  <div>
                    <h2>
                      K Selection — Silhouette Analysis
                    </h2>

                    <p>
                      Actual evaluation results for
                      candidate K values from 2 to 10.
                    </p>
                  </div>

                  <div className="panel-chip">
                    Higher is better
                  </div>

                </div>

                <div className="chart-container">

                  <ResponsiveContainer
                    width="100%"
                    height={320}
                  >
                    <LineChart data={kChartData}>

                      <CartesianGrid
                        strokeDasharray="3 3"
                        vertical={false}
                        stroke="#e2e8f0"
                      />

                      <XAxis
                        dataKey="k"
                        axisLine={false}
                        tickLine={false}
                        label={{
                          value: "Number of clusters (K)",
                          position: "insideBottom",
                          offset: -5,
                        }}
                      />

                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        domain={[0, 0.4]}
                      />

                      <Tooltip />

                      <Line
                        type="monotone"
                        dataKey="silhouette"
                        name="Silhouette Score"
                        stroke="#3b82f6"
                        strokeWidth={3}
                        dot={{
                          r: 5,
                        }}
                        activeDot={{
                          r: 7,
                        }}
                      />

                    </LineChart>
                  </ResponsiveContainer>

                </div>

              </div>

              <div className="panel">

                <div className="panel-header">

                  <div>
                    <h2>
                      Final Model
                    </h2>

                    <p>
                      Selected configuration
                    </p>
                  </div>

                </div>

                <div className="model-proof">

                  <div className="proof-row">
                    <span>Algorithm</span>
                    <strong>K-Means</strong>
                  </div>

                  <div className="proof-row">
                    <span>Selected K</span>
                    <strong>3</strong>
                  </div>

                  <div className="proof-row">
                    <span>Features</span>
                    <strong>6</strong>
                  </div>

                  <div className="proof-row">
                    <span>Silhouette</span>
                    <strong>
                      {silhouette.toFixed(4)}
                    </strong>
                  </div>

                  <div className="proof-row">
                    <span>Clusters</span>
                    <strong>3</strong>
                  </div>

                  <div className="proof-row">
                    <span>Model status</span>
                    <strong className="success-text">
                      Trained ✓
                    </strong>
                  </div>

                </div>

              </div>

            </div>

            {/* ================= SEGMENT DISTRIBUTION ================= */}

            <div className="chart-grid">

              <div className="panel large-panel">

                <div className="panel-header">

                  <div>
                    <h2>
                      Segment Distribution
                    </h2>

                    <p>
                      How customers are distributed
                      across behavioral groups.
                    </p>
                  </div>

                  <div className="panel-chip">
                    {totalCustomers.toLocaleString()} customers
                  </div>

                </div>

                <div className="chart-container">

                  <ResponsiveContainer
                    width="100%"
                    height={310}
                  >
                    <BarChart data={distributionData}>

                      <CartesianGrid
                        strokeDasharray="3 3"
                        vertical={false}
                        stroke="#e2e8f0"
                      />

                      <XAxis
                        dataKey="name"
                        axisLine={false}
                        tickLine={false}
                      />

                      <YAxis
                        axisLine={false}
                        tickLine={false}
                      />

                      <Tooltip />

                      <Bar
                        dataKey="customers"
                        radius={[8, 8, 0, 0]}
                      >
                        {distributionData.map(
                          (entry) => (
                            <Cell
                              key={entry.cluster}
                              fill={
                                SEGMENTS[
                                  entry.cluster
                                ].color
                              }
                            />
                          )
                        )}
                      </Bar>

                    </BarChart>
                  </ResponsiveContainer>

                </div>

              </div>

              <div className="panel">

                <div className="panel-header">

                  <div>
                    <h2>
                      Customer Mix
                    </h2>

                    <p>
                      Segment share
                    </p>
                  </div>

                </div>

                <div className="donut-wrapper">

                  <ResponsiveContainer
                    width="100%"
                    height={245}
                  >
                    <PieChart>

                      <Pie
                        data={distributionData}
                        dataKey="customers"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        innerRadius={65}
                        outerRadius={95}
                        paddingAngle={3}
                      >
                        {distributionData.map(
                          (entry) => (
                            <Cell
                              key={entry.cluster}
                              fill={
                                SEGMENTS[
                                  entry.cluster
                                ].color
                              }
                            />
                          )
                        )}
                      </Pie>

                      <Tooltip />

                    </PieChart>
                  </ResponsiveContainer>

                  <div className="donut-center">
                    <strong>
                      {totalCustomers.toLocaleString()}
                    </strong>

                    <span>Customers</span>
                  </div>

                </div>

                <div className="legend-list">

                  {distributionData.map(
                    (item) => (
                      <div
                        className="legend-item"
                        key={item.cluster}
                      >

                        <div className="legend-left">

                          <span
                            className="legend-dot"
                            style={{
                              background:
                                SEGMENTS[
                                  item.cluster
                                ].color,
                            }}
                          />

                          <span>
                            {item.fullName}
                          </span>

                        </div>

                        <strong>
                          {item.percentage.toFixed(1)}%
                        </strong>

                      </div>
                    )
                  )}

                </div>

              </div>

            </div>

            {/* ================= SEGMENT CARDS ================= */}

            <div className="section-heading">

              <div>
                <h2>
                  Customer Segments
                </h2>

                <p>
                  Behavioral profiles identified by
                  the clustering model.
                </p>
              </div>

              <button
                className="text-button"
                onClick={() => setPage("segments")}
              >
                View detailed analysis →
              </button>

            </div>

            <div className="segment-grid">

              {clusterStats.map((segment) => {

                const meta =
                  SEGMENTS[segment.cluster];

                return (
                  <div
                    className="segment-card"
                    key={segment.cluster}
                  >

                    <div className="segment-card-top">

                      <div
                        className="segment-icon"
                        style={{
                          color: meta.color,
                          background: `${meta.color}15`,
                        }}
                      >
                        {meta.icon}
                      </div>

                      <span className="segment-number">
                        0{segment.cluster + 1}
                      </span>

                    </div>

                    <h3>{meta.name}</h3>

                    <div className="segment-count">
                      {segment.count.toLocaleString()}
                      <span> customers</span>
                    </div>

                    <div className="progress-track">

                      <div
                        className="progress-fill"
                        style={{
                          width: `${segment.percentage}%`,
                          background: meta.color,
                        }}
                      />

                    </div>

                    <div className="segment-meta">
                      <span>
                        {segment.percentage.toFixed(2)}%
                        of customer base
                      </span>
                    </div>

                    <p>
                      {meta.description}
                    </p>

                  </div>
                );
              })}

            </div>

          </section>
        )}

        {/* =====================================================
            SEGMENTS
        ===================================================== */}

        {page === "segments" && (
          <section className="page">

            <div className="page-header">

              <div>

                <div className="eyebrow">
                  SEGMENT ANALYSIS
                </div>

                <h1>
                  Behavioral Segments
                </h1>

                <p>
                  Compare the characteristics of each
                  customer group identified by K-Means.
                </p>

              </div>

            </div>

            <div className="segment-grid">

              {clusterStats.map((segment) => {

                const meta =
                  SEGMENTS[segment.cluster];

                return (
                  <div
                    className="profile-card"
                    key={segment.cluster}
                  >

                    <div className="profile-header">

                      <div
                        className="profile-icon"
                        style={{
                          background: `${meta.color}15`,
                          color: meta.color,
                        }}
                      >
                        {meta.icon}
                      </div>

                      <div>

                        <h3>
                          {meta.name}
                        </h3>

                        <span>
                          Cluster {segment.cluster}
                        </span>

                      </div>

                    </div>

                    <div className="profile-main-number">
                      {segment.count.toLocaleString()}
                      <span> customers</span>
                    </div>

                    <div className="profile-stat-grid">

                      <div>
                        <span>Recency</span>
                        <strong>
                          {segment.Recency.toFixed(1)}
                        </strong>
                      </div>

                      <div>
                        <span>Frequency</span>
                        <strong>
                          {segment.Frequency.toFixed(1)}
                        </strong>
                      </div>

                      <div>
                        <span>Monetary</span>
                        <strong>
                          {formatMoney(
                            segment.Monetary
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>AOV</span>
                        <strong>
                          {formatMoney(
                            segment.AverageOrderValue
                          )}
                        </strong>
                      </div>

                    </div>

                  </div>
                );
              })}

            </div>

            <div className="panel cluster-map-panel">

              <div className="panel-header">

                <div>
                  <h2>
                    Customer Cluster Map
                  </h2>

                  <p>
                    {showPcaMap
                      ? `Same 2D PCA view as the analysis. The six scaled K-Means features are projected here (PC1 ${pcaVariance.pc1.toFixed(1)}%, PC2 ${pcaVariance.pc2.toFixed(1)}%).`
                      : "Recency against log spending, colored with the final K-Means labels. Log scale keeps high-value outliers from hiding the rest of the base."}
                  </p>
                </div>

                <div className="cluster-map-toggle">

                  <button
                    type="button"
                    className={
                      clusterMapView === "pca"
                        ? "map-toggle active"
                        : "map-toggle"
                    }
                    onClick={() =>
                      setClusterMapView("pca")
                    }
                    disabled={!pcaPoints.length}
                  >
                    PCA map
                  </button>

                  <button
                    type="button"
                    className={
                      clusterMapView === "rfm"
                        ? "map-toggle active"
                        : "map-toggle"
                    }
                    onClick={() =>
                      setClusterMapView("rfm")
                    }
                  >
                    Recency vs spend
                  </button>

                </div>

              </div>

              <div className="cluster-map-legend">
                {[0, 1, 2].map((cluster) => (
                  <span
                    key={cluster}
                    className="cluster-map-legend-item"
                  >
                    <span
                      className="cluster-map-swatch"
                      style={{
                        background:
                          SEGMENTS[cluster].color,
                      }}
                    />
                    <span>
                      {SEGMENTS[cluster].name}
                      <em>
                        {(
                          clusterMapSeries[cluster]
                            ?.total || 0
                        ).toLocaleString()}{" "}
                        customers
                      </em>
                    </span>
                  </span>
                ))}
                <span className="cluster-map-legend-item muted">
                  <span className="cluster-map-centroid-mark" />
                  Centroid
                </span>
              </div>

              <div className="cluster-map-canvas">

                <ResponsiveContainer
                  width="100%"
                  height={460}
                >
                  <ScatterChart
                    margin={{
                      top: 18,
                      right: 22,
                      bottom: 28,
                      left: 12,
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#e2e8f0"
                      vertical
                      horizontal
                    />

                    {showPcaMap && (
                      <>
                        <ReferenceLine
                          x={0}
                          stroke="#cbd5e1"
                          strokeDasharray="4 4"
                        />
                        <ReferenceLine
                          y={0}
                          stroke="#cbd5e1"
                          strokeDasharray="4 4"
                        />
                      </>
                    )}

                    <XAxis
                      type="number"
                      dataKey="x"
                      name={
                        showPcaMap
                          ? "PC1"
                          : "Recency"
                      }
                      axisLine={false}
                      tickLine={false}
                      tick={{
                        fontSize: 11,
                        fill: "#64748b",
                      }}
                      tickMargin={8}
                      label={{
                        value: showPcaMap
                          ? `PC1 (${pcaVariance.pc1.toFixed(1)}% variance)`
                          : "Recency (days since last purchase)",
                        position: "insideBottom",
                        offset: -18,
                        fontSize: 12,
                        fill: "#475569",
                      }}
                    />

                    <YAxis
                      type="number"
                      dataKey="y"
                      name={
                        showPcaMap
                          ? "PC2"
                          : "Monetary"
                      }
                      axisLine={false}
                      tickLine={false}
                      tick={{
                        fontSize: 11,
                        fill: "#64748b",
                      }}
                      tickFormatter={
                        showPcaMap
                          ? (value) =>
                              Number(value).toFixed(1)
                          : (value) =>
                              formatMoney(Math.expm1(value))
                      }
                      width={72}
                      label={{
                        value: showPcaMap
                          ? `PC2 (${pcaVariance.pc2.toFixed(1)}% variance)`
                          : "Monetary value",
                        angle: -90,
                        position: "insideLeft",
                        offset: 4,
                        fontSize: 12,
                        fill: "#475569",
                      }}
                    />

                    <Tooltip
                      cursor={{
                        stroke: "#94a3b8",
                        strokeDasharray: "4 4",
                      }}
                      content={
                        <ClusterMapTooltip
                          showPcaMap={showPcaMap}
                        />
                      }
                    />

                    {clusterMapSeries.map((series) => (
                      <Scatter
                        key={`points-${series.cluster}`}
                        name={
                          SEGMENTS[series.cluster].name
                        }
                        data={series.points}
                        fill={
                          SEGMENTS[series.cluster].color
                        }
                        shape={renderClusterDot}
                        isAnimationActive={false}
                        legendType="none"
                      />
                    ))}

                    {clusterMapSeries
                      .filter((series) => series.centroid)
                      .map((series) => (
                        <Scatter
                          key={`centroid-${series.cluster}`}
                          name={`${SEGMENTS[series.cluster].short} centroid`}
                          data={[series.centroid]}
                          fill={
                            SEGMENTS[series.cluster].color
                          }
                          shape={renderClusterDot}
                          isAnimationActive={false}
                          legendType="none"
                        />
                      ))}

                  </ScatterChart>
                </ResponsiveContainer>

              </div>

            </div>

            <div className="panel">

              <div className="panel-header">

                <div>
                  <h2>
                    Behavioral Comparison
                  </h2>

                  <p>
                    Compare average feature values
                    across customer segments.
                  </p>
                </div>

                <select
                  className="feature-select"
                  value={selectedFeature}
                  onChange={(event) =>
                    setSelectedFeature(
                      event.target.value
                    )
                  }
                >
                  {FEATURES.map((feature) => (
                    <option
                      value={feature}
                      key={feature}
                    >
                      {feature.replace(
                        /([A-Z])/g,
                        " $1"
                      )}
                    </option>
                  ))}
                </select>

              </div>

              <div className="chart-container">

                <ResponsiveContainer
                  width="100%"
                  height={360}
                >
                  <BarChart data={featureData}>

                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                      stroke="#e2e8f0"
                    />

                    <XAxis
                      dataKey="name"
                      axisLine={false}
                      tickLine={false}
                    />

                    <YAxis
                      axisLine={false}
                      tickLine={false}
                    />

                    <Tooltip />

                    <Bar
                      dataKey="value"
                      radius={[8, 8, 0, 0]}
                    >
                      {featureData.map(
                        (entry) => (
                          <Cell
                            key={entry.cluster}
                            fill={
                              SEGMENTS[
                                entry.cluster
                              ].color
                            }
                          />
                        )
                      )}
                    </Bar>

                  </BarChart>
                </ResponsiveContainer>

              </div>

            </div>

            <div className="panel">

              <div className="panel-header">

                <div>
                  <h2>
                    Complete Cluster Profile
                  </h2>

                  <p>
                    Original-scale behavioral metrics.
                  </p>
                </div>

              </div>

              <div className="table-wrapper">

                <table>

                  <thead>
                    <tr>
                      <th>Segment</th>
                      <th>Customers</th>
                      <th>Recency</th>
                      <th>Frequency</th>
                      <th>Monetary</th>
                      <th>Total Quantity</th>
                      <th>AOV</th>
                      <th>Products</th>
                    </tr>
                  </thead>

                  <tbody>

                    {clusterStats.map(
                      (segment) => (
                        <tr
                          key={segment.cluster}
                        >

                          <td>
                            <span className="table-segment">

                              <span
                                className="table-dot"
                                style={{
                                  background:
                                    SEGMENTS[
                                      segment.cluster
                                    ].color,
                                }}
                              />

                              {
                                SEGMENTS[
                                  segment.cluster
                                ].name
                              }

                            </span>
                          </td>

                          <td>
                            {segment.count.toLocaleString()}
                          </td>

                          <td>
                            {segment.Recency.toFixed(2)}
                          </td>

                          <td>
                            {segment.Frequency.toFixed(2)}
                          </td>

                          <td>
                            {formatMoney(
                              segment.Monetary
                            )}
                          </td>

                          <td>
                            {formatNumber(
                              segment.TotalQuantity
                            )}
                          </td>

                          <td>
                            {formatMoney(
                              segment.AverageOrderValue
                            )}
                          </td>

                          <td>
                            {formatNumber(
                              segment.UniqueProducts
                            )}
                          </td>

                        </tr>
                      )
                    )}

                  </tbody>

                </table>

              </div>

            </div>

          </section>
        )}

        {/* =====================================================
            CUSTOMER EXPLORER
        ===================================================== */}

        {page === "customers" && (
          <section className="page">

            <div className="page-header">

              <div>

                <div className="eyebrow">
                  CUSTOMER EXPLORER
                </div>

                <h1>
                  Explore a Customer
                </h1>

                <p>
                  Search the analyzed customer base and
                  inspect individual behavioral profiles.
                </p>

              </div>

            </div>

            <div className="search-panel">

              <div>

                <label>
                  Customer ID
                </label>

                <input
                  type="number"
                  placeholder="e.g. 17850"
                  value={searchId}
                  onChange={(event) =>
                    setSearchId(
                      event.target.value
                    )
                  }
                />

              </div>

              <button
                className="primary-button"
                onClick={() => {
                  if (!searchId) return;

                  setSearchId(
                    String(searchId)
                  );
                }}
              >
                Search Customer
              </button>

            </div>

            {selectedCustomer ? (
              <div>

                <div
                  className="customer-hero"
                  style={{
                    "--customer-color":
                      SEGMENTS[
                        selectedCustomer.Cluster
                      ].color,
                  }}
                >

                  <div>

                    <div className="eyebrow light">
                      CUSTOMER PROFILE
                    </div>

                    <h2>
                      Customer #
                      {selectedCustomer.CustomerID}
                    </h2>

                    <p>
                      Assigned segment
                    </p>

                  </div>

                  <div className="customer-segment-badge">
                    {
                      SEGMENTS[
                        selectedCustomer.Cluster
                      ].name
                    }
                  </div>

                </div>

                <div className="customer-metric-grid">

                  <div className="customer-metric">
                    <span>Recency</span>

                    <strong>
                      {selectedCustomer.Recency.toFixed(
                        0
                      )}
                      <small> days</small>
                    </strong>

                    <p>
                      Days since last purchase
                    </p>
                  </div>

                  <div className="customer-metric">
                    <span>Frequency</span>

                    <strong>
                      {selectedCustomer.Frequency.toFixed(
                        0
                      )}
                    </strong>

                    <p>
                      Purchase frequency
                    </p>
                  </div>

                  <div className="customer-metric">
                    <span>Monetary Value</span>

                    <strong>
                      {formatMoney(
                        selectedCustomer.Monetary
                      )}
                    </strong>

                    <p>
                      Total customer spend
                    </p>
                  </div>

                  <div className="customer-metric">
                    <span>Average Order</span>

                    <strong>
                      {formatMoney(
                        selectedCustomer.AverageOrderValue
                      )}
                    </strong>

                    <p>
                      Average order value
                    </p>
                  </div>

                  <div className="customer-metric">
                    <span>Total Quantity</span>

                    <strong>
                      {formatNumber(
                        selectedCustomer.TotalQuantity
                      )}
                    </strong>

                    <p>
                      Products purchased
                    </p>
                  </div>

                  <div className="customer-metric">
                    <span>Unique Products</span>

                    <strong>
                      {formatNumber(
                        selectedCustomer.UniqueProducts
                      )}
                    </strong>

                    <p>
                      Product diversity
                    </p>
                  </div>

                </div>

                <div className="panel">

                  <div className="panel-header">

                    <div>
                      <h2>
                        Customer Interpretation
                      </h2>

                      <p>
                        Model-based behavioral assessment.
                      </p>
                    </div>

                  </div>

                  <div className="interpretation">

                    <div
                      className="interpretation-icon"
                      style={{
                        color:
                          SEGMENTS[
                            selectedCustomer.Cluster
                          ].color,

                        background:
                          `${SEGMENTS[
                            selectedCustomer.Cluster
                          ].color}15`,
                      }}
                    >
                      {
                        SEGMENTS[
                          selectedCustomer.Cluster
                        ].icon
                      }
                    </div>

                    <div>

                      <h3>
                        {
                          SEGMENTS[
                            selectedCustomer.Cluster
                          ].name
                        }
                      </h3>

                      <p>
                        {
                          SEGMENTS[
                            selectedCustomer.Cluster
                          ].description
                        }
                      </p>

                    </div>

                  </div>

                </div>

              </div>
            ) : (

              <div className="empty-state">

                <div className="empty-icon">
                  ◎
                </div>

                <h2>
                  Search for a customer
                </h2>

                <p>
                  Enter a Customer ID above to view
                  their segmentation profile.
                </p>

              </div>

            )}

          </section>
        )}

        {/* =====================================================
            BUSINESS INSIGHTS
        ===================================================== */}

        {page === "insights" && (
          <section className="page">

            <div className="page-header">

              <div>

                <div className="eyebrow">
                  DECISION INTELLIGENCE
                </div>

                <h1>
                  Business Insights
                </h1>

                <p>
                  Translate clustering results into
                  practical customer strategies.
                </p>

              </div>

            </div>

            <div className="priority-banner">

              <div className="priority-icon">
                ✦
              </div>

              <div>

                <strong>
                  Recommended Priority
                </strong>

                <p>
                  Retain high-value customers →
                  Grow regular customers →
                  Re-engage at-risk customers.
                </p>

              </div>

            </div>

            <div className="insights-grid">

              <div className="insight-card">

                <div
                  className="insight-number"
                  style={{
                    background: "#10b98115",
                    color: "#10b981",
                  }}
                >
                  01
                </div>

                <div className="insight-content">

                  <div className="insight-title-row">

                    <h2>
                      Retain High-Value Customers
                    </h2>

                    <span className="insight-tag green">
                      HIGHEST PRIORITY
                    </span>

                  </div>

                  <p>
                    Cluster 1 represents the highest-value
                    customer group. These customers purchase
                    frequently, spend significantly more, and
                    interact with a wider range of products.
                  </p>

                  <div className="action-box">

                    <strong>
                      Recommended actions
                    </strong>

                    <span>Loyalty rewards</span>
                    <span>Early product access</span>
                    <span>Personalized offers</span>
                    <span>
                      Cross-selling & upselling
                    </span>

                  </div>

                </div>

              </div>

              <div className="insight-card">

                <div
                  className="insight-number"
                  style={{
                    background: "#3b82f615",
                    color: "#3b82f6",
                  }}
                >
                  02
                </div>

                <div className="insight-content">

                  <div className="insight-title-row">

                    <h2>
                      Grow Regular Customers
                    </h2>

                    <span className="insight-tag blue">
                      GROWTH
                    </span>

                  </div>

                  <p>
                    Cluster 2 contains the largest customer
                    population. These customers show moderate
                    engagement and represent an important
                    opportunity for increasing customer value.
                  </p>

                  <div className="action-box">

                    <strong>
                      Recommended actions
                    </strong>

                    <span>
                      Product recommendations
                    </span>

                    <span>
                      Bundles & cross-selling
                    </span>

                    <span>
                      Personalized promotions
                    </span>

                    <span>
                      Repeat-purchase campaigns
                    </span>

                  </div>

                </div>

              </div>

              <div className="insight-card">

                <div
                  className="insight-number"
                  style={{
                    background: "#ef444415",
                    color: "#ef4444",
                  }}
                >
                  03
                </div>

                <div className="insight-content">

                  <div className="insight-title-row">

                    <h2>
                      Re-Engage At-Risk Customers
                    </h2>

                    <span className="insight-tag red">
                      RETENTION
                    </span>

                  </div>

                  <p>
                    Cluster 0 shows lower purchase frequency,
                    lower monetary value, and higher recency.
                    These customers may require targeted
                    re-engagement.
                  </p>

                  <div className="action-box">

                    <strong>
                      Recommended actions
                    </strong>

                    <span>
                      Personalized recommendations
                    </span>

                    <span>
                      Limited-time offers
                    </span>

                    <span>
                      Purchase reminders
                    </span>

                    <span>
                      New-product announcements
                    </span>

                  </div>

                </div>

              </div>

            </div>

            {/* ================= MODEL EXPLANATION ================= */}

            <div className="two-column">

              <div className="panel">

                <div className="panel-header">

                  <div>
                    <h2>
                      Why K = 3?
                    </h2>

                    <p>
                      Model selection rationale
                    </p>
                  </div>

                </div>

                <div className="methodology">

                  <div className="method-step">

                    <div className="method-number">
                      01
                    </div>

                    <div>

                      <strong>
                        Evaluate candidate values
                      </strong>

                      <p>
                        K values from 2 through 10 were
                        evaluated using inertia and
                        silhouette score.
                      </p>

                    </div>

                  </div>

                  <div className="method-step">

                    <div className="method-number">
                      02
                    </div>

                    <div>

                      <strong>
                        Compare clustering quality
                      </strong>

                      <p>
                        K = 2 produced the highest silhouette
                        score, while additional clusters did
                        not provide sufficient improvement.
                      </p>

                    </div>

                  </div>

                  <div className="method-step">

                    <div className="method-number">
                      03
                    </div>

                    <div>

                      <strong>
                        Select business-useful segmentation
                      </strong>

                      <p>
                        K = 3 provides a practical distinction
                        between low-value, regular, and
                        high-value customers.
                      </p>

                    </div>

                  </div>

                </div>

              </div>

              <div className="panel">

                <div className="panel-header">

                  <div>
                    <h2>
                      Model Quality
                    </h2>

                    <p>
                      Final clustering evaluation
                    </p>
                  </div>

                </div>

                <div className="quality-score">

                  <div className="quality-circle">
                    <span>
                      {silhouette.toFixed(3)}
                    </span>
                  </div>

                  <div>

                    <strong>
                      Silhouette Score
                    </strong>

                    <p>
                      Measures how well-separated and
                      internally cohesive the resulting
                      clusters are.
                    </p>

                  </div>

                </div>

                <div className="quality-note">

                  <strong>
                    Important:
                  </strong>

                  <span>
                    Business recommendations are
                    interpretations of observed behavioral
                    patterns, not causal conclusions.
                  </span>

                </div>

              </div>

            </div>

          </section>
        )}

        <footer className="footer">

          <span>
            CustomerIQ
          </span>

          <span>
            K-Means Customer Segmentation
          </span>

          <span>
            Built for AVIP 2026 · Task 3
          </span>

        </footer>

      </main>

    </div>
  );
}

export default App;