PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup collect clean analyze analyze-sentiment all check

setup:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

collect:
	$(PYTHON) scripts/collect_reddit_data.py --limit 500 --time-filter year

clean:
	$(PYTHON) scripts/clean_reddit_data.py

analyze:
	$(PYTHON) scripts/analyze_reddit_data.py

analyze-sentiment:
	$(PYTHON) scripts/analyze_reddit_data.py --with-sentiment

all:
	$(PYTHON) scripts/run_pipeline.py --with-sentiment

check:
	PYTHONPYCACHEPREFIX=.pycache $(PYTHON) -m py_compile scripts/*.py
