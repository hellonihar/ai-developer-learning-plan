# Movie Recommendation Explorer

## Concept
An interactive application that clusters movies using features like genres, ratings, popularity, and release year — then uses cluster membership to power content-based recommendations. Users can explore movie clusters, find similar titles, and discover hidden gems.

## Why This Project
Movie recommendation is a classic clustering application. Grouping movies by content features reveals natural genres and sub-genres that go beyond manual tagging, and makes recommendations interpretable.

## Key Features
- **Data** — Load TMDB/MovieLens dataset or generate synthetic movie data
- **Multiple algorithms** — KMeans, DBSCAN, Hierarchical clustering with sidebar controls
- **Cluster exploration** — Browse movies in each cluster, view feature distributions
- **Recommendations** — Given a seed movie, recommend others from the same cluster with similarity ranking
- **Visualizations** — PCA/t-SNE projection of movie space, genre composition charts, parallel coordinates
- **Explainability** — Show which features define each cluster (centroid analysis)

## Tech Stack
| Layer | Choice |
|-------|--------|
| **Frontend** | Streamlit |
| **Clustering** | scikit-learn (KMeans, DBSCAN, Agglomerative) |
| **Dimensionality reduction** | PCA, t-SNE |
| **Encoding** | One-hot encoding for genres, StandardScaler for numeric features |
| **Visualization** | Plotly, matplotlib |
| **Data** | pandas, numpy |

## Learning Goals
- Encoding mixed-type features (categorical + numeric) for clustering
- Using cluster centroids to explain segment characteristics
- Building a recommendation engine on top of clustering results
- Comparing clustering algorithms on high-dimensional, sparse movie data
