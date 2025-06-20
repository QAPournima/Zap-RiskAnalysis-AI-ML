# ML Risk Analysis Dashboard - Development Makefile

.PHONY: help install install-dev run test lint format clean setup check-env

# Default target
help:  ## Show this help message
	@echo "ML Risk Analysis Dashboard - Development Commands"
	@echo "=================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Environment setup
setup:  ## Set up development environment
	python3 -m venv venv_local
	. venv_local/bin/activate && pip install --upgrade pip setuptools wheel
	. venv_local/bin/activate && pip install -e ".[dev]"
	@echo "✅ Development environment set up successfully!"
	@echo "Run 'source venv_local/bin/activate' to activate the environment"

# Installation
install:  ## Install package for production
	pip install -r requirements/requirements_webapp.txt

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

# Running the application
run:  ## Start the dashboard application
	python run.py

run-dev:  ## Start the dashboard in development mode
	FLASK_ENV=development python run.py

# Testing
test:  ## Run all tests
	pytest src/tests/ -v

test-cov:  ## Run tests with coverage report
	pytest src/tests/ --cov=src/ml_bug_prediction --cov-report=html --cov-report=term-missing

# Code quality
lint:  ## Run linting checks
	flake8 src/ scripts/
	mypy src/ml_bug_prediction/

format:  ## Format code with black and isort
	black src/ scripts/
	isort src/ scripts/

format-check:  ## Check code formatting without making changes
	black --check src/ scripts/
	isort --check-only src/ scripts/

# Utilities
clean:  ## Clean up build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

check-env:  ## Check if required environment variables are set
	python scripts/setup_environment.py

# JIRA connection
test-jira:  ## Test JIRA connection
	python scripts/test_jira_connection.py

# Build and distribution
build:  ## Build the package
	python -m build

build-wheel:  ## Build wheel distribution
	python -m build --wheel

install-local:  ## Install the package locally in development mode
	pip install -e .

# Docker support (future)
docker-build:  ## Build Docker image
	@echo "Docker support coming soon..."

docker-run:  ## Run application in Docker
	@echo "Docker support coming soon..."

# Documentation
docs:  ## Generate documentation
	@echo "Documentation generation coming soon..."

# Development workflow
dev-setup: setup install-dev  ## Complete development setup
	@echo "🚀 Development environment ready!"
	@echo "💡 Run 'make run' to start the dashboard"

dev-check: format-check lint test  ## Run all development checks
	@echo "✅ All development checks passed!"

# Project structure
structure:  ## Show project structure
	@echo "Current project structure:"
	@tree -I 'venv_local|__pycache__|*.pyc|.git|node_modules' -a

# Quick start
quick-start:  ## Quick start guide
	@echo "🚀 ML Risk Analysis Dashboard - Quick Start"
	@echo "=============================================="
	@echo ""
	@echo "1. Set up development environment:"
	@echo "   make dev-setup"
	@echo ""
	@echo "2. Activate virtual environment:"
	@echo "   source venv_local/bin/activate"
	@echo ""
	@echo "3. Start the dashboard:"
	@echo "   make run"
	@echo ""
	@echo "4. Open browser:"
	@echo "   http://localhost:5001"
	@echo ""
	@echo "For more commands, run: make help" 