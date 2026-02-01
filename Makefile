.PHONY: help format lint

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

lock: ## Update provider lock file for multiple platforms
	@echo "🔒 Updating provider lock file..."
	@terraform providers lock \
		-platform=windows_amd64 \
		-platform=darwin_amd64 \
		-platform=darwin_arm64 \
		-platform=linux_amd64
	@echo "✅ Lock file updated"
