.PHONY: help install test coverage clean lint format build upload
.DEFAULT_GOAL := help

PYTHON := .venv/bin/python

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies and package in development mode
	pip install -r dev_requirements.txt
	pip install -e .

test: ## Run tests
	$(PYTHON) -m pytest -v tests/

coverage: ## Run tests with coverage report
	$(PYTHON) -m pytest --cov=src/crossmark_jotform_api --cov-report=term-missing --cov-report=html --cov-report=xml --cov-branch -v tests/

coverage-html: coverage ## Run coverage and open HTML report
	@command -v xdg-open >/dev/null 2>&1 && xdg-open htmlcov/index.html || \
	command -v open >/dev/null 2>&1 && open htmlcov/index.html || \
	echo "Please open htmlcov/index.html in your browser"

clean: ## Clean up build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -f coverage.xml
	rm -f .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

lint: ## Run linting checks
	@echo "This project doesn't have linting configured yet"
	@echo "Consider adding flake8, black, isort, etc."

format: ## Format code
	@echo "This project doesn't have code formatting configured yet"
	@echo "Consider adding black, autopep8, etc."

build: clean ## Build the package
	python -m build

upload: build ## Upload to PyPI (requires credentials)
	python -m twine upload dist/*

upload-test: build ## Upload to TestPyPI (requires credentials)
	python -m twine upload --repository testpypi dist/*

# Development helpers
dev-install: ## Install package in development mode with all extras
	pip install -e ".[dev]"
	
test-quick: ## Run tests without coverage (faster)
	pytest -x --tb=short

test-verbose: ## Run tests with maximum verbosity
	pytest -vv --tb=long

# CI/CD helpers
ci-test: ## Run tests as they would run in CI
	$(PYTHON) -m pytest --cov=src/crossmark_jotform_api --cov-report=xml --cov-branch --cov-fail-under=50 tests/

ci-coverage: ## Generate coverage report for CI with minimum threshold
	$(PYTHON) -m coverage run -m pytest tests/
	$(PYTHON) -m coverage xml
	$(PYTHON) -m coverage report --fail-under=50

coverage-badge: ## Generate coverage badge (requires coverage-badge package)
	@echo "To generate coverage badge, install: pip install coverage-badge"
	@echo "Then run: coverage-badge -o coverage.svg"