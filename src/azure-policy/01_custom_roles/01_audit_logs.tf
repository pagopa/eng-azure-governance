resource "azurerm_role_definition" "audit_logs_contributor" {
  name        = "PagoPA Audit Logs Contributor"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Add audit logs to resources"

  permissions {
    actions = [
      "Microsoft.Resources/deployments/write",
      "Microsoft.Insights/diagnosticSettings/write",
    ]
  }
}
