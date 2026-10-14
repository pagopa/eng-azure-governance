resource "azurerm_policy_definition" "function_app_allowed_linuxfxversion" {
  name                = "function_app_allowed_linuxfxversion"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Function App allowed linuxfxversion"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use Function App allowed linuxfxversion"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_function_app_linuxfxversion_parameters.json")

  policy_rule = file("./policy_rules/allowed_function_app_linuxfxversion_policy.json")

}
