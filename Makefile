.PHONY: help install run test lint format format-check ci clean dev

install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev: run

test:
	poetry run pytest -v

lint:
	poetry run flake8 app/ tests/
	poetry run mypy app/

format:
	poetry run black app/ tests/

format-check:
	poetry run black --check app/ tests/

ci: test lint format-check
