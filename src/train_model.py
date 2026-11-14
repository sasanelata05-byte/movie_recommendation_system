import os
import numpy as np
import pandas as pd
from surprise import Dataset, Reader, SVD

SAMPLE_USERS = 20000
RANDOM_STATE = 42
OUT = "models/svd_artifacts.npz"

ratings = pd.read_csv("data/processed/ratings_clean.csv",
                      usecols=["user_id", "movie_id", "rating"])
sample_users = (ratings["user_id"].drop_duplicates()
                .sample(n=SAMPLE_USERS, random_state=RANDOM_STATE))
small = ratings[ratings["user_id"].isin(sample_users)].reset_index(drop=True)

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(small, reader)
trainset = data.build_full_trainset()

svd = SVD(n_factors=50, n_epochs=10, lr_all=0.005, reg_all=0.02, random_state=42)
svd.fit(trainset)

raw_users = np.array([trainset.to_raw_uid(i) for i in range(trainset.n_users)], dtype=np.int32)
raw_items = np.array([trainset.to_raw_iid(i) for i in range(trainset.n_items)], dtype=np.int32)

triples = list(trainset.all_ratings())
seen_u = np.array([t[0] for t in triples], dtype=np.int32)
seen_i = np.array([t[1] for t in triples], dtype=np.int32)
seen_r = np.array([t[2] for t in triples], dtype=np.int8)

os.makedirs("models", exist_ok=True)
np.savez_compressed(
    OUT,
    pu=svd.pu.astype(np.float32),
    qi=svd.qi.astype(np.float32),
    bu=svd.bu.astype(np.float32),
    bi=svd.bi.astype(np.float32),
    global_mean=np.float32(trainset.global_mean),
    raw_users=raw_users,
    raw_items=raw_items,
    seen_u=seen_u,
    seen_i=seen_i,
    seen_r=seen_r,
)
print(f"Saved {OUT}: {trainset.n_users:,} users, {trainset.n_items:,} movies, {len(triples):,} ratings")