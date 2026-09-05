# Azure Policy: Audit Logs

This Terraform root defines custom Azure Policy definitions that add diagnostic settings for audit logs.

## Purpose

Use this directory for the audit-log policy family. The root covers the Azure resource types listed in the generated reference and directs diagnostic settings to Log Analytics workspaces or Storage Accounts through the checked-in policy rules. Start with the relevant `01_*.tf` resource file and its matching `policy_rules/*.json` files; use the local `terraform.sh` wrapper for the supported Terraform lifecycle actions.

## Validation

From this directory, run non-remote Terraform validation:

```bash
terraform fmt -check .
terraform init -backend=false -lockfile=readonly
terraform validate -no-color
```

No diagram is provided because this directory is a single Terraform policy root and the generated reference below enumerates its definitions, inputs, and outputs more precisely than a separate relationship diagram.

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 4.35.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | 4.35.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_policy_definition.audit_logs_api_management_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_api_management_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_app_service_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_app_service_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_application_gateway_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_application_gateway_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_container_app_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_container_app_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_container_registry_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_container_registry_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_cosmos_db_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_cosmos_db_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_event_hub_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_event_hub_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_grafana_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_grafana_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_keyvault_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_keyvault_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_kubernetes_cluster_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_kubernetes_cluster_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_log_analytics_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_log_analytics_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_postgresql_flexible_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_postgresql_flexible_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_postgresql_single_server_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_postgresql_single_server_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_public_ip_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_public_ip_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_subscription_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_subscription_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_virtual_network_gateway_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_virtual_network_gateway_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/data-sources/management_group) | data source |
| [azurerm_role_definition.audit_logs_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/data-sources/role_definition) | data source |
| [azurerm_role_definition.log_analytics_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/data-sources/role_definition) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_audit_logs_api_management_log_analytics_id"></a> [audit\_logs\_api\_management\_log\_analytics\_id](#output\_audit\_logs\_api\_management\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_api_management_storage_account_id"></a> [audit\_logs\_api\_management\_storage\_account\_id](#output\_audit\_logs\_api\_management\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_app_service_log_analytics_id"></a> [audit\_logs\_app\_service\_log\_analytics\_id](#output\_audit\_logs\_app\_service\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_app_service_storage_account_id"></a> [audit\_logs\_app\_service\_storage\_account\_id](#output\_audit\_logs\_app\_service\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_application_gateway_log_analytics_id"></a> [audit\_logs\_application\_gateway\_log\_analytics\_id](#output\_audit\_logs\_application\_gateway\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_application_gateway_storage_account_id"></a> [audit\_logs\_application\_gateway\_storage\_account\_id](#output\_audit\_logs\_application\_gateway\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_container_app_log_analytics_id"></a> [audit\_logs\_container\_app\_log\_analytics\_id](#output\_audit\_logs\_container\_app\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_container_app_storage_account_id"></a> [audit\_logs\_container\_app\_storage\_account\_id](#output\_audit\_logs\_container\_app\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_container_registry_log_analytics_id"></a> [audit\_logs\_container\_registry\_log\_analytics\_id](#output\_audit\_logs\_container\_registry\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_container_registry_storage_account_id"></a> [audit\_logs\_container\_registry\_storage\_account\_id](#output\_audit\_logs\_container\_registry\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_cosmos_db_log_analytics_id"></a> [audit\_logs\_cosmos\_db\_log\_analytics\_id](#output\_audit\_logs\_cosmos\_db\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_cosmos_db_storage_account_id"></a> [audit\_logs\_cosmos\_db\_storage\_account\_id](#output\_audit\_logs\_cosmos\_db\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_event_hub_log_analytics_id"></a> [audit\_logs\_event\_hub\_log\_analytics\_id](#output\_audit\_logs\_event\_hub\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_event_hub_storage_account_id"></a> [audit\_logs\_event\_hub\_storage\_account\_id](#output\_audit\_logs\_event\_hub\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_grafana_log_analytics_id"></a> [audit\_logs\_grafana\_log\_analytics\_id](#output\_audit\_logs\_grafana\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_grafana_storage_account_id"></a> [audit\_logs\_grafana\_storage\_account\_id](#output\_audit\_logs\_grafana\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_keyvault_log_analytics_id"></a> [audit\_logs\_keyvault\_log\_analytics\_id](#output\_audit\_logs\_keyvault\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_keyvault_storage_account_id"></a> [audit\_logs\_keyvault\_storage\_account\_id](#output\_audit\_logs\_keyvault\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_kubernetes_cluster_log_analytics_id"></a> [audit\_logs\_kubernetes\_cluster\_log\_analytics\_id](#output\_audit\_logs\_kubernetes\_cluster\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_kubernetes_cluster_storage_account_id"></a> [audit\_logs\_kubernetes\_cluster\_storage\_account\_id](#output\_audit\_logs\_kubernetes\_cluster\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_log_analytics_log_analytics_id"></a> [audit\_logs\_log\_analytics\_log\_analytics\_id](#output\_audit\_logs\_log\_analytics\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_log_analytics_storage_account_id"></a> [audit\_logs\_log\_analytics\_storage\_account\_id](#output\_audit\_logs\_log\_analytics\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_postgresql_flexible_log_analytics_id"></a> [audit\_logs\_postgresql\_flexible\_log\_analytics\_id](#output\_audit\_logs\_postgresql\_flexible\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_postgresql_flexible_storage_account_id"></a> [audit\_logs\_postgresql\_flexible\_storage\_account\_id](#output\_audit\_logs\_postgresql\_flexible\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_postgresql_single_server_log_analytics_id"></a> [audit\_logs\_postgresql\_single\_server\_log\_analytics\_id](#output\_audit\_logs\_postgresql\_single\_server\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_postgresql_single_server_storage_account_id"></a> [audit\_logs\_postgresql\_single\_server\_storage\_account\_id](#output\_audit\_logs\_postgresql\_single\_server\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_public_ip_log_analytics_id"></a> [audit\_logs\_public\_ip\_log\_analytics\_id](#output\_audit\_logs\_public\_ip\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_public_ip_storage_account_id"></a> [audit\_logs\_public\_ip\_storage\_account\_id](#output\_audit\_logs\_public\_ip\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_subscription_log_analytics_id"></a> [audit\_logs\_subscription\_log\_analytics\_id](#output\_audit\_logs\_subscription\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_subscription_storage_account_id"></a> [audit\_logs\_subscription\_storage\_account\_id](#output\_audit\_logs\_subscription\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_virtual_network_gateway_log_analytics_id"></a> [audit\_logs\_virtual\_network\_gateway\_log\_analytics\_id](#output\_audit\_logs\_virtual\_network\_gateway\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_virtual_network_gateway_storage_account_id"></a> [audit\_logs\_virtual\_network\_gateway\_storage\_account\_id](#output\_audit\_logs\_virtual\_network\_gateway\_storage\_account\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
