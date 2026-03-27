.PHONY: help lint test

help: ## Show available make targets
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

lint: ## Run ruff check --fix, ruff format, and mypy
	uv run ruff check --fix .
	uv run ruff format .
	uv run mypy .

test: ## Run pytest
	uv run pytest
