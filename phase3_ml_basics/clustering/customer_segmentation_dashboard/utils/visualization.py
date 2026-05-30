import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


def compute_pca(X_scaled, n_components=2):
    pca = PCA(n_components=n_components, random_state=42)
    components = pca.fit_transform(X_scaled)
    var_ratio = pca.explained_variance_ratio_
    return components, var_ratio


def compute_tsne(X_scaled, n_components=2, perplexity=30):
    n = X_scaled.shape[0]
    perplexity = min(perplexity, n - 1)
    tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=42)
    return tsne.fit_transform(X_scaled)


def plot_cluster_scatter(components, labels, title="Cluster Visualization",
                         color_continuous_scale=None):
    df_plot = pd.DataFrame({
        "PC1": components[:, 0],
        "PC2": components[:, 1],
        "Cluster": labels.astype(str),
    })
    fig = px.scatter(
        df_plot, x="PC1", y="PC2", color="Cluster",
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(marker=dict(size=6, opacity=0.7))
    return fig


def plot_parallel_coordinates(df, feature_cols, labels):
    df_plot = df[feature_cols].copy()
    df_plot["Cluster"] = labels.astype(str)

    color_seq = px.colors.qualitative.Set2
    df_plot["Cluster_color"] = labels.astype(int)

    unique_clusters = sorted(df_plot["Cluster_color"].unique())
    n = max(len(unique_clusters), 1)

    scale_values = [i / (n - 1) if n > 1 else 0.5 for i in range(n)]
    scale_colors = [color_seq[i % len(color_seq)] for i in range(n)]

    fig = px.parallel_coordinates(
        df_plot, color="Cluster_color",
        dimensions=feature_cols,
        color_continuous_scale=list(zip(scale_values, scale_colors)),
    )
    fig.update_coloraxes(showscale=False)
    return fig


def plot_radar_chart(df, feature_cols, labels):
    df_plot = df[feature_cols].copy()
    df_plot["Cluster"] = labels

    cluster_means = df_plot.groupby("Cluster")[feature_cols].mean().reset_index()

    fig = go.Figure()
    colors = px.colors.qualitative.Set2

    for i, row in cluster_means.iterrows():
        cluster_id = int(row["Cluster"])
        values = row[feature_cols].values.tolist()
        values += values[:1]
        theta = feature_cols + [feature_cols[0]]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=theta,
            fill="toself",
            name=f"Cluster {cluster_id}",
            line_color=colors[cluster_id % len(colors)],
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="Segment Profile Comparison (Radar Chart)",
    )
    return fig


def plot_profiles_table(df, feature_cols, labels):
    df_plot = df[feature_cols].copy()
    df_plot["Cluster"] = labels

    stats = df_plot.groupby("Cluster").agg(["mean", "std", "count"])
    stats.columns = [f"{col}_{stat}" for col, stat in stats.columns]
    stats = stats.reset_index()
    stats["Cluster"] = stats["Cluster"].astype(int)
    return stats
