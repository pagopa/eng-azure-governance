resource "azurerm_role_definition" "static_web_app_secrets" {
  name        = "PagoPA Static Web Apps List Secrets"
  scope       = data.azurerm_management_group.pagopa.id
  description = "List-only access to Static Web App secrets"

  permissions {
    actions = [
      "Microsoft.Web/staticSites/listSecrets/action",
    ]
  }
}
