resource "azurerm_role_definition" "authorization_reader" {
  name        = "PagoPA Authorization Reader"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Read roles and role assignments and resource groups"

  permissions {
    actions = [
      "Microsoft.Authorization/*/read",
      "Microsoft.Resources/subscriptions/resourcegroups/read",
      "Microsoft.KeyVault/vaults/read",
    ]
  }
}
