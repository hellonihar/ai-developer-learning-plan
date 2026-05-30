import pandas as pd
import io


def add_cluster_labels(df, labels, algorithm_name):
    result = df.copy()
    result["Cluster"] = labels
    result["Algorithm"] = algorithm_name
    return result


def get_csv_bytes(df):
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()
