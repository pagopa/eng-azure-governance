resource "azurerm_role_definition" "ddos_joiner" {
  name        = "PagoPA DDoS Joiner"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Join virtual network to DDoS plan"

  permissions {
    actions = [
      "Microsoft.Network/ddosProtectionPlans/join/action",
    ]
  }
}
