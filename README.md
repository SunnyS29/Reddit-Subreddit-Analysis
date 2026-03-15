# Reddit Subreddit Analysis
### How programming communities shifted when AI tools went mainstream

I wanted to know if the rise of AI coding tools actually changed how developers use Reddit, and whether communities like `r/learnprogramming` slowed down as newer AI-focused spaces took off.

This project collects, cleans, and analyses post-level data across six subreddits to find out.

---

## Subreddits tracked

- `r/programming` - the established baseline
- `r/learnprogramming` - traditional learning community
- `r/cscareerquestions` - career sentiment indicator
- `r/vibecoding` - AI-assisted, new wave
- `r/Codex` - coding assistant community
- `r/ClaudeCode` - alternative AI coding assistant community

---

## What the pipeline does

Pulls posts from each subreddit, cleans and combines them, then exports summary CSVs ready for Tableau.

```text
data/raw/<subreddit>.csv          raw post-level data per subreddit
data/clean/reddit_analysis.csv    cleaned combined dataset
data/clean/growth_by_month.csv    post volume by subreddit and month
data/clean/engagement_summary.csv subreddit engagement metrics
data/clean/sentiment_by_month.csv sentiment trends over time (optional)
outputs/cleaning_report.md        documented cleaning decisions
```

---

## Setup

1. Get Reddit API credentials at `https://reddit.com/prefs/apps`
2. Copy `.env.example` to `.env` and fill in your details
3. Install dependencies:

```bash
make setup
# or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run it

Full pipeline in one command:

```bash
make all
```

Or step by step:

```bash
python3 scripts/collect_reddit_data.py --limit 500 --time-filter year
python3 scripts/clean_reddit_data.py
python3 scripts/analyze_reddit_data.py --with-sentiment
```

---

## Current status

Code and environment are ready. Waiting on Reddit API credentials before live collection can run.

In the meantime, a dataset with the same column structure can be dropped into `data/raw/` to run the rest of the pipeline.

---

## Project structure

```text
.
|-- data/
|   |-- raw/
|   `-- clean/
|-- outputs/
|-- scripts/
|   |-- collect_reddit_data.py
|   |-- clean_reddit_data.py
|   |-- analyze_reddit_data.py
|   `-- run_pipeline.py
|-- docs/
|   `-- HANDOFF.md
|-- .env.example
|-- Makefile
`-- requirements.txt
```

---

Built as a portfolio project. Dashboard and write-up coming once the data collection is done.
[sunnysangar.com](https://sunnysangar.com)
