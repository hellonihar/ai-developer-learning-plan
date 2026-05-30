import numpy as np
import pandas as pd


def get_recommendations(seed_title, df, labels, X, top_n=10):
    if seed_title not in df["title"].values:
        return pd.DataFrame()

    seed_idx = df[df["title"] == seed_title].index[0]
    seed_cluster = labels[seed_idx]

    cluster_indices = np.where(labels == seed_cluster)[0]
    cluster_indices = cluster_indices[cluster_indices != seed_idx]

    if len(cluster_indices) == 0:
        return pd.DataFrame()

    seed_vec = X[seed_idx]
    cluster_vecs = X[cluster_indices]
    distances = np.linalg.norm(cluster_vecs - seed_vec, axis=1)

    sorted_order = np.argsort(distances)
    top_indices = cluster_indices[sorted_order][:top_n]

    result = df.iloc[top_indices].copy()
    result["distance"] = distances[sorted_order][:top_n]
    result = result.reset_index(drop=True)
    return result


def get_cluster_movies(df, labels, cluster_id):
    idx = np.where(labels == cluster_id)[0]
    return df.iloc[idx].copy().reset_index(drop=True)


def compute_cluster_profiles(df, labels, numeric_cols, categorical_cols):
    df_p = df.copy()
    df_p["Cluster"] = labels

    numeric_stats = df_p.groupby("Cluster")[numeric_cols].agg(["mean", "std"])
    numeric_stats.columns = [f"{col}_{stat}" for col, stat in numeric_stats.columns]

    cat_means = df_p.groupby("Cluster")[categorical_cols].mean().mul(100).round(1)
    cat_means = cat_means.add_suffix("_pct")

    profiles = numeric_stats.join(cat_means).reset_index()
    profiles["Cluster"] = profiles["Cluster"].astype(int)
    profiles["Count"] = df_p.groupby("Cluster").size().values
    return profiles
