resource "azurerm_role_definition" "security_contributor" {
  name        = "PagoPA Security Contributor"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Location and SuppressionRules alerts"

  permissions {
    actions = [
      "Microsoft.Security/locations/alerts/*",
      "Microsoft.Security/alertsSuppressionRules/*"
    ]
  }
}