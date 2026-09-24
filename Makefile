.PHONY: lint check

lint:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .
	cd frontend && npm run lint

check: lint
	.venv/bin/pytest -q
	cd frontend && npm run build
