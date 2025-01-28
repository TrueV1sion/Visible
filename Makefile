.PHONY: help setup install test lint format clean docker-build docker-up docker-down

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Set up development environment
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	python -c "import nltk; nltk.download('punkt')"
	python -m spacy download en_core_web_sm

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests with coverage
	pytest tests/ --cov=ai_orchestration --cov-report=term-missing

lint: ## Run linting checks
	flake8 ai_orchestration
	pylint ai_orchestration
	mypy ai_orchestration

format: ## Format code
	black ai_orchestration
	isort ai_orchestration

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

logs: ## View Docker container logs
	docker-compose logs -f

shell: ## Open a shell in the API container
	docker-compose exec api /bin/bash

jupyter: ## Open Jupyter Lab
	docker-compose exec jupyter jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''

test-docker: ## Run tests in Docker
	docker-compose exec api pytest tests/ --cov=ai_orchestration

lint-docker: ## Run linting in Docker
	docker-compose exec api make lint

format-docker: ## Run formatting in Docker
	docker-compose exec api make format 