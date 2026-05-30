import streamlit as st
import pandas as pd
import numpy as np

from utils.data import load_csv, generate_synthetic_data, FEATURE_COLUMNS
from utils.clustering import (
    run_clustering,
    get_default_params,
    ALGORITHMS,
)
from utils.evaluation import compute_elbow, compute_silhouette, compute_davies_bouldin
from utils.visualization import (
    compute_pca,
    compute_tsne,
    plot_cluster_scatter,
    plot_parallel_coordinates,
    plot_radar_chart,
    plot_profiles_table,
)
from utils.export import add_cluster_labels, get_csv_bytes

st.set_page_config(page_title="Customer Segmentation Dashboard", layout="wide")
st.title("Customer Segmentation Dashboard")
st.markdown("Segment customers using KMeans, DBSCAN, or Hierarchical clustering.")

if "data" not in st.session_state:
    st.session_state.data = None
if "labels" not in st.session_state:
    st.session_state.labels = None
if "X_scaled" not in st.session_state:
    st.session_state.X_scaled = None
if "feature_cols" not in st.session_state:
    st.session_state.feature_cols = FEATURE_COLUMNS
if "algorithm" not in st.session_state:
    st.session_state.algorithm = "KMeans (sklearn)"

with st.sidebar:
    st.header("Data Source")
    data_option = st.radio("Choose data", ["Synthetic Data", "Upload CSV"])

    if data_option == "Synthetic Data":
        n_samples = st.slider("Number of samples", 100, 1000, 300, step=50)
        if st.button("Generate Data"):
            with st.spinner("Generating..."):
                st.session_state.data = generate_synthetic_data(
                    n_samples=n_samples, random_state=42
                )
                st.session_state.feature_cols = FEATURE_COLUMNS
                st.session_state.labels = None
            st.success(f"Generated {n_samples} rows of synthetic data.")
    else:
        uploaded = st.file_uploader("Upload CSV", type="csv")
        if uploaded is not None:
            try:
                st.session_state.data = load_csv(uploaded)
                numeric_cols = st.session_state.data.select_dtypes(
                    include=[np.number]
                ).columns.tolist()
                if len(numeric_cols) >= 2:
                    st.session_state.feature_cols = numeric_cols
                st.session_state.labels = None
                st.success("CSV loaded successfully.")
            except Exception as e:
                st.error(f"Error: {e}")

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
            "Number of clusters (k)", 2, 10,
            value=default_params.get("n_clusters", 3)
        )
    elif algo == "DBSCAN":
        params["eps"] = st.slider(
            "eps (neighborhood radius)", 0.1, 3.0,
            value=default_params.get("eps", 0.5), step=0.05
        )
        params["min_samples"] = st.slider(
            "min_samples", 2, 20,
            value=default_params.get("min_samples", 5)
        )
    elif algo == "Hierarchical (Agglomerative)":
        params["n_clusters"] = st.slider(
            "Number of clusters", 2, 10,
            value=default_params.get("n_clusters", 3)
        )
        params["linkage"] = st.selectbox(
            "Linkage criterion",
            ["ward", "complete", "average", "single"],
            index=["ward", "complete", "average", "single"].index(
                default_params.get("linkage", "ward")
            ),
        )

    run_btn = st.button("Run Clustering", type="primary")

if st.session_state.data is None:
    st.info("👈 Generate or upload data to get started.")
    st.stop()

df = st.session_state.data
feature_cols = st.session_state.feature_cols

if run_btn:
    with st.spinner(f"Running {algo}..."):
        try:
            labels, model, X_scaled, scaler = run_clustering(
                algo, df, feature_cols, **params
            )
            st.session_state.labels = labels
            st.session_state.X_scaled = X_scaled
        except Exception as e:
            st.error(f"Clustering failed: {e}")

if st.session_state.labels is None:
    st.warning("Configure settings and click **Run Clustering**.")
    st.stop()

labels = st.session_state.labels
X_scaled = st.session_state.X_scaled

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Data Preview", "Elbow Method", "Cluster Results",
    "Segment Profiles", "Export"
])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Raw Data")
        st.dataframe(df.head(100), use_container_width=True)
    with col2:
        st.subheader("Statistical Summary")
        st.dataframe(df[feature_cols].describe(), use_container_width=True)

with tab2:
    if algo in ("KMeans (sklearn)", "KMeans (scratch)"):
        st.subheader("Elbow Method — Inertia vs K")
        with st.spinner("Computing elbow curve..."):
            k_range, inertias = compute_elbow(X_scaled, max_k=10)
        elbow_df = pd.DataFrame({"K": k_range, "Inertia": inertias})
        st.line_chart(elbow_df, x="K", y="Inertia")

        deltas = np.diff(inertias)
        delta_deltas = np.diff(deltas)
        if len(delta_deltas) > 0:
            optimal_k = int(np.argmax(delta_deltas) + 2)
            st.info(
                f"💡 Suggested optimal K based on elbow method: **{optimal_k}**"
            )
    else:
        st.info("Elbow method is only available for KMeans-based algorithms.")

with tab3:
    st.subheader("Cluster Visualizations")

    metrics_col1, metrics_col2 = st.columns(2)
    with metrics_col1:
        sil = compute_silhouette(X_scaled, labels)
        if sil is not None:
            st.metric("Silhouette Score", f"{sil:.3f}")
    with metrics_col2:
        db = compute_davies_bouldin(X_scaled, labels)
        if db is not None:
            st.metric("Davies–Bouldin Index", f"{db:.3f}")

    vis_col1, vis_col2 = st.columns(2)

    with vis_col1:
        with st.spinner("Computing PCA..."):
            pca_components, var_ratio = compute_pca(X_scaled)
        fig_pca = plot_cluster_scatter(
            pca_components, labels,
            title=f"PCA Projection ({var_ratio[0]:.1%} / {var_ratio[1]:.1%} variance)"
        )
        st.plotly_chart(fig_pca, use_container_width=True)

    with vis_col2:
        with st.spinner("Computing t-SNE (may be slow for large data)..."):
            if X_scaled.shape[0] <= 2000:
                tsne_components = compute_tsne(X_scaled)
                fig_tsne = plot_cluster_scatter(
                    tsne_components, labels,
                    title="t-SNE Projection"
                )
                st.plotly_chart(fig_tsne, use_container_width=True)
            else:
                st.info("t-SNE skipped for >2000 rows (performance).")

with tab4:
    st.subheader("Segment Profiles")

    prof_col1, prof_col2 = st.columns([1, 1])

    with prof_col1:
        fig_radar = plot_radar_chart(df, feature_cols, labels)
        st.plotly_chart(fig_radar, use_container_width=True)

    with prof_col2:
        fig_parallel = plot_parallel_coordinates(df, feature_cols, labels)
        st.plotly_chart(fig_parallel, use_container_width=True)

    st.subheader("Per-Cluster Statistics")
    stats_df = plot_profiles_table(df, feature_cols, labels)
    st.dataframe(stats_df, use_container_width=True)

with tab5:
    st.subheader("Export Segmented Data")

    result_df = add_cluster_labels(df, labels, algo)
    st.dataframe(result_df.head(20), use_container_width=True)
    st.caption(f"Full dataset: {result_df.shape[0]} rows × {result_df.shape[1]} columns")

    csv_bytes = get_csv_bytes(result_df)
    st.download_button(
        label="📥 Download CSV",
        data=csv_bytes,
        file_name="customer_segments.csv",
        mime="text/csv",
    )
