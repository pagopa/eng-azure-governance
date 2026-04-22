---
description: Create or extend a custom Azure RBAC role in the governance custom roles stack.
name: internal-create-custom-role
agent: agent
argument-hint: file_stub=<slug> role_name=<display name> description=<text> actions=<action1,action2> [not_actions=<action1,action2>]
---

# Internal Custom Role Task

## Instructions
1. Use `.github/skills/internal-cloud-policy/SKILL.md`.
2. Create or update `src/01_custom_roles/01_${input:file_stub}.tf`.
3. Match the repository's existing role shape:
   - `resource "azurerm_role_definition" "<resource_name>"`;
   - `name = "<display name>"`;
   - `scope = data.azurerm_management_group.pagopa.id`;
   - `description = "<text>"`;
   - a `permissions` block with explicit `actions`.
4. Keep the role scoped to the `pagopa` management group, not to a subscription-level data source.
5. Keep permission lists explicit and least-privilege; avoid broad wildcards unless a nearby role already shows a justified precedent.
6. Use the same numbering and one-role-per-file convention already present in `src/01_custom_roles/`.
7. Mirror sibling comment density and formatting instead of introducing a different template style.

## Minimal example
- Input: `file_stub=apim_reader role_name="PagoPA API Management Reader" description="Read-only access to API Management configuration" actions=Microsoft.ApiManagement/service/read,Microsoft.Authorization/*/read`
- Expected output:
  - A new or updated `src/01_custom_roles/01_apim_reader.tf`.
  - The role uses `data.azurerm_management_group.pagopa.id`.
  - The permissions block follows the same layout as neighboring files such as `01_apim_operator_app.tf`.

## Validation
- Run `terraform fmt -check` in `src/01_custom_roles`.
- Run `terraform validate` in `src/01_custom_roles`.
- Verify the action strings are valid Azure RBAC operations and are no broader than required.
