---
name: internal-terraform
description: Use when adding, refactoring, or reviewing Terraform or OpenTofu configuration, including root-level resources, reusable modules, drift-safe changes, and HCL interface design.
---

# Terraform Skill

## When to use

- Add or modify resources, variables, outputs, data sources in existing configurations.
- Create a new reusable Terraform module from scratch.
- Refactor inline resources into a module.
- Decide whether a change belongs in an existing configuration or warrants a new module.

## Feature vs module — when to use which

See `references/decision-guide.md` for the full decision flowchart. Quick rule:

| Situation | Use |
|---|---|
| Adding resources to an existing root/environment config | Feature (inline) |
| Logic reused across 2+ root configs or repositories | Module |
| Complex resource group with its own lifecycle | Module |
| One-off resource for a single environment | Feature (inline) |

## Mandatory rules

- Follow `.github/instructions/internal-terraform.instructions.md` for provider and external module pinning.
- Use `snake_case` for all Terraform identifiers.
- Add `description` and `type` to every variable.
- Avoid `default` values in variables for non-module components; pass configurations via `.tfvars`.
- Avoid using `locals` for hardcoded configuration; use direct values in the code unless they need to be configurable.
- *Note:* The above two rules on avoiding defaults and restricting locals do not apply to reusable standalone modules.
- Add `description` to every output.
- Avoid hardcoded values (IDs, ARNs, subscription IDs, secrets).
- Apply tags on all taggable resources.
- Preserve naming and folder conventions of the target repository.
- Preserve stable module input/output contracts when modifying existing modules.
- Keep Terraform formatting and file splits consistent with the target directory; when the repo already separates `providers.tf`, `terraform.tf`, `variables.tf`, or `outputs.tf`, preserve that structure.

## State and delivery controls

- Prefer remote state with locking and encryption for shared environments; do not normalize team workflows around local shared state files.
- Treat `terraform import`, `terraform state mv`, and `terraform state rm` as explicit migration steps that must be documented alongside address or module refactors.
- Review drift before structural changes, especially when renaming resources, changing `for_each` keys, or splitting code into modules.
- Pin external modules and provider versions intentionally; when changing constraints, state the upgrade or compatibility reason.
- Run policy or compliance gates when the repository or delivery pipeline already depends on them.
- Stay Terraform/OpenTofu compatible unless the target repository explicitly standardizes on OpenTofu-only features.

## Style Conventions

- Use two spaces for indentation and no tabs.
- Place meta-arguments before normal arguments, keep arguments before nested blocks, and keep lifecycle-style control blocks last.
- Use descriptive singular `snake_case` identifiers; use `main` only when there is one obvious instance and a more specific name adds no clarity.
- When `variables.tf` or `outputs.tf` exist as dedicated files, keep entries deterministic and easy to scan, typically alphabetical by identifier.

## Module standard layout

- `main.tf` — resources and data sources
- `variables.tf` — input variables with `description` and `type`
- `outputs.tf` — outputs with `description`
- `versions.tf` — `required_version` and `required_providers` with pinned versions
- `README.md` — usage example, inputs, outputs

## Templates

Load `references/template-examples.md` when you need a minimal inline feature example or a starter reusable module.

## Imported complements

- Load `.github/skills/terraform-terraform-search-import/SKILL.md` when existing unmanaged resources must be discovered or bulk-imported into Terraform state.
- Load `.github/skills/terraform-terraform-test/SKILL.md` when authoring `.tftest.hcl` coverage, choosing plan-vs-apply test modes, or troubleshooting Terraform test execution.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using `count` where `for_each` with logical keys fits | Index-based addressing causes drift when items are added/removed in the middle | Use `for_each` with a map or `toset()` of logical keys |
| Missing `description` on variables and outputs | Undocumented interfaces block collaboration and code review | Always add `description` — it costs nothing |
| Hardcoded ARNs, subscription IDs, or account IDs | Breaks portability between environments and accounts | Use variables or data sources |
| Provider version not pinned in `required_providers` | Non-deterministic plans across machines and CI | Pin with `~>` or exact version constraint |
| `ignore_changes` without documented rationale | Hides drift and confuses future maintainers | Add a comment explaining why the lifecycle rule exists |
| Creating a module for a one-off resource group | Over-engineering adds indirection without reuse benefit | Keep it inline; extract when 2+ callers emerge |
| Breaking module interface (removing/renaming variables) | Breaks all consumers silently | Deprecate old vars, add new ones, migrate consumers, then remove |
| Missing `versions.tf` in modules | No reproducibility guarantee | Always include `required_version` and `required_providers` |
| Missing `prevent_destroy` on critical production resources | Accidental deletion during `terraform apply` | Add lifecycle for databases, DNS zones, encryption keys |
| `default = ""` instead of `default = null` for optional strings | Empty string passes validation but means "no value" ambiguously | Use `null` for truly optional inputs |

## Validation

- `terraform fmt -check -recursive`
- `terraform validate`
- Review `terraform plan` output for unexpected changes
- For modules: run example/consumer plan review
