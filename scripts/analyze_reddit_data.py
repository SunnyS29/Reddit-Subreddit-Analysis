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
CHATGPT_LAUNCH_DATE = pd.Timestamp("2022-11-01", tz="UTC")
BEGINNER_KEYWORDS = [
    "how do i",
    "beginner",
    "help",
    "stuck",
    "confused",
    "new to",
    "just started",
    "learning",
    "noob",
    "advice",
]
AI_REFERENCE_DATES = [
    {
        "event_date": "2022-11-01",
        "event_label": "ChatGPT public launch",
        "event_group": "AI release",
    },
    {
        "event_date": "2023-03-01",
        "event_label": "GPT-4 released",
        "event_group": "AI release",
    },
    {
        "event_date": "2023-03-01",
        "event_label": "Claude launched",
        "event_group": "AI release",
    },
    {
        "event_date": "2024-01-01",
        "event_label": "Cursor mainstream traction",
        "event_group": "Tool adoption",
    },
    {
        "event_date": "2025-01-01",
        "event_label": "Vibe coding mainstream term",
        "event_group": "Cultural shift",
    },
]
SUBREDDIT_METADATA = [
    {
        "subreddit": "programming",
        "analysis_role": "baseline",
        "ai_track": "not_ai_track",
        "series_type": "continuous",
    },
    {
        "subreddit": "learnprogramming",
        "analysis_role": "learning_community",
        "ai_track": "not_ai_track",
        "series_type": "continuous",
    },
    {
        "subreddit": "cscareerquestions",
        "analysis_role": "career_sentiment",
        "ai_track": "not_ai_track",
        "series_type": "continuous",
    },
    {
        "subreddit": "vibecoding",
        "analysis_role": "ai_counterpoint",
        "ai_track": "developer_ai_adoption",
        "series_type": "continuous",
    },
    {
        "subreddit": "chatgpt",
        "analysis_role": "general_ai_adoption",
        "ai_track": "general_ai_adoption",
        "series_type": "continuous",
    },
    {
        "subreddit": "claudeai",
        "analysis_role": "general_ai_adoption",
        "ai_track": "general_ai_adoption",
        "series_type": "continuous",
    },
    {
        "subreddit": "codex",
        "analysis_role": "developer_ai_adoption",
        "ai_track": "developer_ai_adoption",
        "series_type": "discontinuous",
    },
    {
        "subreddit": "claudecode",
        "analysis_role": "developer_ai_adoption",
        "ai_track": "developer_ai_adoption",
        "series_type": "discontinuous",
    },
]


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


def enrich_analysis_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    beginner_pattern = "|".join(BEGINNER_KEYWORDS)
    df["is_beginner_post"] = (
        df["title"].astype("string").str.lower().str.contains(beginner_pattern, na=False)
    )
    df["period_relative_to_chatgpt"] = df["created_at"].apply(
        lambda value: "after_chatgpt_launch"
        if value >= CHATGPT_LAUNCH_DATE
        else "before_chatgpt_launch"
    )
    metadata_df = pd.DataFrame(SUBREDDIT_METADATA)
    df = df.merge(metadata_df, on="subreddit", how="left")
    return df


def export_growth(df: pd.DataFrame) -> None:
    growth = (
        df.groupby(["subreddit", "month"], as_index=False)
        .size()
        .rename(columns={"size": "post_count"})
        .sort_values(["subreddit", "month"])
    )
    growth.to_csv(CLEAN_OUTPUT_DIR / "growth_by_month.csv", index=False)


def export_beginner_trend(df: pd.DataFrame) -> None:
    beginner_trend = (
        df.loc[df["is_beginner_post"]]
        .groupby(["subreddit", "month"], as_index=False)
        .size()
        .rename(columns={"size": "beginner_post_count"})
        .sort_values(["subreddit", "month"])
    )
    beginner_trend.to_csv(CLEAN_OUTPUT_DIR / "beginner_activity_by_month.csv", index=False)


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


def export_engagement_pre_post(df: pd.DataFrame) -> None:
    engagement_pre_post = (
        df.groupby(["subreddit", "period_relative_to_chatgpt"], as_index=False)
        .agg(
            avg_score=("score", "mean"),
            avg_comments=("num_comments", "mean"),
            avg_engagement_ratio=("engagement_ratio", "mean"),
            total_posts=("post_id", "count"),
        )
        .sort_values(["subreddit", "period_relative_to_chatgpt"])
    )
    engagement_pre_post.to_csv(
        CLEAN_OUTPUT_DIR / "engagement_pre_post_chatgpt.csv", index=False
    )


def export_reference_dates() -> None:
    reference_dates = pd.DataFrame(AI_REFERENCE_DATES)
    reference_dates["event_date"] = pd.to_datetime(reference_dates["event_date"])
    reference_dates.to_csv(CLEAN_OUTPUT_DIR / "ai_reference_dates.csv", index=False)


def export_subreddit_metadata() -> None:
    metadata_df = pd.DataFrame(SUBREDDIT_METADATA)
    metadata_df.to_csv(CLEAN_OUTPUT_DIR / "subreddit_metadata.csv", index=False)


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
    df = enrich_analysis_columns(load_clean_data())
    df.to_csv(CLEAN_DATA_PATH, index=False)
    export_growth(df)
    export_beginner_trend(df)
    export_engagement(df)
    export_engagement_pre_post(df)
    export_reference_dates()
    export_subreddit_metadata()

    if args.with_sentiment:
        export_sentiment(df)

    print("Saved analysis outputs to data/clean/")


if __name__ == "__main__":
    main()
