resource "azurerm_policy_definition" "app_service_allowed_sku" {
  name                = "app_service_allowed_sku"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA App Service allowed SKU"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use App Service allowed SKU"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_app_service_sku_parameters.json")

  policy_rule = file("./policy_rules/allowed_app_service_sku_policy.json")
}
