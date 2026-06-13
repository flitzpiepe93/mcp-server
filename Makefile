.DEFAULT_GOAL := help

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up:  ## Start Keycloak + MCP server in the background (with build)
	docker compose up -d --build

refresh:  ## Tear down (incl. volumes) and start fresh (with build)
	docker compose down -v
	docker compose up -d --build

client:  ## Run the example agent client once against the server
	docker compose run --rm client
