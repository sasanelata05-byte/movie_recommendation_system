# Movie Recommendation System (Netflix Prize + SVD)

## 1. Problem

Streaming platforms offer thousands of titles, so users need help finding what they'll enjoy. This project builds a collaborative filtering recommender using Singular Value Decomposition (SVD) on Netflix Prize ratings. It learns hidden taste factors from users' past ratings and ranks unseen movies for each user.

## 2. Data

- **Ratings:** `combined_data_1.txt` from the Netflix Prize dataset. It has 4,499 movies and 24,053,764 ratings. Each movie header line ends with a colon, followed by `UserID,Rating,Date` rows. `src/parse_ratings.py` converts this into one row per rating.
- **Genres:** `movielens_movies.csv` (MovieLens), which provides titles and genres.
- **Titles:** `movie_titles.csv` from the Netflix dataset. *TODO: add once the join is complete and report the match rate.*

**Cleaning:** users and movies with fewer than 20 ratings were removed. This kept 22,319,353 ratings (93%), 260,506 users, and all 4,499 movies. Most of the removed ratings came from users with few ratings.

## 3. EDA

## 3. EDA

- **Rating distribution:** ratings skew toward the upper middle. Four is the most common rating (about 7.5 million), followed by three (about 6.5 million). Ratings of 1 and 2 are rare, which gives a mean of 3.60 and a median of 4.
- **User activity:** most users rate few movies. The median user has 58 ratings, 75% have 106 or fewer, and a small group of heavy raters reaches 4,467. The log-scale plot shows the long tail clearly.
- **Movie popularity:** popularity is highly uneven. The median movie has 508 ratings, while the most-rated movie has 171,309. Popular movies don't always have high averages, so the most-rated movies are not automatically the best.
- **Ratings over time:** volume rose sharply from 1999 to 2005, reaching about 11 million in the final year. Most of the data comes from recent years, which makes a time-based train/test split a useful next experiment.
- **Average rating per user:** averages are centered near 3.6, with most users between 3.0 and 4.2. This variation in how generously users rate supports including user bias terms in the model.

## 4. Method

- **Baseline:** `BaselineOnly`, which predicts from the global average plus user and movie biases.
- **Model:** `SVD` from the Surprise library, with 50 latent factors, 10 epochs, learning rate 0.005, and regularization 0.02.
- **Evaluation:** an 80/20 train/test split with a fixed random seed. RMSE and MAE measure rating accuracy. Precision@10 and Recall@10 (threshold: rating of 4 or higher) measure ranking quality.
- **Sample:** development and evaluation used 20,000 randomly selected users (1,370,409 training and 342,603 test ratings). Training on the full dataset was too slow on the available hardware.

## 5. Results

| Model | RMSE | MAE | Precision@10 | Recall@10 |
|---|---|---|---|---|
| Baseline | 0.9222 | 0.7262 | 0.558 | 0.785 |
| SVD | 0.9011 | 0.7052 | 0.565 | 0.790 |

SVD improves on the baseline on all four metrics. The gains are modest, about 2% lower error and about 1 point higher precision and recall, which is typical when a strong baseline already captures popularity and user generosity.

## 6. Example recommendations

For user 1248029 (338 rated movies), SVD's top 10 unseen movies had predicted ratings from 4.03 to 4.23. None of them appeared in the user's rating history.

*TODO: replace the IDs with titles and genres once `movie_titles.csv` is joined.*

## 7. Limitations and next steps

- **Subset of the catalog:** `combined_data_1.txt` covers only movies 1 to 4,499. The full dataset has 17,770 titles, and the other rating files would extend coverage.
- **Sample-based evaluation:** results come from 20,000 users. Full-data training and a grid search for hyperparameters are still needed.
- **Title matching:** joining Netflix and MovieLens titles by name and year will miss some movies. *TODO: report the match rate.*
- **Cold start:** the model cannot make reliable predictions for new users or new movies.
- **No time awareness:** the model ignores when ratings were given.
- **Next steps:** tune hyperparameters on a sample, train on the full dataset, and try hybrid models that combine genre information with ratings.

## Running the project

```bash
python src/parse_ratings.py    # builds data/processed/ratings.csv
python src/clean_ratings.py    # filters to data/processed/ratings_clean.csv
```

Then run `notebooks/eda.ipynb` in order.