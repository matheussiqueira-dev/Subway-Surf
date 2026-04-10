.PHONY: help install install-dev run run-api run-all lint fmt type-check test test-cov clean

PYTHON  ?= python
PYTEST  ?= pytest
RUFF    ?= ruff
MYPY    ?= mypy

help:           ## Show this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
install:        ## Install production dependencies.
	$(PYTHON) -m pip install -r requirements.txt

install-dev:    ## Install all dev + production dependencies.
	$(PYTHON) -m pip install -r requirements-dev.txt

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
run:            ## Start the gesture controller (camera required).
	$(PYTHON) main.py --mode controller

run-api:        ## Start the REST API + dashboard only.
	$(PYTHON) main.py --mode api

run-all:        ## Start controller + API simultaneously.
	$(PYTHON) main.py --mode all

# ---------------------------------------------------------------------------
# Quality gates
# ---------------------------------------------------------------------------
lint:           ## Run ruff linter.
	$(RUFF) check src tests main.py

fmt:            ## Auto-format with ruff.
	$(RUFF) format src tests main.py
	$(RUFF) check --fix src tests main.py

type-check:     ## Run mypy in strict mode.
	$(MYPY) src main.py

test:           ## Run the test suite.
	$(PYTEST) tests/

test-cov:       ## Run tests with HTML coverage report.
	$(PYTEST) --cov=src --cov-report=term-missing --cov-report=html tests/

# ---------------------------------------------------------------------------
# Housekeeping
# ---------------------------------------------------------------------------
clean:          ## Remove build artefacts and caches.
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov     -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
