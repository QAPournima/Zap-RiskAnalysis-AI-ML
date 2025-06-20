.PHONY: help install install-dev run test clean lint format check build docs

# Default target
help:
	@echo "ML Risk Analysis Dashboard - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  run          Run the dashboard server"
	@echo "  test         Run tests"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black"
	@echo "  check        Run all checks (lint + test)"
	@echo "  build        Build distribution packages"
	@echo "  clean        Clean build artifacts"
	@echo "  docs         Generate documentation"
	@echo "  setup-env    Setup virtual environment"

# Environment setup
setup-env:
	python -m venv venv_local
	@echo "Virtual environment created. Run: source venv_local/bin/activate"

# Install dependencies
install:
	pip install -r requirements/requirements_webapp.txt

install-dev: install
	pip install -r requirements/requirements.txt
	pip install -e .

# Run application
run:
	python run.py

# Testing
test:
	python -m pytest src/tests/ -v

# Code quality
lint:
	flake8 src/
	mypy src/

format:
	black src/
	black run.py setup.py

check: lint test
	@echo "All checks passed!"

# Build and distribution
build: clean
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Documentation
docs:
	@echo "Documentation available in docs/ directory"
	@echo "Main documentation: README.md"

# Development utilities
dev-setup: setup-env install-dev
	@echo "Development environment ready!"
	@echo "Run 'make run' to start the dashboard"

# Docker commands (if needed in future)
docker-build:
	docker build -t ml-risk-analysis .

docker-run:
	docker run -p 5001:5001 ml-risk-analysis 