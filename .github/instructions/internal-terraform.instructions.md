---
description: Terraform authoring standards for readability, typed interfaces, and validation-first delivery.
applyTo: "**/*.tf"
---

# Terraform Instructions

## Baseline rules

- Run `terraform fmt` before commit.
- Use 2-space indentation.
- Keep related resources grouped in predictable files such as `providers.tf`, `variables.tf`, `outputs.tf`, and domain-specific resource files when the target directory already follows that split.
- Use `snake_case` for resources, variables, locals, and outputs.
- Add `description` to variables and outputs, plus `type` to variables.
- Prefer data sources or direct references over hardcoded IDs.
- Mark truly sensitive variables and outputs with `sensitive = true`.
- Never commit credentials, tokens, certificates, secrets, or Terraform state to version control.
- Prefer `for_each` over `count` when logical keys matter.
- Keep backend, state locking, and workspace or environment separation explicit.
- Pin provider versions and external module refs intentionally.

- Use `prevent_destroy` for critical resources when appropriate.
- Use `create_before_destroy` for replacement-sensitive resources.
- Use `ignore_changes` only with documented rationale.
- Prefer least-privilege IAM/RBAC and narrow network exposure in the infrastructure being declared.
- Enable encryption at rest and in transit when the platform supports it.

## Use the skill for deeper guidance

- Load `.github/skills/internal-terraform/SKILL.md` for feature-vs-module decisions, migration steps, state and delivery controls, templates, and common mistakes.
- Keep this instruction as the auto-loaded baseline; keep detailed workflow and examples in the skill.

## Validation

- Run `terraform validate` after changes.
- Run `tflint` when available for the target project.
- Review `terraform plan` before apply.
