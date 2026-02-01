---
applyTo: "**/*.tf"
---

# Terraform Files Instructions

## General Rules

- Run `terraform fmt` before committing
- Use `tfenv` for version management
- Use `./terraform.sh plan|apply|destroy` wrapper

## File Organization

- `99_main.tf`: Provider configuration
- `99_terraform.tf`: Backend and required providers
- `99_variables.tf`: Input variables
- `99_data_source.tf`: Data sources
- `01_*.tf`: Resource definitions

## Backend Configuration

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.<module>.terraform.tfstate"
  }
}
```

## Policy Definition Structure

```hcl
resource "azurerm_policy_definition" "example" {
  name         = "pagopa-domain-rule-name"
  policy_type  = "Custom"
  mode         = "All"
  display_name = "PagoPA - Rule Description"
  description  = "Detailed description of what this policy does"

  metadata = jsonencode({
    category = "Domain"
    version  = "1.0.0"
  })

  policy_rule = jsonencode({
    if = {
      # conditions
    }
    then = {
      effect = "Deny"  # or "Audit", "AuditIfNotExists", etc.
    }
  })

  parameters = jsonencode({
    # parameter definitions
  })
}
```

## Policy Initiative Structure

```hcl
resource "azurerm_policy_set_definition" "example" {
  name         = "pagopa-domain-initiative"
  policy_type  = "Custom"
  display_name = "PagoPA Domain Initiative"
  description  = "Groups related policies for domain"

  policy_definition_reference {
    policy_definition_id = azurerm_policy_definition.rule1.id
    parameter_values     = jsonencode({})
  }
}
```

## Lock File Management

Support multiple platforms:

```bash
terraform providers lock \
  -platform=windows_amd64 \
  -platform=darwin_amd64 \
  -platform=darwin_arm64 \
  -platform=linux_amd64
```
