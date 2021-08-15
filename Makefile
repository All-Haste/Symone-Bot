.PHONY: test format fmt
test:
	python3 -m pytest

format:
	python3 -m black .

fmt: format
