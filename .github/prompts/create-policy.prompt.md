---
agent: agent
description: Create a new Azure Policy definition
---

# Create Azure Policy Definition

## Context

This prompt helps you create a new Azure Policy definition for a specific domain.

## Input Required

- **Domain**: ${input:domain:api_management,app_service,cosmosdb,kubernetes,networking,postgresql,redis,storage,virtual_machine}
- **Policy Name**: ${input:policyName}
- **Description**: ${input:description}
- **Effect**: ${input:effect:Deny,Audit,AuditIfNotExists}

## Instructions

1. Navigate to `src/02_policy_${input:domain}/`
2. Create a new `.tf` file or add to existing
3. Add the policy definition:

```hcl
resource "azurerm_policy_definition" "${input:policyName}" {
  name         = "pagopa-${input:domain}-${input:policyName}"
  policy_type  = "Custom"
  mode         = "All"
  display_name = "PagoPA - ${input:description}"
  description  = "${input:description}"

  metadata = jsonencode({
    category = "${input:domain}"
    version  = "1.0.0"
  })

  policy_rule = jsonencode({
    if = {
      # Define conditions
    }
    then = {
      effect = "${input:effect}"
    }
  })
}
```

## Validations

- [ ] Policy name follows `pagopa-*` convention
- [ ] Description is clear
- [ ] Effect is appropriate for the rule
- [ ] Conditions are correct
- [ ] Terraform validates successfully

## References

Follow the conventions in `#file:.github/copilot-instructions.md`
