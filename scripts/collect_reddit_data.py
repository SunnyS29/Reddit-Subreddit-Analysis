from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import praw
from dotenv import load_dotenv


DEFAULT_SUBREDDITS = [
    "programming",
    "learnprogramming",
    "cscareerquestions",
    "vibecoding",
    "Codex",
    "ClaudeCode",
]
SORT_ORDERS = ("top", "new", "hot")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Reddit posts for the subreddit analysis project."
    )
    parser.add_argument(
        "--subreddits",
        nargs="+",
        default=DEFAULT_SUBREDDITS,
        help="Subreddits to collect.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Number of posts to request per sort order.",
    )
    parser.add_argument(
        "--time-filter",
        default="year",
        choices=["all", "day", "hour", "month", "week", "year"],
        help="Time filter for the top() listing.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Directory for raw CSV exports.",
    )
    return parser.parse_args()


def build_reddit_client() -> praw.Reddit:
    load_dotenv()

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    missing = [
        key
        for key, value in {
            "REDDIT_CLIENT_ID": client_id,
            "REDDIT_SECRET": client_secret,
            "REDDIT_USER_AGENT": user_agent,
        }.items()
        if not value
    ]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required environment variables: {joined}")

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def fetch_posts(
    reddit: praw.Reddit,
    subreddit_name: str,
    limit: int,
    time_filter: str,
) -> pd.DataFrame:
    subreddit = reddit.subreddit(subreddit_name)
    subscriber_count = subreddit.subscribers
    collected_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, object]] = []

    for sort_order in SORT_ORDERS:
        if sort_order == "top":
            listing = subreddit.top(limit=limit, time_filter=time_filter)
        elif sort_order == "new":
            listing = subreddit.new(limit=limit)
        else:
            listing = subreddit.hot(limit=limit)

        for post in listing:
            rows.append(
                {
                    "post_id": post.id,
                    "subreddit": subreddit_name,
                    "title": post.title,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "created_utc": post.created_utc,
                    "url": post.url,
                    "subscriber_count": subscriber_count,
                    "sort_order": sort_order,
                    "time_filter": time_filter if sort_order == "top" else None,
                    "collected_at_utc": collected_at,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    reddit = build_reddit_client()

    for subreddit_name in args.subreddits:
        subreddit_df = fetch_posts(
            reddit=reddit,
            subreddit_name=subreddit_name,
            limit=args.limit,
            time_filter=args.time_filter,
        )

        output_path = output_dir / f"{subreddit_name}.csv"
        subreddit_df.to_csv(output_path, index=False)
        print(f"Saved {len(subreddit_df)} rows to {output_path}")


if __name__ == "__main__":
    main()
