# Makefile for Disk Monitor Python Project
# Engineered by Andreas Huemmer [andreas.huemmer@adminsend.de]

.PHONY: help install install-dev test lint format type-check clean build upload venv activate

# Default target
help:
	@echo "Disk Monitor - Python Development Framework"
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  venv         - Create virtual environment"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests with pytest"
	@echo "  lint         - Run flake8 linting"
	@echo "  format       - Format code with black and isort"
	@echo "  type-check   - Run mypy type checking"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  check        - Run all quality checks (lint, type-check, test)"
	@echo "  run          - Run the disk monitor application"

# Virtual environment management
venv:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

activate:
	@echo "To activate virtual environment, run:"
	@echo "source venv/bin/activate"

# Installation targets
install:
	@echo "Installing production dependencies..."
	pip install -e .

install-dev:
	@echo "Installing development dependencies..."
	pip install -e ".[dev,test]"
	pip install -r requirements-dev.txt

# Testing
test:
	@echo "Running tests with pytest..."
	python -m pytest tests/ -v --tb=short

test-cov:
	@echo "Running tests with coverage..."
	python -m pytest tests/ --cov=disk_monitor --cov-report=html --cov-report=term

# Code quality
lint:
	@echo "Running flake8 linting..."
	python -m flake8 disk_monitor/ tests/

format:
	@echo "Formatting code with black..."
	python -m black disk_monitor/ tests/
	@echo "Sorting imports with isort..."
	python -m isort disk_monitor/ tests/

type-check:
	@echo "Running mypy type checking..."
	python -m mypy disk_monitor/

# Combined quality check
check: lint type-check test
	@echo "All quality checks completed successfully!"

# Build and distribution
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	@echo "Building distribution packages..."
	python -m build

# Application execution
run:
	@echo "Running disk monitor..."
	python -m disk_monitor

run-net:
	@echo "Running disk monitor with network drives..."
	python -m disk_monitor --net

run-fast:
	@echo "Running disk monitor with 1-second refresh..."
	python -m disk_monitor --time 1

# Development workflow
dev-setup: venv install-dev
	@echo "Development environment setup complete!"
	@echo "Activate with: source venv/bin/activate"

# Validation for Python framework requirements
validate-python:
	@echo "Validating Python version (requires 3.8+)..."
	@python3 -c "import sys; assert sys.version_info >= (3, 8), f'Python 3.8+ required, got {sys.version_info[:2]}'"
	@echo "Python version validation passed!"

validate-project:
	@echo "Validating project structure..."
	@test -f pyproject.toml || (echo "Missing pyproject.toml" && exit 1)
	@test -f requirements.txt || (echo "Missing requirements.txt" && exit 1)
	@test -d disk_monitor || (echo "Missing disk_monitor package" && exit 1)
	@test -d tests || (echo "Missing tests directory" && exit 1)
	@echo "Project structure validation passed!"

validate: validate-python validate-project
	@echo "All validations passed!"