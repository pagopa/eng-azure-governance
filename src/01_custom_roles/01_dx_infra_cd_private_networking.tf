module "dx_infra_cd_private_networking" {
  source  = "pagopa-dx/azure-merge-roles/azurerm"
  version = "~> 0.0"

  scope     = data.azurerm_management_group.pagopa.id
  role_name = "PagoPA DX Infra CD Private Networking"
  reason    = "Merged role for DX Infra CD identities managing private DNS networking"
  source_roles = [
    "Private DNS Zone Contributor",
    "Network Contributor",
  ]
}
