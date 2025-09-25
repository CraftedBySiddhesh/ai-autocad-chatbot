SHELL := /bin/bash
PYTHON ?= python
PIP_COMPILE ?= pip-compile

.PHONY: setup lint type test fix lock clean

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-dev.txt

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .

type:
	$(PYTHON) -m mypy app

fix:
	$(PYTHON) -m isort .
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check . --fix

lock:
	$(PIP_COMPILE) --resolver=backtracking --upgrade -c constraints.txt -o requirements.txt requirements.in
	$(PIP_COMPILE) --resolver=backtracking --upgrade -c constraints.txt -o requirements-dev.txt requirements-dev.in

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache dist build

test:
	$(PYTHON) -m pytest
