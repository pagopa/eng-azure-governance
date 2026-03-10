---
description: Create or extend an Azure Policy initiative in the governance policy-set stack.
name: internal-create-initiative
agent: agent
argument-hint: domain=<api_management|app_service|container_apps|cosmosdb|dns|event_hub|key_vault|kubernetes|log_analytics|networking|postgresql|redis|virtual_machine|virtual_machine_scale_set> environment=<dev|uat|prod|locals|pci|eu> description=<text>
---

# Internal Policy Initiative Task

## Instructions
1. Use `.github/skills/tech-ai-cloud-policy/SKILL.md`.
2. Create or update `src/03_policy_set/01_${input:domain}_${input:environment}.tf`.
3. Match the current initiative pattern:
   - an environment-specific input variable such as `variable "${input:domain}_${input:environment}"`;
   - `resource "azurerm_policy_set_definition" ...` with `management_group_id = data.azurerm_management_group.pagopa.id`;
   - `metadata = jsonencode(...)`;
   - `policy_definition_reference` blocks pointing either to built-in policy IDs or to `data.terraform_remote_state.policy_<domain>` outputs.
4. If the initiative references a custom policy output that is not exposed yet, first add the missing output in the source module `src/02_policy_<domain>/99_output.tf` and the matching remote-state block in `src/03_policy_set/99_data_source.tf`.
5. Reuse existing `01_<domain>_locals.tf` helpers when the domain already defines reference IDs or parameter scopes there.
6. Add or update the initiative output `<domain>_<environment>_id` using the same pattern already used by sibling initiatives.
7. Keep metadata category, versioning, parameter wiring, and comment style consistent with the closest initiative in the same domain.

## Minimal example
- Input: `domain=api_management environment=dev description="DEV initiative for API Management controls"`
- Expected output:
  - `src/03_policy_set/01_api_management_dev.tf` is created or updated using the same structure already used by the repository's policy-set files.
  - References to custom policies come from the matching remote state outputs.
  - An initiative output is present for downstream reuse.

## Validation
- Run `terraform fmt -check` in `src/03_policy_set`.
- Run `terraform validate` in `src/03_policy_set`.
- Verify every `policy_definition_reference` resolves either to an existing remote-state output or to a valid built-in Azure Policy ID.
