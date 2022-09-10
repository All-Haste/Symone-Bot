.PHONY: test format fmt lint

PYTHON?=python3

test:
	$(PYTHON) -m pytest $(CURDIR) --cov=$(CURDIR) --cov-report xml
	coverage report --fail-under=99

format:
	$(PYTHON) -m black .

fmt: format

lint:
	$(PYTHON) -m flake8 . --max-complexity=10 --max-line-length=127

coverage-report:
	$(PYTHON) -m pytest . --cov=$(CURDIR) --cov-report html