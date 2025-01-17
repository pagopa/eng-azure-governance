resource "azurerm_policy_definition" "log_analytics_link_dedicated_cluster" {
  name                = "log_analytics_link_dedicated_cluster"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Log Analytics Workspace must be linked to dedicated cluster"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Link Log Analytics Workspace to dedicated cluster"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/link_dedicated_cluster_parameters.json")

  policy_rule = file("./policy_rules/link_dedicated_cluster_policy.json")

}
