module "dx_app_ci_resource_group_reader" {
  source  = "pagopa-dx/azure-merge-roles/azurerm"
  version = "~> 0.0"

  scope     = data.azurerm_management_group.pagopa.id
  role_name = "PagoPA DX App CI Resource Group Reader"
  reason    = "Merged role for DX App CI identities at resource group scope"
  source_roles = [
    azurerm_role_definition.iac_reader.name,
    azurerm_role_definition.static_web_app_secrets.name,
  ]
}
