resource "azurerm_policy_definition" "redis_disable_nosslport" {
  name                = "redis_disable_nosslport"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Redis disable no SSL port"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Disable no SSL Redis port"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/disable_nosslport_parameters.json")

  policy_rule = file("./policy_rules/disable_nosslport_policy.json")

}
