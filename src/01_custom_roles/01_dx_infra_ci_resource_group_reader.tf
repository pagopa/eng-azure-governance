module "dx_infra_ci_resource_group_reader" {
  source  = "pagopa-dx/azure-merge-roles/azurerm"
  version = "~> 0.0"

  scope     = data.azurerm_management_group.pagopa.id
  role_name = "PagoPA DX Infra CI Resource Group Reader"
  reason    = "Merged role for DX Infra CI identities at resource group scope"
  source_roles = [
    "DocumentDB Account Contributor",
    "Key Vault Secrets User",
    "Key Vault Certificate User",
    "Key Vault Crypto Officer",
    "Storage Blob Data Reader",
    "Storage Queue Data Reader",
    "Storage Table Data Reader",
    "Container Apps Operator",
    "Container Apps Jobs Operator",
  ]
}
