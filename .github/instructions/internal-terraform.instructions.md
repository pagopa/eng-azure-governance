---
description: Terraform authoring standards for readability, typed interfaces, and validation-first delivery.
applyTo: "**/*.tf"
---

# Terraform Instructions

## Baseline rules

- Run `terraform fmt` before commit.
- Use 2-space indentation.
- Keep related resources grouped in predictable files such as `providers.tf`, `variables.tf`, `outputs.tf`, and domain-specific resource files when the target directory already follows that split.
- For new Terraform root directories without an established competing layout, use a numbered domain split that expresses logical hierarchy: keep `00-*` for init or fundamental data, allocate `10-97` dynamically from upstream prerequisites to downstream branches, reserve `98-locals.tf`, `99-providers.tf`, `99-variables.tf`, and `99-outputs.tf`, and keep the detailed structure aligned with `.github/skills/internal-terraform/references/structure-standard.md`.
- Treat numbered root files as a human-facing hierarchy, not as Terraform's execution engine; real dependency order must still come from references, data sources, or explicit `depends_on`.
- When the target directory already uses another stable structure, adapt the default instead of forcing a migration or changing business logic.
- For root directories using the repository default runner pattern, keep environment files under `env/<account|subscription|project>/`, with `backend.ini` for `terraform.sh` backend configuration and `terraform.tfvars` for environment-specific input values.
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

## Provider lock and isolation

- Terraform roots validated with `terraform init -lockfile=readonly` in CI must commit a `.terraform.lock.hcl` and pre-populate provider checksums for every platform that will run validation, plan, or apply.
- Refresh checksums with `terraform providers lock` covering at minimum `windows_amd64`, `darwin_amd64`, `darwin_arm64`, `linux_amd64`, and `linux_arm64`, for example: `terraform providers lock -platform=windows_amd64 -platform=darwin_amd64 -platform=darwin_arm64 -platform=linux_amd64 -platform=linux_arm64`.
- Root configurations validated in isolation must declare their own `terraform { required_version, required_providers }` block so `terraform validate` and TFLint stay deterministic regardless of caller directory.
- Child modules that read adjacent templates or query files must resolve them from `path.module` so validation stays stable across CI runners and local shells.

## Use the skill for deeper guidance

- Load `.github/skills/internal-terraform/SKILL.md` for feature-vs-module decisions, migration steps, state and delivery controls, templates, and common mistakes.
- Keep this instruction as the auto-loaded baseline; keep detailed workflow and examples in the skill.

## Validation

- Run `terraform validate` after changes.
- Run `tflint` when available for the target project.
- Review `terraform plan` before apply.
