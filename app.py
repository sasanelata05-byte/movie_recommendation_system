import os
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACT_PATH = os.path.join(BASE_DIR, "models", "svd_artifacts.npz")
TITLES_PATH = os.path.join(BASE_DIR, "models", "movie_titles.csv")

METRICS = {
    "baseline": {"rmse": 0.9222, "mae": 0.7262, "precision": 0.558, "recall": 0.785},
    "svd": {"rmse": 0.9011, "mae": 0.7052, "precision": 0.565, "recall": 0.790},
}

app = Flask(__name__)

# Load the trained factors once at startup
art = np.load(ARTIFACT_PATH)
PU, QI = art["pu"], art["qi"]
BU, BI = art["bu"], art["bi"]
GLOBAL_MEAN = float(art["global_mean"])
RAW_USERS, RAW_ITEMS = art["raw_users"], art["raw_items"]
SEEN_U, SEEN_I, SEEN_R = art["seen_u"], art["seen_i"], art["seen_r"]
USER_TO_IDX = {int(u): i for i, u in enumerate(RAW_USERS)}

# Optional: add movie names by creating models/movie_titles.csv
# with columns movie_id,title,genres (genres separated by |)
TITLES = {}
if os.path.exists(TITLES_PATH):
    df = pd.read_csv(TITLES_PATH).fillna("")
    TITLES = {int(r.movie_id): {"title": r.title,
                                "genres": r.genres.replace("|", " · ")}
              for r in df.itertuples()}


def predict_all(u):
    scores = GLOBAL_MEAN + BU[u] + BI + QI @ PU[u]
    return np.clip(scores, 1.0, 5.0)


def movie_info(raw_id):
    info = TITLES.get(raw_id, {})
    return {
        "movie_id": raw_id,
        "title": info.get("title", f"Movie #{raw_id}"),
        "genres": info.get("genres", ""),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify(status="ok")


@app.route("/api/stats")
def stats():
    return jsonify(users=len(RAW_USERS), movies=len(RAW_ITEMS),
                   ratings=int(len(SEEN_U)), metrics=METRICS)


@app.route("/api/random")
def random_users():
    count = min(max(request.args.get("count", 1, type=int), 1), 10)
    picks = np.random.choice(RAW_USERS, size=count, replace=False)
    return jsonify(users=[int(p) for p in picks])


@app.route("/api/recommend")
def recommend():
    user_id = request.args.get("user", type=int)
    n = min(max(request.args.get("n", 12, type=int), 1), 20)

    if user_id is None:
        return jsonify(error="Please enter a numeric viewer ID."), 400
    if user_id not in USER_TO_IDX:
        return jsonify(error=f"Viewer {user_id} isn't in our sample. Try 'Surprise me'."), 404

    u = USER_TO_IDX[user_id]
    mask = SEEN_U == u
    seen_items = SEEN_I[mask]
    seen_ratings = SEEN_R[mask]

    scores = predict_all(u)
    scores[seen_items] = -np.inf
    top = np.argpartition(-scores, n)[:n]
    top = top[np.argsort(-scores[top])]

    order = np.argsort(-seen_ratings, kind="stable")[:8]
    history = [{**movie_info(int(RAW_ITEMS[seen_items[k]])),
                "rating": int(seen_ratings[k])} for k in order]

    recommendations = []
    for i in top:
        est = float(scores[i])
        recommendations.append({
            **movie_info(int(RAW_ITEMS[i])),
            "predicted": round(est, 2),
            "match": int(round((est - 1) / 4 * 100)),
        })

    return jsonify(user_id=user_id, rated_count=int(mask.sum()),
                   history=history, recommendations=recommendations)


if __name__ == "__main__":
    app.run(debug=True)