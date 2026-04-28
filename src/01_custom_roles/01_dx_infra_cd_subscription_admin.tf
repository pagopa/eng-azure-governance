module "dx_infra_cd_subscription_admin" {
  source  = "pagopa-dx/azure-merge-roles/azurerm"
  version = "~> 0.0"

  scope     = data.azurerm_management_group.pagopa.id
  role_name = "PagoPA DX Infra CD Subscription Admin"
  reason    = "Merged role for DX Infra CD identities at subscription scope"
  source_roles = [
    "Reader",
    "Role Based Access Control Administrator",
  ]
}
