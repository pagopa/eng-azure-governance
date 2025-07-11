resource "azurerm_policy_definition" "min_execution" {
  name                = "min_execution"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Container Apps audit min execution"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Audit min execution for container apps"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/min_execution_parameters.json")

  policy_rule = file("./policy_rules/min_execution_policy.json")

}
