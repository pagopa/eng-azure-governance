# policy_assignments

<!-- markdownlint-disable -->
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azuread"></a> [azuread](#requirement\_azuread) | = 2.31.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.38.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_management_group_policy_assignment.assistenza_operations_prod_application_gateway](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.assistenza_operations_prod_audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.assistenza_operations_prod_iso_27001_2013](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.assistenza_operations_prod_resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.assistenza_operations_prod_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_cloud_prod_application_gateway](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_cloud_prod_audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_cloud_prod_iso_27001_2013](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_cloud_prod_resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_cloud_prod_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_pci_dev_audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_pci_dev_pcidssv4](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_pci_prod_application_gateway](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_pci_prod_audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_pci_prod_pcidssv4](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_pci_prod_resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_pci_prod_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_pci_uat_audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_pci_uat_pcidssv4](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_prod_application_gateway](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_prod_audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_prod_iso_27001_2013](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_prod_resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagamenti_servizi_prod_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagopa_data_sovereignty_eu](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.security_itoperations_prod_application_gateway](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.security_itoperations_prod_audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.security_itoperations_prod_iso_27001_2013](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.security_itoperations_prod_resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.security_itoperations_prod_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.strategic_innovation_prod_audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.strategic_innovation_prod_iso_27001_2013](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.strategic_innovation_prod_resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_exemption.assistenza_operations_dev_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.assistenza_operations_prod_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.assistenza_operations_prod_iso_27001_2013_mitigated](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.assistenza_operations_prod_iso_27001_2013_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.assistenza_operations_uat_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagamenti_servizi_cloud_dev_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagamenti_servizi_cloud_prod_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagamenti_servizi_cloud_prod_iso_27001_2013_mitigated](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagamenti_servizi_cloud_prod_iso_27001_2013_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagamenti_servizi_dev_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagamenti_servizi_prod_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagamenti_servizi_prod_iso_27001_2013_mitigated](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagamenti_servizi_prod_iso_27001_2013_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagamenti_servizi_uat_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagopa_azure_security_benchmark_mitigated](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagopa_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.security_itoperations_prod_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.security_itoperations_prod_iso_27001_2013_mitigated](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.security_itoperations_prod_iso_27001_2013_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.strategic_innovation_dev_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.strategic_innovation_prod_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.strategic_innovation_prod_iso_27001_2013_mitigated](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.strategic_innovation_prod_iso_27001_2013_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_role_assignment.assistenza_operations_prod_audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.assistenza_operations_prod_audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.assistenza_operations_prod_audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.assistenza_operations_prod_resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_cloud_prod_audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_cloud_prod_audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_cloud_prod_audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_cloud_prod_resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_dev_audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_dev_audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_dev_audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_prod_audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_prod_audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_prod_audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_prod_resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_uat_audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_uat_audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_pci_uat_audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_prod_audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_prod_audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_prod_audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_prod_resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.security_itoperations_prod_audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.security_itoperations_prod_audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.security_itoperations_prod_audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.security_itoperations_prod_resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.strategic_innovation_prod_audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.strategic_innovation_prod_audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.strategic_innovation_prod_audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.strategic_innovation_prod_resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/role_assignment) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.assistenza_operations_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.assistenza_operations_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.assistenza_operations_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagamenti_servizi_cloud_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagamenti_servizi_cloud_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagamenti_servizi_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagamenti_servizi_pci_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagamenti_servizi_pci_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagamenti_servizi_pci_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagamenti_servizi_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagamenti_servizi_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.security_itoperations_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.strategic_innovation_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.strategic_innovation_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/subscription) | data source |
| [terraform_remote_state.policy_set](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_location"></a> [location](#input\_location) | location | `string` | `"westeurope"` | no |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_policy_type"></a> [policy\_type](#input\_policy\_type) | policy type | `string` | `"Custom"` | no |

## Outputs

No outputs.
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
