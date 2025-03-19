resource "azurerm_role_definition" "log_analytics_table_reader" {
  name        = "PagoPA Log Analytics Table Reader"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Read from Log Analytics Table"
  permissions {
    actions = [
      "Microsoft.OperationalInsights/workspaces/read",
      "Microsoft.OperationalInsights/workspaces/query/read",
    ]
    not_actions = [
      "Microsoft.OperationalInsights/workspaces/sharedKeys/read"
    ]
  }
}