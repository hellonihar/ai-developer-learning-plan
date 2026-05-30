# Customer Segmentation Dashboard

Interactive dashboard for segmenting customers using clustering algorithms. Built with Streamlit and scikit-learn.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Usage

### 1. Load Data

| Option | Details |
|--------|---------|
| **Synthetic Data** | Generate 100–1000 rows of realistic customer data with 5 features (Age, Annual Income, Spending Score, Purchase Frequency, Tenure). Built from 3 multivariate Gaussian clusters. |
| **Upload CSV** | Upload any CSV file. Must contain at least 2 numeric columns. All numeric columns are used as features. |

Click **Generate Data** or upload a CSV file in the sidebar.

### 2. Configure & Run Clustering

Select an algorithm and tune its hyperparameters in the sidebar:

| Algorithm | Parameters | Notes |
|-----------|------------|-------|
| **KMeans (sklearn)** | `n_clusters` (2–10) | scikit-learn implementation with k-means++ initialization |
| **KMeans (scratch)** | `n_clusters` (2–10) | From-scratch implementation using random initialization, Euclidean distance, and convergence check |
| **DBSCAN** | `eps` (0.1–3.0), `min_samples` (2–20) | Density-based; points not assigned to any cluster are labeled -1 |
| **Hierarchical (Agglomerative)** | `n_clusters` (2–10), `linkage` (ward/complete/average/single) | Bottom-up merging |

Click **Run Clustering** to execute. Data is standardized (z-score) before clustering.

### 3. Explore Results (5 Tabs)

| Tab | Content |
|-----|---------|
| **Data Preview** | Raw data table (first 100 rows) + statistical summary (mean, std, min, max, etc.) |
| **Elbow Method** | Inertia-vs-K line chart (KMeans only) with automatic optimal K suggestion |
| **Cluster Results** | PCA scatter plot (with variance ratios), t-SNE scatter plot, Silhouette Score, and Davies–Bouldin Index |
| **Segment Profiles** | Radar chart comparing cluster means, parallel coordinates plot, per-cluster statistics table (mean, std, count) |
| **Export** | Preview the segmented data + download as CSV |

## Project Structure

```
customer_segmentation_dashboard/
├── app.py                 # Streamlit entry point
├── requirements.txt       # Dependencies
├── APPLICATION_IDEA.md    # Original concept
└── utils/
    ├── data.py            # CSV loading, synthetic data generation
    ├── clustering.py      # KMeans (scratch + sklearn), DBSCAN, Agglomerative
    ├── evaluation.py      # Elbow method, Silhouette, Davies-Bouldin
    ├── visualization.py   # PCA, t-SNE, scatter plots, radar, parallel coordinates
    └── export.py          # CSV export with cluster labels
```

## Tech Stack

streamlit, scikit-learn, pandas, numpy, plotly, matplotlib, seaborn
