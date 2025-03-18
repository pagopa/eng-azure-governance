resource "azurerm_policy_definition" "log_analytics_allowed_sku" {
  name                = "log_analytics_allowed_sku"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Log Analytics Workspace allowed sku"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Log Analytics Workspace allowed sku are PerGB2018 or LACluster"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_sku_parameters.json")

  policy_rule = file("./policy_rules/allowed_sku_policy.json")

}
