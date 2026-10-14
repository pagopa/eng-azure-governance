# Azure Policy Assignments: UAT

This Terraform module assigns the UAT policy sets to an Azure subscription.

## Purpose

Use this module for the UAT assignments covering API Management, App Service, Cosmos DB, Log Analytics, Redis, virtual machines, and virtual-machine scale sets. The generated Terraform reference below lists the module's inputs and assignments.

## Validation

From this directory, run non-remote Terraform validation:

```bash
terraform fmt -check .
terraform init -backend=false -lockfile=readonly
terraform validate -no-color
```

No diagram is provided because this module is a single subscription-assignment boundary and the generated Terraform reference below enumerates its inputs and resources precisely.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | ~> 4.63.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | 4.63.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_subscription_policy_assignment.api_management](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.app_service](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.cosmosdb](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.redis](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.virtual_machine](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.virtual_machine_scale_set](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_policy_set_ids"></a> [policy\_set\_ids](#input\_policy\_set\_ids) | A map for each policy set id to assign | `map(string)` | n/a | yes |
| <a name="input_subscription"></a> [subscription](#input\_subscription) | The Subsription where this Policy Assignment should be created | <pre>object({<br/>    id              = string<br/>    subscription_id = string<br/>    display_name    = string<br/>  })</pre> | n/a | yes |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | Metadata category name | `string` | `"Custom PagoPA"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
