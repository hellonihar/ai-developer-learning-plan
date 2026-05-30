# Customer Segmentation Dashboard

## Concept
An interactive dashboard that segments customers using clustering algorithms (KMeans, DBSCAN, Hierarchical) based on purchasing behavior, demographics, and engagement metrics. Users can upload their own customer data or use synthetic data, tune hyperparameters, and explore segment characteristics.

## Why This Project
Customer segmentation is the most common real-world application of clustering. A clear, visual dashboard makes the output interpretable to non-technical stakeholders.

## Key Features
- **Data input** — Upload CSV or generate synthetic customer data
- **Multiple algorithms** — KMeans, DBSCAN, Hierarchical clustering with sidebar controls for hyperparameters
- **Elbow method** — Automatic inertia plot for optimal K selection
- **Segment profiling** — Mean/median stats per cluster (age, spend, frequency, etc.)
- **Visualizations** — 2D PCA/t-SNE projection, parallel coordinates, radar charts for segment comparison
- **Export** — Download segmented data as CSV

## Tech Stack
| Layer | Choice |
|-------|--------|
| **Frontend** | Streamlit |
| **Clustering** | scikit-learn (KMeans, DBSCAN, Agglomerative) |
| **Dimensionality reduction** | PCA, t-SNE |
| **Visualization** | Plotly, matplotlib, seaborn |
| **Data** | pandas, numpy |

## Learning Goals
- Implementing KMeans from scratch vs. using sklearn
- Understanding hyperparameter effects (n_clusters, eps, linkage)
- Interpreting silhouette scores and Davies–Bouldin index
- Communicating cluster insights visually
