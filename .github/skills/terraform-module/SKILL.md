---
name: terraform-module
description: Guide for creating or modifying Terraform modules in this repository. Use when asked to change resources, variables, outputs, data sources, or modules.
---

# Terraform Module

## Context

I need to modify or extend Terraform configuration for Azure governance (policies, initiatives, custom roles).

## Codebase Discovery

Analyze existing files with `#codebase` and:
- `#file:src/01_custom_roles/`
- `#file:src/02_policy_*/`
- `#file:src/03_policy_set/`
- `#file:src/04_policy_assignments/`

## Input Required

- **Modification type**: ${input:type:resource,variable,output,data_source,module}
- **Description**: ${input:description}

## Conventions

- Use `snake_case` for resources and variables
- Always add `description` to variables
- Use `try()` for optional values
- Follow the folder naming convention: `02_policy_{service}/`

## Provider

```hcl
terraform {
  required_version = ">= 1.7.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "yourterraformstate"
    container_name       = "tfstate"
    key                  = "azure-governance.tfstate"
  }
}

provider "azurerm" {
  features {}
}
```

## Validations

- Always add `description` to variables
- Use `try()` for optional values in JSON
- Check with `#problems` for any errors after modifications
- Run `terraform fmt` before committing

## References

Follow conventions in `#file:.github/copilot-instructions.md`
