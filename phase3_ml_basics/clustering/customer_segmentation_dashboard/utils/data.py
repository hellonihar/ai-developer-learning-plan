import pandas as pd
import numpy as np
import io


FEATURE_COLUMNS = ["Age", "Annual_Income_k", "Spending_Score", "Purchase_Freq", "Tenure_Months"]


def load_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        raise ValueError("CSV must contain at least 2 numeric columns.")
    return df


def generate_synthetic_data(n_samples=300, random_state=42):
    rng = np.random.RandomState(random_state)

    n_per_cluster = n_samples // 3

    # Cluster 0: Young, low income, high spend
    c0 = rng.multivariate_normal(
        [25, 30, 80, 12, 6], [[5, 0, 0, 0, 0], [0, 8, 0, 0, 0],
                               [0, 0, 10, 0, 0], [0, 0, 0, 3, 0],
                               [0, 0, 0, 0, 2]], n_per_cluster
    )
    # Cluster 1: Middle-aged, mid income, mid spend
    c1 = rng.multivariate_normal(
        [45, 60, 50, 6, 24], [[6, 0, 0, 0, 0], [0, 10, 0, 0, 0],
                               [0, 0, 12, 0, 0], [0, 0, 0, 2, 0],
                               [0, 0, 0, 0, 5]], n_per_cluster
    )
    # Cluster 2: Older, high income, low spend
    c2 = rng.multivariate_normal(
        [55, 90, 25, 3, 48], [[6, 0, 0, 0, 0], [0, 12, 0, 0, 0],
                               [0, 0, 8, 0, 0], [0, 0, 0, 1.5, 0],
                               [0, 0, 0, 0, 6]], n_per_cluster
    )

    data = np.vstack([c0, c1, c2])
    rng.shuffle(data)

    df = pd.DataFrame(data, columns=FEATURE_COLUMNS)
    df = df.round({
        "Age": 0,
        "Annual_Income_k": 1,
        "Spending_Score": 0,
        "Purchase_Freq": 1,
        "Tenure_Months": 0,
    })
    df[["Age", "Spending_Score", "Tenure_Months"]] = df[
        ["Age", "Spending_Score", "Tenure_Months"]
    ].astype(int)
    df["Spending_Score"] = df["Spending_Score"].clip(0, 100)
    df["Age"] = df["Age"].clip(18, 70)
    df["Purchase_Freq"] = df["Purchase_Freq"].clip(0, 30)
    df["Tenure_Months"] = df["Tenure_Months"].clip(0, 72)
    df["Annual_Income_k"] = df["Annual_Income_k"].clip(15, 150)

    return df
