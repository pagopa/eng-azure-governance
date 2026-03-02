---
description: Create or modify Terraform resources and features
name: cs-terraform
agent: agent
argument-hint: action=<create|modify> type=<resource|module|variable|output|data_source> description=<text> target_dir=<path>
---

# Terraform Task

## Context
Create or modify Terraform resources, modules, variables, outputs, or data sources while preserving module consistency.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Task type**: ${input:type:resource,module,variable,output,data_source}
- **Description**: ${input:description}
- **Target directory**: ${input:target_dir}

## Instructions

1. Use `.github/skills/terraform-feature/SKILL.md` for resource-level changes.
2. If `type=module`, also use `.github/skills/terraform-module/SKILL.md`.
3. Search existing `.tf` files in the target directory.
4. Follow existing naming conventions and patterns.
5. Apply the task with:
   - correct naming (`snake_case`)
   - `description` for variables/outputs
   - no hardcoded values
   - tags where supported
6. Keep technical output and documentation in English.

## Minimal example
- Input: `action=create type=module description="Reusable role module" target_dir=src/modules/iam-role`
- Expected output:
  - Standard module file layout with typed variables and described outputs.
  - No hardcoded IDs/secrets and consistent naming.
  - Validation-ready module (`fmt`, `validate`, plan review).

## Validation
- Run `terraform fmt`.
- Run `terraform validate`.
- Check errors in `terraform plan`.
