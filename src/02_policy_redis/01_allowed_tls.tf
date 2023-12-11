resource "azurerm_policy_definition" "redis_allowed_tls" {
  name                = "redis_allowed_tls"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Redis allowed tls"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use Redis allowed tls"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_tls_parameters.json")

  policy_rule = file("./policy_rules/allowed_tls_policy.json")

}
