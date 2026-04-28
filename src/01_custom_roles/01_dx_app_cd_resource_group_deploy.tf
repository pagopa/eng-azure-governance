module "dx_app_cd_resource_group_deploy" {
  source  = "pagopa-dx/azure-merge-roles/azurerm"
  version = "~> 0.0"

  scope     = data.azurerm_management_group.pagopa.id
  role_name = "PagoPA DX App CD Resource Group Deploy"
  reason    = "Merged role for DX App CD identities at resource group scope"
  source_roles = [
    "Website Contributor",
    "CDN Profile Contributor",
    "Container Apps Contributor",
    "Storage Blob Data Contributor",
    azurerm_role_definition.static_web_app_secrets.name,
  ]
}
