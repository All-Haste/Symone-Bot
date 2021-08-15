.PHONY: test format fmt lint
test:
	python3 -m pytest

format:
	python3 -m black .

fmt: format

lint:
	flake8 . --max-complexity=10 --max-line-length=127
