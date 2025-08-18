.PHONY: help install test lint format clean build publish d	$(MAKE) test
	$(MAKE) build

security:  ## Run security checksocs

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync

dev-install:  ## Install in development mode
	uv sync --dev
	pre-commit install

test:  ## Run tests
	uv run pytest

test-cov:  ## Run tests with coverage
	uv run pytest --cov=src/detect_commented_terraform --cov-report=html --cov-report=term-missing --cov-report=xml

test-parallel:  ## Run tests in parallel
	uv run pytest -n auto

lint:  ## Run linting
	uv run ruff check src tests
	uv run mypy src

format:  ## Format code
	uv run ruff format src tests

format-check:  ## Check code formatting
	uv run ruff format --check src tests
	uv run ruff check src tests

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf docs/_build/

build:  ## Build package
	uv build

publish:  ## Publish to PyPI
	uv publish

publish-test:  ## Publish to TestPyPI
	uv publish --index-url https://test.pypi.org/simple/

pre-commit:  ## Run pre-commit hooks
	pre-commit run --all-files

check:  ## Run all checks (format, lint, test)
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) build

validate-workflows:  ## Validate GitHub Actions workflows
	@echo "Validating GitHub Actions workflows..."
	@for file in .github/workflows/*.yml; do \
		echo "Checking $$file"; \
		python -c "import yaml; yaml.safe_load(open('$$file'))" || exit 1; \
	done
	@echo "✅ All workflows are valid"

check-security:  ## Run security checks
	uv run bandit -r src/
	uv run safety check

docs:  ## Build documentation
	cd docs && uv run sphinx-build -b html . _build/html

docs-serve:  ## Serve documentation locally
	cd docs && uv run sphinx-autobuild -b html . _build/html

docs-clean:  ## Clean documentation build
	rm -rf docs/_build/
