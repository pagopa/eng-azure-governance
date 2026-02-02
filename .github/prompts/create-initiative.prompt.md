---
agent: agent
description: Create a new Policy Initiative (Set)
---

# Create Policy Initiative

## Context

This prompt helps you create a new Policy Initiative that groups related policies.

## Input Required

- **Domain**: ${input:domain:api_management,app_service,cosmosdb,kubernetes,networking,postgresql,redis,storage,virtual_machine}
- **Environment**: ${input:environment:dev,uat,prod}
- **Description**: ${input:description}

## Instructions

1. Navigate to `src/03_policy_set/`
2. Create file `01_${input:domain}_${input:environment}.tf`
3. Add the initiative definition:

```hcl
resource "azurerm_policy_set_definition" "${input:domain}_${input:environment}" {
  name         = "pagopa-${input:domain}-${input:environment}"
  policy_type  = "Custom"
  display_name = "PagoPA ${input:domain} Initiative (${input:environment})"
  description  = "${input:description}"

  metadata = jsonencode({
    category = "${input:domain}"
    version  = "1.0.0"
  })

  # Reference policies from 02_policy_* folders
  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.policy1.id
    reference_id         = "policy1"
  }

  # Add more policy references as needed
}
```

## Validations

- [ ] Initiative name follows convention
- [ ] All referenced policies exist
- [ ] Environment-specific parameters set
- [ ] Terraform validates successfully

## References

Follow the conventions in `#file:.github/copilot-instructions.md`
