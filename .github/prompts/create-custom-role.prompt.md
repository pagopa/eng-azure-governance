---
agent: agent
description: Create a custom RBAC role
---

# Create Custom RBAC Role

## Context

This prompt helps you create a custom RBAC role with least privilege permissions.

## Input Required

- **Role Name**: ${input:roleName}
- **Description**: ${input:description}

## Instructions

1. Navigate to `src/01_custom_roles/`
2. Create or edit `.tf` file
3. Add the role definition:

```hcl
resource "azurerm_role_definition" "${input:roleName}" {
  name        = "${input:roleName}"
  scope       = data.azurerm_subscription.current.id
  description = "${input:description}"

  permissions {
    actions = [
      # List specific allowed actions
      "Microsoft.Resources/subscriptions/resourceGroups/read",
    ]
    not_actions = []
    data_actions = []
    not_data_actions = []
  }

  assignable_scopes = [
    data.azurerm_subscription.current.id,
  ]
}
```

## Permissions Guidelines

- Use specific actions, avoid wildcards (`*`)
- Only include necessary permissions
- Document why each permission is needed
- Consider data plane vs control plane actions

## Validations

- [ ] Role name is descriptive
- [ ] Permissions follow least privilege
- [ ] No unnecessary wildcards
- [ ] Terraform validates successfully

## References

Follow the conventions in `#file:.github/copilot-instructions.md`
