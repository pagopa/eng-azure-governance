resource "azurerm_policy_definition" "postgresql_required_engine_version" {
  name                = "postgresql_required_engine_version"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Database for PostgreSQL Flexible required version"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use greater versions for PostgreSQL flexible"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/required_engine_version_parameters.json")

  policy_rule = file("./policy_rules/required_engine_version_policy.json")
}
