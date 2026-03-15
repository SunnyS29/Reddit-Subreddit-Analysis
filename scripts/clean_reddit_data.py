from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DATA_DIR = Path("data/raw")
CLEAN_DATA_DIR = Path("data/clean")
OUTPUTS_DIR = Path("outputs")


def load_raw_data() -> pd.DataFrame:
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No raw CSV files found in data/raw.")

    return pd.concat((pd.read_csv(path) for path in csv_files), ignore_index=True)


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    metrics = {
        "rows_loaded": int(len(df)),
    }

    # Standardize text fields early so grouping and duplicate checks behave consistently.
    df["subreddit"] = df["subreddit"].astype("string").str.strip().str.lower()
    df["title"] = (
        df["title"]
        .astype("string")
        .fillna("")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    df["url"] = df["url"].astype("string").str.strip()
    df["sort_order"] = df["sort_order"].astype("string").str.strip().str.lower()

    df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(0)
    df["num_comments"] = pd.to_numeric(df["num_comments"], errors="coerce").fillna(0)
    df["created_utc"] = pd.to_numeric(df["created_utc"], errors="coerce")
    df["subscriber_count"] = pd.to_numeric(
        df["subscriber_count"], errors="coerce"
    ).fillna(0)

    critical_missing_mask = (
        df["post_id"].isna()
        | df["subreddit"].isna()
        | df["title"].eq("")
        | df["created_utc"].isna()
    )
    metrics["rows_dropped_missing_critical_fields"] = int(critical_missing_mask.sum())
    df = df.loc[~critical_missing_mask].copy()

    # Duplicate posts are expected because the same post can appear in top, hot, and new.
    # We keep the strongest snapshot so later summaries use the most complete engagement stats.
    df = df.sort_values(
        by=["post_id", "score", "num_comments", "collected_at_utc"],
        ascending=[True, False, False, False],
    )
    duplicate_mask = df.duplicated(subset=["post_id"], keep="first")
    metrics["rows_dropped_duplicates"] = int(duplicate_mask.sum())
    df = df.loc[~duplicate_mask].copy()

    df["created_at"] = pd.to_datetime(df["created_utc"], unit="s", utc=True)
    df["month"] = df["created_at"].dt.to_period("M").astype("string")
    df["engagement_ratio"] = df["num_comments"] / (df["score"] + 1)

    score_threshold = df["score"].mean() + (3 * df["score"].std(ddof=0))
    comment_threshold = df["num_comments"].mean() + (3 * df["num_comments"].std(ddof=0))
    df["is_score_outlier"] = df["score"] > score_threshold
    df["is_comment_outlier"] = df["num_comments"] > comment_threshold
    metrics["score_outliers_flagged"] = int(df["is_score_outlier"].sum())
    metrics["comment_outliers_flagged"] = int(df["is_comment_outlier"].sum())
    metrics["rows_remaining"] = int(len(df))

    return df, metrics


def write_cleaning_report(df: pd.DataFrame, metrics: dict[str, int]) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    null_summary = df.isna().sum().sort_values(ascending=False)
    lines = [
        "# Cleaning Report",
        "",
        "## Decisions",
        "",
        "- Standardized subreddit names to lowercase to avoid grouping mismatches.",
        "- Trimmed and normalized title whitespace so text analysis treats equivalent titles the same way.",
        "- Coerced score, comment, subscriber, and timestamp fields to numeric values for reliable calculations.",
        "- Dropped rows missing critical fields (`post_id`, `subreddit`, `title`, `created_utc`) because they cannot support analysis.",
        "- Deduplicated on `post_id` because posts can appear in multiple Reddit listing types.",
        "- Kept the highest-engagement snapshot for duplicated posts to preserve the richest available metrics.",
        "- Added `created_at`, `month`, and `engagement_ratio` for time-series and engagement analysis.",
        "- Flagged score and comment outliers above 3 standard deviations instead of deleting them.",
        "",
        "## Metrics",
        "",
    ]

    for key, value in metrics.items():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Null counts after cleaning",
            "",
        ]
    )
    lines.extend(f"- {column}: {count}" for column, count in null_summary.items())
    lines.extend(
        [
            "",
            "## Dataset coverage",
            "",
            f"- date range: {df['created_at'].min()} to {df['created_at'].max()}",
            f"- subreddits: {', '.join(sorted(df['subreddit'].unique()))}",
        ]
    )

    (OUTPUTS_DIR / "cleaning_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = load_raw_data()
    cleaned_df, metrics = clean_dataframe(df)
    cleaned_df.to_csv(CLEAN_DATA_DIR / "reddit_analysis.csv", index=False)
    write_cleaning_report(cleaned_df, metrics)
    print(f"Saved cleaned dataset with {len(cleaned_df)} rows to data/clean/reddit_analysis.csv")


if __name__ == "__main__":
    main()
