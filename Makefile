.PHONY: dev infra api router web ingest eval test fmt

infra:
	docker compose -f infra/docker-compose.yml up -d

api:
	uvicorn apps.api.app.main:app --reload --port 8000

router:
	uvicorn services.router.server:app --reload --port 8100

web:
	cd apps/web && pnpm dev

ingest:
	python -m services.ingestion.pipeline $(FILE)

eval:
	python evals/run_ragas.py --golden evals/golden_set.jsonl

test:
	pytest -q tests/

fmt:
	ruff check --fix .
