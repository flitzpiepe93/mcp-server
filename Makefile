.DEFAULT_GOAL := help

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up:  ## Start Keycloak + MCP server (with build); logs stream to the console
	docker compose up --build

refresh:  ## Tear down (incl. volumes) and start fresh (with build)
	docker compose down -v
	docker compose up --build

down:  ## Stop containers and remove volumes (Keycloak realm state is discarded)
	docker compose down -v

run-client:  ## Run the example agent client once against the server
	docker compose run --rm client

docs-serve:  ## Serve the documentation locally with live reload
	uv run --group docs mkdocs serve
