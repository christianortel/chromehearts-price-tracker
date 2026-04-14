SHELL := /bin/sh

.PHONY: install api web dev lint typecheck test seed migrate up down

install:
	cd apps/web && npm install

api:
	cd apps/api && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd apps/web && npm run dev

dev:
	docker compose up --build

lint:
	cd apps/api && python -m ruff check .
	cd apps/web && npm run lint

typecheck:
	cd apps/api && python -m mypy app
	cd apps/web && npm run typecheck

test:
	cd apps/api && python -m pytest
	cd apps/web && npm run test:e2e

seed:
	cd apps/api && python -m app.db.seed

migrate:
	cd apps/api && alembic upgrade head

up:
	docker compose up --build -d

down:
	docker compose down -v

