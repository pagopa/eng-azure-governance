---
applyTo: "**/*.tf"
---

# Terraform Instructions

## Formatting
- Run `terraform fmt` before commit.
- Use 2-space indentation.
- Use `tfenv` (or repository equivalent) for Terraform version management.

## Naming conventions
- Resources: `snake_case` (for example `aws_iam_role.lambda_execution`).
- Variables: `snake_case` with `description`.
- Locals: `snake_case`, grouped by domain.

## Structure
- Always add `description` to variables.
- Use type constraints for variables.
- Prefer `for_each` over `count` when logical keys matter.
- Prefer data sources over hardcoded IDs.
- Keep backend/state configuration explicit and consistent with repository standards.
- Ensure state locking is enabled when supported by the backend.
- Keep workspace/environment separation explicit.

## Lifecycle and safety
- Use `prevent_destroy` for critical resources when appropriate.
- Use `create_before_destroy` for replacement-sensitive resources.
- Use `ignore_changes` only with documented rationale.

## Multi-cloud baseline
- Pin provider versions in `required_providers`.
- Keep provider configuration explicit for region/subscription/project scope.
- Reuse repository-specific provider conventions for AWS, Azure, and GCP.

## Validation
- Run `terraform validate` after changes.
- Review `terraform plan` before apply.
