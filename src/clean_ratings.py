import pandas as pd

ratings = pd.read_csv("data/processed/ratings.csv")
print("Before filtering:", ratings.shape,
      ratings["user_id"].nunique(), "users,",
      ratings["movie_id"].nunique(), "movies")

user_counts = ratings["user_id"].value_counts()
movie_counts = ratings["movie_id"].value_counts()

MIN_RATINGS = 20
ratings = ratings[
    ratings["user_id"].isin(user_counts[user_counts >= MIN_RATINGS].index) &
    ratings["movie_id"].isin(movie_counts[movie_counts >= MIN_RATINGS].index)
].reset_index(drop=True)

ratings["date"] = pd.to_datetime(ratings["date"])
ratings.to_csv("data/processed/ratings_clean.csv", index=False)

print("After filtering:", ratings.shape,
      ratings["user_id"].nunique(), "users,",
      ratings["movie_id"].nunique(), "movies")