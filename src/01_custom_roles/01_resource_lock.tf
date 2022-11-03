resource "azurerm_role_definition" "resource_lock_contributor" {
  name        = "PagoPA Resource Lock Contributor"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Add lock to resources"

  permissions {
    actions = [
      "Microsoft.Resources/deployments/write",
      "Microsoft.Authorization/locks/write",
    ]
  }
}
