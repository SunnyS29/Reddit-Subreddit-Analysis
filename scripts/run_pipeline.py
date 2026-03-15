from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Reddit analysis pipeline end to end."
    )
    parser.add_argument(
        "--with-sentiment",
        action="store_true",
        help="Include TextBlob title sentiment analysis in the final export step.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Number of posts to request per subreddit listing.",
    )
    parser.add_argument(
        "--time-filter",
        default="year",
        choices=["all", "day", "hour", "month", "week", "year"],
        help="Time filter to use for Reddit top posts.",
    )
    return parser.parse_args()


def run_step(args: list[str], label: str) -> None:
    print(f"\n=== {label} ===")
    subprocess.run(
        [sys.executable, *args],
        check=True,
        cwd=PROJECT_ROOT,
    )


def main() -> None:
    args = parse_args()

    run_step(
        [
            "scripts/collect_reddit_data.py",
            "--limit",
            str(args.limit),
            "--time-filter",
            args.time_filter,
        ],
        "Collecting Reddit data",
    )
    run_step(["scripts/clean_reddit_data.py"], "Cleaning raw data")

    analysis_args = ["scripts/analyze_reddit_data.py"]
    if args.with_sentiment:
        analysis_args.append("--with-sentiment")
    run_step(analysis_args, "Creating analysis outputs")

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
