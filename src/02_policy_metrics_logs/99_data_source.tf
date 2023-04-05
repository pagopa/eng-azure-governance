data "azurerm_management_group" "pagopa" {
  name = "pagopa"
}

data "azurerm_role_definition" "audit_logs_contributor" {
  name = "PagoPA Audit Logs Contributor"
}

data "azurerm_role_definition" "log_analytics_contributor" {
  name = "Log Analytics Contributor"
}
