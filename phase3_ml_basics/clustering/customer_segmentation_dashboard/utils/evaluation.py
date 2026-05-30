import numpy as np
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def compute_elbow(X_scaled, max_k=10, random_state=42):
    inertias = []
    k_range = range(2, max_k + 1)
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        model.fit(X_scaled)
        inertias.append(model.inertia_)
    return list(k_range), inertias


def compute_silhouette(X_scaled, labels):
    unique = set(labels)
    if len(unique) < 2 or len(unique) >= len(labels):
        return None
    return silhouette_score(X_scaled, labels)


def compute_davies_bouldin(X_scaled, labels):
    unique = set(labels)
    if len(unique) < 2 or len(unique) >= len(labels):
        return None
    return davies_bouldin_score(X_scaled, labels)
