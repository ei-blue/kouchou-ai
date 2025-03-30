run:
	@echo "Loading ../.env.server and starting Uvicorn..."
	set -a && source ../.env.server && set +a && rye run uvicorn src.main:app --reload --port 8000

lint/check:
	rye run ruff check .

lint/format:
	rye run ruff check --fix .
