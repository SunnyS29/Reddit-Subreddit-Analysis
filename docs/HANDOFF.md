# Handoff Guide

## Project goal

Measure how programming-focused Reddit communities changed as AI-assisted coding communities grew, then export the results for Tableau.

## Current status

- Project structure is in place.
- Python dependencies are installed in `.venv`.
- Collection defaults now target `r/Codex` and `r/ClaudeCode`.
- Live data collection has not run yet because `.env` does not contain Reddit API credentials.

## Fastest way to resume

1. Copy `.env.example` to `.env`.
2. Add `REDDIT_CLIENT_ID`, `REDDIT_SECRET`, and `REDDIT_USER_AGENT`.
3. Run `make all`.

## What each step does

### 1. Collect

Command:

```bash
make collect
```

Script: `scripts/collect_reddit_data.py`

What it does:

- Connects to Reddit using PRAW
- Pulls posts from `top`, `new`, and `hot`
- Saves one CSV per subreddit in `data/raw/`

### 2. Clean

Command:

```bash
make clean
```

Script: `scripts/clean_reddit_data.py`

What it does:

- Combines all raw CSV files
- Standardizes columns and types
- Drops incomplete rows
- Deduplicates repeated posts across listing types
- Creates derived fields like `created_at`, `month`, and `engagement_ratio`
- Writes `data/clean/reddit_analysis.csv`
- Writes `outputs/cleaning_report.md`

### 3. Analyze

Command:

```bash
make analyze-sentiment
```

Script: `scripts/analyze_reddit_data.py`

What it does:

- Creates monthly post-volume output for growth charts
- Creates subreddit-level engagement summary output
- Optionally calculates title sentiment with TextBlob
- Writes Tableau-ready CSVs to `data/clean/`

## One-command run

Command:

```bash
make all
```

This calls `scripts/run_pipeline.py`, which runs collect, clean, and analyze in order.

## Important files

- `scripts/collect_reddit_data.py`: Reddit API pull
- `scripts/clean_reddit_data.py`: data cleaning and QA
- `scripts/analyze_reddit_data.py`: summary exports
- `scripts/run_pipeline.py`: end-to-end wrapper
- `README.md`: setup and usage
- `outputs/cleaning_report.md`: cleaning decisions after a successful run

## Troubleshooting

- If collection fails immediately, check whether `.env` exists and has valid credentials.
- If `make` says `.venv/bin/python` is missing, run `make setup`.
- If sentiment analysis fails, rerun `make setup` to ensure `textblob` is installed.
- If there is no output in `data/raw/`, the collection step did not complete successfully.

## Suggested next deliverables after data is collected

1. Review `outputs/cleaning_report.md` for cleaning choices and anomalies.
2. Inspect `data/clean/growth_by_month.csv` and `data/clean/engagement_summary.csv`.
3. Build the Tableau dashboard.
4. Write the portfolio summary and findings.
