resource "azurerm_role_definition" "export_deployments_template" {
  name        = "PagoPA Export Deployments Template"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Export Deployments Template"

  permissions {
    actions = [
      "Microsoft.Resources/deployments/exportTemplate/action",
    ]
  }
}
