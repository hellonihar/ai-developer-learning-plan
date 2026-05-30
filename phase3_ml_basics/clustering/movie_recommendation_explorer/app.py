import streamlit as st
import pandas as pd
import numpy as np

from utils.data import (
    generate_synthetic_movies,
    get_feature_columns,
    ALL_GENRES,
    NUMERIC_FEATURES,
)
from utils.clustering import (
    run_clustering,
    get_default_params,
    ALGORITHMS,
)
from utils.recommendations import (
    get_recommendations,
    get_cluster_movies,
    compute_cluster_profiles,
)
from utils.visualization import (
    compute_pca,
    compute_tsne,
    plot_cluster_scatter,
    plot_genre_composition,
    plot_parallel_coordinates,
    plot_cluster_radar,
)

st.set_page_config(page_title="Movie Recommendation Explorer", layout="wide")
st.title("Movie Recommendation Explorer")
st.markdown("Cluster movies by features and get content-based recommendations.")

if "data" not in st.session_state:
    st.session_state.data = None
if "labels" not in st.session_state:
    st.session_state.labels = None
if "X" not in st.session_state:
    st.session_state.X = None
if "algorithm" not in st.session_state:
    st.session_state.algorithm = "KMeans (sklearn)"

with st.sidebar:
    st.header("Data")
    n_movies = st.slider("Number of movies", 200, 1000, 500, step=50)
    if st.button("Generate Movie Data"):
        with st.spinner("Generating..."):
            st.session_state.data = generate_synthetic_movies(
                n_movies=n_movies, random_state=42
            )
            st.session_state.labels = None
            st.session_state.X = None
        st.success(f"Generated {n_movies} movies.")

    st.divider()

    st.header("Clustering Settings")
    algo = st.selectbox(
        "Algorithm",
        list(ALGORITHMS.keys()),
        index=list(ALGORITHMS.keys()).index(st.session_state.algorithm),
    )
    st.session_state.algorithm = algo

    default_params = get_default_params(algo)
    params = {}

    if algo in ("KMeans (sklearn)", "KMeans (scratch)"):
        params["n_clusters"] = st.slider(
            "Number of clusters", 2, 8,
            value=default_params.get("n_clusters", 4)
        )
    elif algo == "DBSCAN":
        params["eps"] = st.slider(
            "eps", 0.1, 3.0,
            value=default_params.get("eps", 1.5), step=0.05
        )
        params["min_samples"] = st.slider(
            "min_samples", 2, 20,
            value=default_params.get("min_samples", 5)
        )
    elif algo == "Hierarchical (Agglomerative)":
        params["n_clusters"] = st.slider(
            "Number of clusters", 2, 8,
            value=default_params.get("n_clusters", 4)
        )
        params["linkage"] = st.selectbox(
            "Linkage",
            ["ward", "complete", "average", "single"],
            index=["ward", "complete", "average", "single"].index(
                default_params.get("linkage", "ward")
            ),
        )

    run_btn = st.button("Run Clustering", type="primary")

if st.session_state.data is None:
    st.info("👈 Generate movie data to get started.")
    st.stop()

df = st.session_state.data
numeric_cols, categorical_cols = get_feature_columns(df)

if run_btn:
    with st.spinner(f"Running {algo}..."):
        try:
            labels, model, X, scaler = run_clustering(
                algo, df, numeric_cols, categorical_cols, **params
            )
            st.session_state.labels = labels
            st.session_state.X = X
        except Exception as e:
            st.error(f"Clustering failed: {e}")

if st.session_state.labels is None:
    st.warning("Configure settings and click **Run Clustering**.")
    st.stop()

labels = st.session_state.labels
X = st.session_state.X

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Data Preview", "Cluster Results", "Movie Explorer",
    "Recommendations", "Cluster Profiles",
])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Movie Data")
        display_cols = ["title"] + numeric_cols + categorical_cols
        st.dataframe(df[display_cols].head(100), use_container_width=True)
    with col2:
        st.subheader("Numeric Summary")
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        st.subheader("Genre Frequencies")
        genre_counts = df[categorical_cols].sum().sort_values(ascending=False)
        st.dataframe(
            genre_counts.reset_index().rename(
                columns={"index": "Genre", 0: "Count"}
            ),
            use_container_width=True,
        )

with tab2:
    st.subheader("Cluster Visualizations")

    vis_col1, vis_col2 = st.columns(2)

    with vis_col1:
        with st.spinner("Computing PCA..."):
            pca_components, var_ratio = compute_pca(X)
        fig_pca = plot_cluster_scatter(
            pca_components, labels,
            title=f"PCA Projection ({var_ratio[0]:.1%} / {var_ratio[1]:.1%} variance)",
            hover_text=df["title"].values,
        )
        st.plotly_chart(fig_pca, use_container_width=True)

    with vis_col2:
        with st.spinner("Computing t-SNE..."):
            if X.shape[0] <= 2000:
                tsne_components = compute_tsne(X)
                fig_tsne = plot_cluster_scatter(
                    tsne_components, labels,
                    title="t-SNE Projection",
                    hover_text=df["title"].values,
                )
                st.plotly_chart(fig_tsne, use_container_width=True)
            else:
                st.info("t-SNE skipped for >2000 rows.")

with tab3:
    st.subheader("Browse Movies by Cluster")
    unique_clusters = sorted(set(labels))
    selected_cluster = st.selectbox(
        "Select cluster", unique_clusters,
        format_func=lambda c: f"Cluster {c} ({np.sum(labels == c)} movies)"
    )

    cluster_df = get_cluster_movies(df, labels, selected_cluster)
    display_cols = ["title"] + numeric_cols + categorical_cols
    st.dataframe(cluster_df[display_cols], use_container_width=True)

with tab4:
    st.subheader("Get Movie Recommendations")
    movie_titles = df["title"].tolist()
    seed_movie = st.selectbox("Select a movie", movie_titles)

    top_n = st.slider("Number of recommendations", 5, 20, 10)

    if seed_movie:
        recs = get_recommendations(seed_movie, df, labels, X, top_n=top_n)

        if len(recs) > 0:
            seed_cluster = labels[df[df["title"] == seed_movie].index[0]]
            st.info(
                f"**{seed_movie}** is in **Cluster {seed_cluster}**. "
                f"Showing {len(recs)} similar movies:"
            )

            rec_display = recs[["title"] + numeric_cols + ["distance"]].copy()
            rec_display["distance"] = rec_display["distance"].round(3)
            st.dataframe(rec_display, use_container_width=True)

            with st.spinner("Computing PCA for visualization..."):
                seed_idx = df[df["title"] == seed_movie].index[0]
                highlight_labels = np.full(len(labels), "Other", dtype=object)
                highlight_labels[seed_idx] = "Seed Movie"
                rec_indices = recs.index.values
                for idx in rec_indices:
                    highlight_labels[idx] = "Recommended"

                pca_rec, _ = compute_pca(X)
                fig_rec = plot_cluster_scatter(
                    pca_rec, highlight_labels,
                    title="Seed + Recommendations in PCA Space",
                    hover_text=df["title"].values,
                )
                st.plotly_chart(fig_rec, use_container_width=True)
        else:
            st.warning("No other movies in this cluster to recommend.")

with tab5:
    st.subheader("Cluster Profile Analysis")

    profiles = compute_cluster_profiles(df, labels, numeric_cols, categorical_cols)
    st.dataframe(profiles, use_container_width=True)

    prof_col1, prof_col2 = st.columns(2)

    with prof_col1:
        fig_radar = plot_cluster_radar(profiles, numeric_cols)
        st.plotly_chart(fig_radar, use_container_width=True)

    with prof_col2:
        fig_genre = plot_genre_composition(df, labels, categorical_cols)
        st.plotly_chart(fig_genre, use_container_width=True)

    fig_parallel = plot_parallel_coordinates(df, numeric_cols, labels)
    st.plotly_chart(fig_parallel, use_container_width=True)
