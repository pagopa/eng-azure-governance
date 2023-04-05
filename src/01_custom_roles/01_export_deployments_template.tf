resource "azurerm_role_definition" "export_deployments_template" {
  name        = "PagoPA Export Deployments Template"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Export Deployments Template. Deprecated use PagoPA IaC Reader"

  permissions {
    actions = [
      "Microsoft.Resources/deployments/exportTemplate/action",
    ]
  }
}
