# governance

<!-- markdownlint-disable -->
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.31.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | ~> 3.1.0 |
| <a name="requirement_time"></a> [time](#requirement\_time) | ~> 0.7.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_consumption_budget_subscription.governance_budget](https://registry.terraform.io/providers/hashicorp/azurerm/3.31.0/docs/resources/consumption_budget_subscription) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.31.0/docs/data-sources/client_config) | data source |
| [azurerm_monitor_action_group.budget_ag](https://registry.terraform.io/providers/hashicorp/azurerm/3.31.0/docs/data-sources/monitor_action_group) | data source |
| [azurerm_resource_group.monitoring_rg](https://registry.terraform.io/providers/hashicorp/azurerm/3.31.0/docs/data-sources/resource_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.31.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_action_group_budget_name"></a> [action\_group\_budget\_name](#input\_action\_group\_budget\_name) | Action group for Budget name | `string` | n/a | yes |
| <a name="input_action_group_budget_resource_group"></a> [action\_group\_budget\_resource\_group](#input\_action\_group\_budget\_resource\_group) | Action group resource group | `string` | n/a | yes |
| <a name="input_budget_subscription_amount"></a> [budget\_subscription\_amount](#input\_budget\_subscription\_amount) | (Required) The total amount of cost to track with the budget. | `string` | n/a | yes |
| <a name="input_budget_subscription_notifications"></a> [budget\_subscription\_notifications](#input\_budget\_subscription\_notifications) | n/a | <pre>list(<br>    object({<br>      enabled        = bool   # (Optional) Should the notification be enabled?<br>      threshold      = number #(Required) Threshold value associated with a notification. Notification is sent when the cost exceeded the threshold. It is always percent and has to be between 0 and 1000.<br>      operator       = string # (Required) The comparison operator for the notification. Must be one of EqualTo, GreaterThan, or GreaterThanOrEqualTo.<br>      threshold_type = string # (Optional) The type of threshold for the notification. This determines whether the notification is triggered by forecasted costs or actual costs. The allowed values are Actual and Forecasted. Default is Actual.<br>    })<br>  )</pre> | n/a | yes |
| <a name="input_budget_subscription_time_grain"></a> [budget\_subscription\_time\_grain](#input\_budget\_subscription\_time\_grain) | (Required) The time covered by a budget. Tracking of the amount will be reset based on the time grain. Must be one of BillingAnnual, BillingMonth, BillingQuarter, Annually, Monthly and Quarterly. Defaults to Monthly. | `string` | n/a | yes |
| <a name="input_env"></a> [env](#input\_env) | Environment name | `string` | `""` | no |
| <a name="input_env_short"></a> [env\_short](#input\_env\_short) | (Required) | `string` | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | (Required) Region choosed to deploy the resources | `string` | n/a | yes |
| <a name="input_location_short"></a> [location\_short](#input\_location\_short) | Short location form to avoid names to much larger | `string` | `"weu"` | no |
| <a name="input_monitoring_resource_group"></a> [monitoring\_resource\_group](#input\_monitoring\_resource\_group) | Resource group where the monitoring is saved | `string` | n/a | yes |
| <a name="input_prefix"></a> [prefix](#input\_prefix) | Project prefix | `string` | n/a | yes |
| <a name="input_subscription_foundation"></a> [subscription\_foundation](#input\_subscription\_foundation) | Allows you to enable the creation of vault, AD permissions and other configurations for the subscription if not present | `bool` | `false` | no |

## Outputs

No outputs.
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
