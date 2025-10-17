.PHONY: install precommit format lint typecheck up down logs topics

PY=python

install:
	$(PY) -m pip install -U pip
	$(PY) -m pip install -r requirements.txt
	pre-commit install

precommit:
	pre-commit run --all-files

format:
	black .
	ruff check . --fix

lint:
	ruff check .
	flake8 .

typecheck:
	mypy .

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

topics:
	$(PY) scripts/create_topics.py
