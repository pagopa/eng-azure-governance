module "dx_app_ci_resource_group_reader" {
  source = "git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles?ref=implement-merge-roles-terraform-module"

  scope       = data.azurerm_management_group.pagopa.id
  role_name   = "PagoPA DX App CI Resource Group Reader"
  description = "Merged role for DX App CI identities at resource group scope"
  source_roles = [
    azurerm_role_definition.iac_reader.name,
    azurerm_role_definition.static_web_app_secrets.name,
  ]
}