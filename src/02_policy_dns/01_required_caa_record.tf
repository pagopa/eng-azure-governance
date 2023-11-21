resource "azurerm_policy_definition" "dns_required_caa_record" {
  name                = "dns_required_caa_record"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA DNS required CAA records"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use DNS required CAA records"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/required_caa_record_parameters.json")

  policy_rule = file("./policy_rules/required_caa_record_policy.json")

}
