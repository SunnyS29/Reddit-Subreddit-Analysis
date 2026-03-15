from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from textblob import TextBlob
except ImportError:  # pragma: no cover
    TextBlob = None


CLEAN_DATA_PATH = Path("data/clean/reddit_analysis.csv")
CLEAN_OUTPUT_DIR = Path("data/clean")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create analysis exports for the Reddit subreddit analysis project."
    )
    parser.add_argument(
        "--with-sentiment",
        action="store_true",
        help="Calculate title sentiment using TextBlob.",
    )
    return parser.parse_args()


def load_clean_data() -> pd.DataFrame:
    if not CLEAN_DATA_PATH.exists():
        raise FileNotFoundError(
            "Clean dataset not found. Run scripts/clean_reddit_data.py first."
        )

    df = pd.read_csv(CLEAN_DATA_PATH, parse_dates=["created_at"])
    df["month"] = df["month"].astype("string")
    return df


def export_growth(df: pd.DataFrame) -> None:
    growth = (
        df.groupby(["subreddit", "month"], as_index=False)
        .size()
        .rename(columns={"size": "post_count"})
        .sort_values(["subreddit", "month"])
    )
    growth.to_csv(CLEAN_OUTPUT_DIR / "growth_by_month.csv", index=False)


def export_engagement(df: pd.DataFrame) -> None:
    engagement = (
        df.groupby("subreddit", as_index=False)
        .agg(
            avg_score=("score", "mean"),
            avg_comments=("num_comments", "mean"),
            avg_engagement_ratio=("engagement_ratio", "mean"),
            median_score=("score", "median"),
            total_posts=("post_id", "count"),
            avg_subscriber_count=("subscriber_count", "mean"),
        )
        .sort_values("avg_score", ascending=False)
    )
    engagement.to_csv(CLEAN_OUTPUT_DIR / "engagement_summary.csv", index=False)


def export_sentiment(df: pd.DataFrame) -> None:
    if TextBlob is None:
        raise RuntimeError(
            "TextBlob is not installed. Install dependencies before running sentiment analysis."
        )

    df = df.copy()
    df["sentiment"] = df["title"].apply(
        lambda title: TextBlob(str(title)).sentiment.polarity
    )
    sentiment = (
        df.groupby(["subreddit", "month"], as_index=False)["sentiment"]
        .mean()
        .sort_values(["subreddit", "month"])
    )
    sentiment.to_csv(CLEAN_OUTPUT_DIR / "sentiment_by_month.csv", index=False)


def main() -> None:
    args = parse_args()
    CLEAN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_clean_data()
    export_growth(df)
    export_engagement(df)

    if args.with_sentiment:
        export_sentiment(df)

    print("Saved analysis outputs to data/clean/")


if __name__ == "__main__":
    main()
