.PHONY: test format fmt lint coverage-report check

PYTHON?=python3

test:
	$(PYTHON) -m pytest $(CURDIR) --cov=$(CURDIR) --cov-report xml
	coverage report --fail-under=90

format:
	$(PYTHON) -m black .

fmt: format

lint:
	$(PYTHON) -m flake8 . --max-complexity=10 --max-line-length=127

coverage-report:
	$(PYTHON) -m pytest . --cov=$(CURDIR) --cov-report html

check: format lint test
