module "dx_infra_cd_private_networking" {
  source = "git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles?ref=implement-merge-roles-terraform-module"

  scope       = data.azurerm_management_group.pagopa.id
  role_name   = "PagoPA DX Infra CD Private Networking"
  description = "Merged role for DX Infra CD identities managing private DNS networking"
  source_roles = [
    "Private DNS Zone Contributor",
    "Network Contributor",
  ]
}