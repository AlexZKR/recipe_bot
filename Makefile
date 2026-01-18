run_local: start
	. venv/bin/activate
	PYTHONPATH=$(PWD) \
	&& python -m recipebot.drivers.main

requirements:
	python -m pip install --upgrade pip setuptools wheel && python -m pip install -r requirements.txt


# Load overrides from .env if available
-include .env

# Database connection defaults that can be overridden when calling make
DB_HOST ?= localhost
DB_PORT ?= 5432
DB_USER ?= postgres
DB_PASSWORD ?= pass
DB_NAME ?= postgres

# Linting
lint: mypy ruff bandit

mypy:
	mypy .

ruff:
	ruff check --config pyproject.toml --fix

bandit:
	bandit -c pyproject.toml -r . --quiet

# Formatting
format:
	ruff format --config pyproject.toml .

start:
	docker compose up --build -d

stop:
	docker compose down

# Testing
check: lint tests

tests:
	PYTHONPATH=$(PWD) \
	&& . venv/bin/activate \
	&& pytest --cov --cov-fail-under=90 --cov-report html

apply-migration-recipe-category:
ifeq ($(strip $(MIGRATION_SQL)),)
	$(error MIGRATION_SQL is required for apply-migration-recipe-category)
endif
	PGPASSWORD=$(DB_PASSWORD) \
	psql "host=$(DB_HOST) port=$(DB_PORT) user=$(DB_USER) dbname=$(DB_NAME)" \
		-v ON_ERROR_STOP=1 \
		-f $(MIGRATION_SQL)

coverage:
	PYTHONPATH=$(PWD) \
	&& . venv/bin/activate \
	&& python -m webbrowser -t htmlcov/index.html

# Jupyter notebook
notebook:
	. venv/bin/activate \
	&& jupyter notebook --notebook-dir=notebooks
