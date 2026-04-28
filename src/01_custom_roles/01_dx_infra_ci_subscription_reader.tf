module "dx_infra_ci_subscription_reader" {
  source  = "pagopa-dx/azure-merge-roles/azurerm"
  version = "~> 0.0"

  scope     = data.azurerm_management_group.pagopa.id
  role_name = "PagoPA DX Infra CI Subscription Reader"
  reason    = "Merged role for DX Infra CI identities at subscription scope"
  source_roles = [
    "Reader",
    "Reader and Data Access",
    azurerm_role_definition.iac_reader.name,
  ]
}
