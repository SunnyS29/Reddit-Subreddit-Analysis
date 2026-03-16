from __future__ import annotations

import argparse
import random
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


SUBREDDIT_CONFIG = {
    "programming": {
        "subscriber_count": 5200000,
        "monthly_posts": 24,
        "beginner_probability": 0.10,
        "base_score": 220,
        "base_comments": 32,
        "start": "2021-01-01",
    },
    "learnprogramming": {
        "subscriber_count": 4600000,
        "monthly_posts": 28,
        "beginner_probability": 0.60,
        "base_score": 120,
        "base_comments": 26,
        "start": "2021-01-01",
    },
    "cscareerquestions": {
        "subscriber_count": 1800000,
        "monthly_posts": 20,
        "beginner_probability": 0.18,
        "base_score": 105,
        "base_comments": 34,
        "start": "2021-01-01",
    },
    "vibecoding": {
        "subscriber_count": 140000,
        "monthly_posts": 16,
        "beginner_probability": 0.48,
        "base_score": 88,
        "base_comments": 18,
        "start": "2024-10-01",
    },
    "ChatGPT": {
        "subscriber_count": 520000,
        "monthly_posts": 22,
        "beginner_probability": 0.25,
        "base_score": 135,
        "base_comments": 28,
        "start": "2022-11-01",
    },
    "ClaudeAI": {
        "subscriber_count": 210000,
        "monthly_posts": 18,
        "beginner_probability": 0.22,
        "base_score": 118,
        "base_comments": 22,
        "start": "2023-03-01",
    },
    "Codex": {
        "subscriber_count": 95000,
        "monthly_posts": 14,
        "beginner_probability": 0.22,
        "base_score": 92,
        "base_comments": 17,
        "start": "2024-06-01",
    },
    "ClaudeCode": {
        "subscriber_count": 72000,
        "monthly_posts": 12,
        "beginner_probability": 0.20,
        "base_score": 86,
        "base_comments": 16,
        "start": "2024-10-01",
    },
}

SORT_ORDERS = ("top", "new", "hot")
COLLECTED_AT = "2026-03-16T00:00:00+00:00"
BEGINNER_TEMPLATES = [
    "How do I start learning Python as a beginner?",
    "New to coding and stuck on my first project",
    "Beginner question: how do I debug this loop?",
    "Just started programming and need advice",
    "Help, I am confused about functions and classes",
    "Noob question about APIs and JSON parsing",
]
GENERAL_TEMPLATES = [
    "Best practices for structuring a growing codebase",
    "Interesting discussion about software architecture tradeoffs",
    "Tooling setup that improved my developer workflow",
    "What changed your approach to debugging this year?",
    "Thoughts on typed languages versus fast iteration",
    "Showcase: side project lessons after shipping version one",
]
CAREER_TEMPLATES = [
    "How is the job market feeling for junior developers right now?",
    "Career advice after getting rejected from multiple roles",
    "What skills matter most for landing an entry-level data job?",
    "Feeling optimistic after finally getting interviews again",
]
AI_TEMPLATES = [
    "Using AI to scaffold a weekend project from scratch",
    "Prompting workflow that helped me ship faster this week",
    "How much coding are you still doing by hand?",
    "What AI coding habits actually save time long term?",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate mock Reddit raw CSVs for pipeline testing."
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Directory where raw CSVs should be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible mock data.",
    )
    parser.add_argument(
        "--end-month",
        default="2026-02-01",
        help="Last month to include in YYYY-MM-DD form.",
    )
    return parser.parse_args()


def month_range(start: str, end: str) -> list[pd.Timestamp]:
    return list(pd.date_range(start=start, end=end, freq="MS", tz="UTC"))


def title_for_subreddit(subreddit: str, is_beginner: bool, rng: random.Random) -> str:
    if subreddit == "cscareerquestions":
        templates = CAREER_TEMPLATES
    elif subreddit in {"vibecoding", "ChatGPT", "ClaudeAI", "Codex", "ClaudeCode"}:
        templates = AI_TEMPLATES + BEGINNER_TEMPLATES
    else:
        templates = BEGINNER_TEMPLATES if is_beginner else GENERAL_TEMPLATES

    title = rng.choice(templates)
    if subreddit == "vibecoding":
        title = f"{title} with AI pair programming"
    elif subreddit == "ChatGPT":
        title = f"{title} with ChatGPT"
    elif subreddit == "ClaudeAI":
        title = f"{title} with Claude"
    elif subreddit == "Codex":
        title = f"{title} using Codex"
    elif subreddit == "ClaudeCode":
        title = f"{title} in Claude Code"
    return title


def monthly_volume_multiplier(subreddit: str, month: pd.Timestamp) -> float:
    if subreddit == "learnprogramming":
        return 1.15 if month < pd.Timestamp("2022-11-01", tz="UTC") else 0.78
    if subreddit == "vibecoding":
        return 0.15 if month < pd.Timestamp("2025-01-01", tz="UTC") else 1.45
    if subreddit == "ChatGPT":
        return 0.35 if month < pd.Timestamp("2023-01-01", tz="UTC") else 1.65
    if subreddit == "ClaudeAI":
        return 0.20 if month < pd.Timestamp("2024-01-01", tz="UTC") else 1.30
    if subreddit == "Codex":
        return 0.35 if month < pd.Timestamp("2025-01-01", tz="UTC") else 1.25
    if subreddit == "ClaudeCode":
        return 0.30 if month < pd.Timestamp("2025-01-01", tz="UTC") else 1.20
    if subreddit == "cscareerquestions":
        return 1.10 if month >= pd.Timestamp("2023-01-01", tz="UTC") else 0.95
    return 1.0


def beginner_probability(subreddit: str, month: pd.Timestamp, base_probability: float) -> float:
    if subreddit == "learnprogramming" and month >= pd.Timestamp("2022-11-01", tz="UTC"):
        return max(0.18, base_probability - 0.18)
    if subreddit == "vibecoding" and month >= pd.Timestamp("2025-01-01", tz="UTC"):
        return min(0.75, base_probability + 0.20)
    return base_probability


def messy_subreddit_value(subreddit: str, rng: random.Random) -> str:
    if rng.random() < 0.08:
        return f" {subreddit.upper()} "
    if rng.random() < 0.08:
        return subreddit.upper()
    return subreddit


def messy_sort_order(sort_order: str, rng: random.Random) -> str:
    if rng.random() < 0.15:
        return sort_order.upper()
    return sort_order


def generate_subreddit_rows(
    subreddit: str,
    config: dict[str, object],
    end_month: str,
    rng: random.Random,
) -> list[dict[str, object]]:
    months = month_range(str(config["start"]), end_month)
    rows: list[dict[str, object]] = []
    logical_post_counter = 0

    for month in months:
        monthly_posts = max(
            2,
            int(round(int(config["monthly_posts"]) * monthly_volume_multiplier(subreddit, month))),
        )

        for _ in range(monthly_posts):
            logical_post_counter += 1
            post_id = f"{subreddit.lower()}_{month.strftime('%Y%m')}_{logical_post_counter:04d}"
            is_beginner = rng.random() < beginner_probability(
                subreddit,
                month,
                float(config["beginner_probability"]),
            )
            title = title_for_subreddit(subreddit, is_beginner, rng)
            created_at = month + pd.Timedelta(days=rng.randint(0, 27), hours=rng.randint(0, 23))
            created_utc = created_at.timestamp()
            score_base = int(config["base_score"])
            comment_base = int(config["base_comments"])

            if subreddit in {
                "vibecoding",
                "ChatGPT",
                "ClaudeAI",
                "Codex",
                "ClaudeCode",
            } and month >= pd.Timestamp(
                "2025-01-01", tz="UTC"
            ):
                score_base += 35
                comment_base += 8
            if subreddit == "learnprogramming" and month >= pd.Timestamp("2022-11-01", tz="UTC"):
                score_base -= 15
                comment_base -= 4

            score = max(1, int(rng.gauss(score_base, score_base * 0.30)))
            num_comments = max(0, int(rng.gauss(comment_base, max(4, comment_base * 0.35))))
            url = f"https://reddit.com/r/{subreddit}/comments/{post_id}"
            snapshots = rng.sample(SORT_ORDERS, k=rng.randint(2, 3))

            for index, sort_order in enumerate(snapshots):
                snapshot_score = max(1, score - (len(snapshots) - index - 1) * rng.randint(0, 8))
                snapshot_comments = max(
                    0,
                    num_comments - (len(snapshots) - index - 1) * rng.randint(0, 4),
                )
                rows.append(
                    {
                        "post_id": post_id,
                        "subreddit": messy_subreddit_value(subreddit, rng),
                        "title": "" if rng.random() < 0.02 else title,
                        "score": "" if rng.random() < 0.03 else snapshot_score,
                        "num_comments": "N/A"
                        if rng.random() < 0.03
                        else snapshot_comments,
                        "created_utc": created_utc,
                        "url": url,
                        "subscriber_count": int(config["subscriber_count"]),
                        "sort_order": messy_sort_order(sort_order, rng),
                        "time_filter": "year" if sort_order == "top" else "",
                        "collected_at_utc": COLLECTED_AT,
                    }
                )

    return rows


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for existing_csv in output_dir.glob("*.csv"):
        existing_csv.unlink()

    for subreddit, config in SUBREDDIT_CONFIG.items():
        rows = generate_subreddit_rows(subreddit, config, args.end_month, rng)
        df = pd.DataFrame(rows)
        output_path = output_dir / f"{subreddit}.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved mock data for r/{subreddit}: {len(df)} rows -> {output_path}")


if __name__ == "__main__":
    main()
