.PHONY: test format fmt
PYTHON?=python3

test:
	$(PYTHON) -m pytest

format:
	$(PYTHON) -m black .

fmt: format
