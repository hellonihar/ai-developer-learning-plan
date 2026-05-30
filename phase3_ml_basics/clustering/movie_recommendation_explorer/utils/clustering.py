import numpy as np
import pandas as pd
from sklearn.cluster import KMeans as SklearnKMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler


class KMeansScratch:
    def __init__(self, n_clusters=3, max_iter=100, tol=1e-4, random_state=None):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.centroids = None
        self.labels = None
        self.inertia_ = None
        self.n_iter_ = 0

    def fit(self, X):
        rng = np.random.RandomState(self.random_state)
        n_samples = X.shape[0]

        idx = rng.choice(n_samples, self.n_clusters, replace=False)
        self.centroids = X[idx].copy()

        for i in range(self.max_iter):
            distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
            self.labels = np.argmin(distances, axis=1)

            new_centroids = np.array([
                X[self.labels == k].mean(axis=0) if np.any(self.labels == k)
                else self.centroids[k]
                for k in range(self.n_clusters)
            ])

            shift = np.linalg.norm(new_centroids - self.centroids)
            self.centroids = new_centroids
            self.n_iter_ = i + 1

            if shift < self.tol:
                break

        self.inertia_ = sum(
            np.linalg.norm(X[self.labels == k] - self.centroids[k]) ** 2
            for k in range(self.n_clusters)
            if np.any(self.labels == k)
        )
        return self

    def predict(self, X):
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
        return np.argmin(distances, axis=1)

    def fit_predict(self, X):
        self.fit(X)
        return self.labels


def run_kmeans_sklearn(X, n_clusters=3, random_state=42):
    model = SklearnKMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = model.fit_predict(X)
    return labels, model


def run_kmeans_scratch(X, n_clusters=3, random_state=42):
    model = KMeansScratch(n_clusters=n_clusters, random_state=random_state)
    labels = model.fit_predict(X)
    return labels, model


def run_dbscan(X, eps=0.5, min_samples=5):
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(X)
    return labels, model


def run_agglomerative(X, n_clusters=3, linkage="ward"):
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
    labels = model.fit_predict(X)
    return labels, model


ALGORITHMS = {
    "KMeans (sklearn)": run_kmeans_sklearn,
    "KMeans (scratch)": run_kmeans_scratch,
    "DBSCAN": run_dbscan,
    "Hierarchical (Agglomerative)": run_agglomerative,
}


def get_default_params(algorithm_name):
    params = {
        "KMeans (sklearn)": {"n_clusters": 4},
        "KMeans (scratch)": {"n_clusters": 4},
        "DBSCAN": {"eps": 1.5, "min_samples": 5},
        "Hierarchical (Agglomerative)": {"n_clusters": 4, "linkage": "ward"},
    }
    return params.get(algorithm_name, {})


def prepare_features(df, numeric_cols, categorical_cols):
    X_numeric = df[numeric_cols].values
    scaler = StandardScaler()
    X_numeric_scaled = scaler.fit_transform(X_numeric)

    X_cat = df[categorical_cols].values

    X = np.hstack([X_numeric_scaled, X_cat])
    return X, scaler, X_numeric_scaled


def run_clustering(algorithm_name, df, numeric_cols, categorical_cols, **kwargs):
    X, scaler, X_numeric_scaled = prepare_features(df, numeric_cols, categorical_cols)

    func = ALGORITHMS[algorithm_name]
    labels, model = func(X, **kwargs)

    return labels, model, X, scaler
