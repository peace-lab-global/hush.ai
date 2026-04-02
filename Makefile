.PHONY: install dev fmt lint typecheck test check build clean

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e .

dev:
	$(PYTHON) -m pip install -e ".[dev]"

fmt:
	$(PYTHON) -m ruff format hushai tests

lint:
	$(PYTHON) -m ruff check hushai tests

typecheck:
	$(PYTHON) -m mypy hushai

test:
	$(PYTHON) -m pytest -v --cov=hushai --cov-report=term-missing --cov-fail-under=70

check: lint
	$(PYTHON) -m ruff format --check hushai tests
	$(MAKE) typecheck
	$(MAKE) test

build:
	$(PYTHON) -m pip install -U build twine
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml htmlcov
