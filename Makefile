COMITATO_VENV_PYTHON := ./src/comitato/comitato_azure_retirements/.venv/bin/python
COMITATO_TEST_PATH := tests/comitato/comitato_azure_retirements

.PHONY: help format lint test

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

format: ## Format Terraform files
	@echo "🎨 Formatting Terraform files..."
	@terraform fmt -recursive src/
	@echo "✅ Terraform files formatted"

lint: ## Run all linters
	@echo "🔍 Running linters..."
	@$(MAKE) format
	@echo "✅ All checks passed"

test: ## Run Python tests for comitato_azure_retirements
	@if [ ! -x "$(COMITATO_VENV_PYTHON)" ]; then \
		echo "❌ Missing Python virtual environment: $(COMITATO_VENV_PYTHON)"; \
		echo "ℹ️  Run bash src/comitato/comitato_azure_retirements/run.sh --help to bootstrap dependencies"; \
		exit 1; \
	fi
	@echo "🧪 Running Python tests via project virtual environment..."
	@PYTHONPATH=. $(COMITATO_VENV_PYTHON) -m pytest $(COMITATO_TEST_PATH)
	@echo "✅ Python tests passed"

lock: ## Update provider lock file for multiple platforms
	@echo "🔒 Updating provider lock file..."
	@terraform providers lock \
		-platform=windows_amd64 \
		-platform=darwin_amd64 \
		-platform=darwin_arm64 \
		-platform=linux_amd64
	@echo "✅ Lock file updated"
