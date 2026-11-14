import csv

def parse_netflix_ratings(in_path, out_path):
    current_movie = None
    count = 0
    with open(in_path, "r") as f, open(out_path, "w", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["user_id", "movie_id", "rating", "date"])
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.endswith(":"):
                current_movie = int(line[:-1])
            else:
                user_id, rating, date = line.split(",")
                writer.writerow([user_id, current_movie, rating, date])
                count += 1
    print(f"Wrote {count:,} ratings to {out_path}")

if __name__ == "__main__":
    parse_netflix_ratings("data/raw/combined_data_1.txt",
                          "data/processed/ratings.csv")