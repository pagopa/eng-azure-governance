---
description: Create or extend an Azure Policy definition in one of the governance domain modules.
name: internal-create-policy
agent: agent
argument-hint: domain=<module_suffix> policy_stub=<slug> display_name=<text> mode=<All|Indexed> effect=<Deny|Audit|AuditIfNotExists>
---

# Internal Policy Definition Task

## Instructions
1. Use `.github/skills/tech-ai-cloud-policy/SKILL.md`.
2. Work inside `src/02_policy_${input:domain}/`.
3. Create or update a Terraform file such as `01_${input:policy_stub}.tf`, following the existing one-policy-per-file pattern already used in the target domain.
4. Keep the definition aligned with the repository's current structure:
   - `management_group_id = data.azurerm_management_group.pagopa.id`;
   - `metadata = jsonencode(...)`;
   - `parameters = file("./policy_rules/${input:policy_stub}_parameters.json")` when the domain module uses file-backed parameters;
   - `policy_rule = file("./policy_rules/${input:policy_stub}_policy.json")` for the rule body when that is the established module pattern.
5. Add any required JSON assets under `src/02_policy_${input:domain}/policy_rules/` using the same naming scheme as neighboring definitions.
6. Export the new policy ID from `src/02_policy_${input:domain}/99_output.tf` when initiatives or remote-state consumers will need it.
7. Keep display names, resource names, and metadata style consistent with the other policies in the same domain folder.

## Minimal example
- Input: `domain=api_management policy_stub=require_private_endpoint display_name="PagoPA API Management requires private endpoint" mode=Indexed effect=Deny`
- Expected output:
  - A Terraform definition under `src/02_policy_api_management/`.
  - Matching files under `src/02_policy_api_management/policy_rules/`.
  - An output added to `99_output.tf` if the policy will be consumed by `src/03_policy_set/`.

## Validation
- Validate JSON syntax for any new files in `policy_rules/`.
- Run `terraform fmt -check` in `src/02_policy_${input:domain}`.
- Run `terraform validate` in `src/02_policy_${input:domain}`.
- Verify the new resource name and output naming fit the conventions already used by sibling policies.
