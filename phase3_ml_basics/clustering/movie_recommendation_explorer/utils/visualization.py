import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


COLORS = px.colors.qualitative.Set2


def compute_pca(X, n_components=2):
    pca = PCA(n_components=n_components, random_state=42)
    components = pca.fit_transform(X)
    var_ratio = pca.explained_variance_ratio_
    return components, var_ratio


def compute_tsne(X, n_components=2, perplexity=30):
    n = X.shape[0]
    perplexity = min(perplexity, n - 1)
    tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=42)
    return tsne.fit_transform(X)


def plot_cluster_scatter(components, labels, title="Movie Space", hover_text=None):
    df_plot = pd.DataFrame({
        "x": components[:, 0],
        "y": components[:, 1],
        "Cluster": labels.astype(str),
    })
    if hover_text is not None:
        df_plot["title"] = hover_text

    fig = px.scatter(
        df_plot, x="x", y="y", color="Cluster",
        title=title, hover_data=["title"] if hover_text is not None else None,
        color_discrete_sequence=COLORS,
    )
    fig.update_traces(marker=dict(size=5, opacity=0.7))
    return fig


def plot_genre_composition(df, labels, genres):
    df_plot = df[genres].copy()
    df_plot["Cluster"] = labels.astype(str)

    cluster_genre_pct = df_plot.groupby("Cluster")[genres].mean().mul(100).reset_index()
    melted = cluster_genre_pct.melt(id_vars="Cluster", var_name="Genre", value_name="Percentage")

    fig = px.bar(
        melted, x="Genre", y="Percentage", color="Cluster",
        barmode="group", title="Genre Composition by Cluster (%)",
        color_discrete_sequence=COLORS,
    )
    return fig


def plot_parallel_coordinates(df, numeric_cols, labels):
    df_plot = df[numeric_cols].copy()
    df_plot["Cluster"] = labels.astype(str)

    color_seq = COLORS
    df_plot["Cluster_color"] = labels.astype(int)

    unique_clusters = sorted(df_plot["Cluster_color"].unique())
    n = max(len(unique_clusters), 1)

    scale_values = [i / (n - 1) if n > 1 else 0.5 for i in range(n)]
    scale_colors = [color_seq[i % len(color_seq)] for i in range(n)]

    fig = px.parallel_coordinates(
        df_plot, color="Cluster_color",
        dimensions=numeric_cols,
        color_continuous_scale=list(zip(scale_values, scale_colors)),
    )
    fig.update_coloraxes(showscale=False)
    return fig


def plot_cluster_radar(profiles_df, numeric_cols):
    cols_for_radar = [c for c in numeric_cols if f"{c}_mean" in profiles_df.columns]
    mean_cols = [f"{c}_mean" for c in cols_for_radar]

    fig = go.Figure()

    for _, row in profiles_df.iterrows():
        cluster_id = int(row["Cluster"])
        values = row[mean_cols].values.tolist()
        values += values[:1]
        theta = cols_for_radar + [cols_for_radar[0]]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=theta,
            fill="toself",
            name=f"Cluster {cluster_id}",
            line_color=COLORS[cluster_id % len(COLORS)],
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title="Cluster Numeric Profile Comparison",
    )
    return fig
