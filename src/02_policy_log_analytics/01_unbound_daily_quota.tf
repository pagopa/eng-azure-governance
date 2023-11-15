resource "azurerm_policy_definition" "log_analytics_unbound_daily_quota" {
  name                = "log_analytics_unbound_daily_quota"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Log Analytics unbound daily quota"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Uncap Log Analytics daily quota"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/unbound_daily_quota_parameters.json")

  policy_rule = file("./policy_rules/unbound_daily_quota_policy.json")
}
