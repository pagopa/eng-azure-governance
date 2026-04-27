module "dx_infra_cd_resource_group_deploy" {
  source = "git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles?ref=implement-merge-roles-terraform-module"

  scope       = data.azurerm_management_group.pagopa.id
  role_name   = "PagoPA DX Infra CD Resource Group Deploy"
  description = "Merged role for DX Infra CD identities at resource group scope"
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