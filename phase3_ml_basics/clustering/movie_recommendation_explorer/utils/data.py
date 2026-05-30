import pandas as pd
import numpy as np

ALL_GENRES = [
    "Action", "Comedy", "Drama", "Horror",
    "Sci-Fi", "Romance", "Thriller", "Animation",
]

NUMERIC_FEATURES = [
    "vote_average", "popularity", "release_year",
    "runtime", "budget_mil",
]

CATEGORICAL_FEATURES = ALL_GENRES

def generate_synthetic_movies(n_movies=500, random_state=42):
    rng = np.random.RandomState(random_state)
    n_per = n_movies // 4
    titles = [f"Movie_{i}" for i in range(n_movies)]

    dfs = []

    profiles = [
        {"name": "Blockbusters",  "n": n_per,
         "genres": {"Action": 0.7, "Sci-Fi": 0.5, "Thriller": 0.3},
         "vote": 7.0, "vote_std": 0.8,
         "pop": 75, "pop_std": 12,
         "year": 2015, "year_std": 6,
         "runtime": 140, "runtime_std": 15,
         "budget": 150, "budget_std": 40},
        {"name": "Indie Dramas",  "n": n_per,
         "genres": {"Drama": 0.8, "Romance": 0.4},
         "vote": 8.0, "vote_std": 0.7,
         "pop": 35, "pop_std": 10,
         "year": 2010, "year_std": 8,
         "runtime": 110, "runtime_std": 18,
         "budget": 15, "budget_std": 10},
        {"name": "Horror",  "n": n_per,
         "genres": {"Horror": 0.8, "Thriller": 0.4},
         "vote": 5.8, "vote_std": 1.0,
         "pop": 45, "pop_std": 12,
         "year": 2018, "year_std": 4,
         "runtime": 95, "runtime_std": 12,
         "budget": 10, "budget_std": 8},
        {"name": "Comedies",  "n": n_per,
         "genres": {"Comedy": 0.8, "Romance": 0.3, "Drama": 0.2},
         "vote": 6.5, "vote_std": 0.9,
         "pop": 60, "pop_std": 14,
         "year": 2012, "year_std": 7,
         "runtime": 100, "runtime_std": 13,
         "budget": 40, "budget_std": 20},
    ]

    for prof in profiles:
        n = prof["n"]
        data = {
            "title": titles[:n],
            "vote_average": np.clip(
                rng.normal(prof["vote"], prof["vote_std"], n), 1, 10
            ).round(1),
            "popularity": np.clip(
                rng.normal(prof["pop"], prof["pop_std"], n), 0, 100
            ).round(1),
            "release_year": np.clip(
                rng.normal(prof["year"], prof["year_std"], n), 1980, 2025
            ).astype(int),
            "runtime": np.clip(
                rng.normal(prof["runtime"], prof["runtime_std"], n), 45, 250
            ).astype(int),
            "budget_mil": np.clip(
                rng.normal(prof["budget"], prof["budget_std"], n), 0.5, 400
            ).round(1),
        }

        for genre in ALL_GENRES:
            prob = prof["genres"].get(genre, 0.05)
            data[genre] = (rng.random(n) < prob).astype(int)

        df = pd.DataFrame(data)
        dfs.append(df)
        titles = titles[n:]

    result = pd.concat(dfs, ignore_index=True)
    rng.shuffle(result.values)
    result = result.reset_index(drop=True)
    return result


def get_feature_columns(df):
    numeric = [c for c in NUMERIC_FEATURES if c in df.columns]
    categorical = [c for c in ALL_GENRES if c in df.columns]
    return numeric, categorical
