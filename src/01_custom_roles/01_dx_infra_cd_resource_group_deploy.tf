module "dx_infra_cd_resource_group_deploy" {
  source  = "pagopa-dx/azure-merge-roles/azurerm"
  version = "~> 0.0"

  scope     = data.azurerm_management_group.pagopa.id
  role_name = "PagoPA DX Infra CD Resource Group Deploy"
  reason    = "Merged role for DX Infra CD identities at resource group scope"
  source_roles = [
    "Contributor",
    "User Access Administrator",
    "Key Vault Secrets Officer",
    "Key Vault Certificates Officer",
    "Key Vault Crypto Officer",
    "Storage Blob Data Contributor",
    "Storage Queue Data Contributor",
    "Storage Table Data Contributor",
    "Container Apps Contributor",
  ]
}
