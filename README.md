# Reddit Subreddit Analysis

This project follows the portfolio plan in `Reddit_Analysis_Project_Plan.docx` and turns it into a working Python workflow for collecting, cleaning, analyzing, and exporting Reddit data.

## What this pipeline does

The project pulls posts from six subreddits, combines them into one cleaned dataset, and exports summary CSVs for Tableau.

Tracked subreddits:

- `r/programming`
- `r/learnprogramming`
- `r/cscareerquestions`
- `r/vibecoding`
- `r/Codex`
- `r/ClaudeCode`

## Project structure

```text
.
|-- data/
|   |-- clean/
|   `-- raw/
|-- outputs/
|-- scripts/
|   |-- run_pipeline.py
|   |-- analyze_reddit_data.py
|   |-- clean_reddit_data.py
|   `-- collect_reddit_data.py
|-- docs/
|   `-- HANDOFF.md
|-- .env.example
|-- .gitignore
|-- Makefile
`-- requirements.txt
```

## Setup

1. Create a Reddit application at `https://reddit.com/prefs/apps`.
2. Copy `.env.example` to `.env` and fill in your credentials.
3. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Or use the helper target:

```bash
make setup
```

## Quick start

Run the full workflow:

```bash
make all
```

Or with Python directly:

```bash
.venv/bin/python scripts/run_pipeline.py --with-sentiment
```

## Run the workflow

Collect raw subreddit data:

```bash
python3 scripts/collect_reddit_data.py --limit 500 --time-filter year
```

Clean and combine the raw CSVs:

```bash
python3 scripts/clean_reddit_data.py
```

Create Tableau-ready outputs:

```bash
python3 scripts/analyze_reddit_data.py --with-sentiment
```

Helper commands:

```bash
make collect
make clean
make analyze
make analyze-sentiment
make check
```

## Outputs

- `data/raw/<subreddit>.csv`: raw post-level pulls per subreddit
- `data/clean/reddit_analysis.csv`: cleaned combined dataset
- `data/clean/growth_by_month.csv`: post volume by subreddit and month
- `data/clean/engagement_summary.csv`: subreddit engagement summary
- `data/clean/sentiment_by_month.csv`: optional sentiment trend export
- `outputs/cleaning_report.md`: documented cleaning decisions and quality checks

## Current status

The code and environment are ready. The only blocker is adding Reddit API credentials to `.env` before the live collection step can run.

## Handoff

If someone else needs to continue the work, start with [docs/HANDOFF.md](/Users/sunny/Documents/Reddit_Analysis/docs/HANDOFF.md). It explains the pipeline, current status, exact commands, and what to do next.

## Recommended next steps

1. Add your Reddit API credentials to `.env`, then run the collection script.
2. Review `outputs/cleaning_report.md` after cleaning to confirm the decisions fit your story.
3. Load the CSVs in `data/clean/` into Tableau Public and build the dashboard from the plan.
4. Add the final dashboard screenshot, key finding, and methodology summary to your portfolio.
