module "dx_infra_ci_subscription_reader" {
  source = "git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles?ref=implement-merge-roles-terraform-module"

  scope       = data.azurerm_management_group.pagopa.id
  role_name   = "PagoPA DX Infra CI Subscription Reader"
  description = "Merged role for DX Infra CI identities at subscription scope"
  source_roles = [
    "Reader",
    "Reader and Data Access",
    azurerm_role_definition.iac_reader.name,
  ]
}