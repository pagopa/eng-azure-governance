module "dx_infra_cd_subscription_admin" {
  source = "git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles?ref=implement-merge-roles-terraform-module"

  scope       = data.azurerm_management_group.pagopa.id
  role_name   = "PagoPA DX Infra CD Subscription Admin"
  description = "Merged role for DX Infra CD identities at subscription scope"
  source_roles = [
    "Reader",
    "Role Based Access Control Administrator",
  ]
}