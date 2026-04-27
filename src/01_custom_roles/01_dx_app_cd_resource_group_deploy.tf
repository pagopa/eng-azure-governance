module "dx_app_cd_resource_group_deploy" {
  source = "git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles?ref=implement-merge-roles-terraform-module"

  scope       = data.azurerm_management_group.pagopa.id
  role_name   = "PagoPA DX App CD Resource Group Deploy"
  description = "Merged role for DX App CD identities at resource group scope"
  source_roles = [
    "Website Contributor",
    "CDN Profile Contributor",
    "Container Apps Contributor",
    "Storage Blob Data Contributor",
    azurerm_role_definition.static_web_app_secrets.name,
  ]
}