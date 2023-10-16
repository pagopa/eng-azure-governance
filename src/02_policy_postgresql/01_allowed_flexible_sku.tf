resource "azurerm_policy_definition" "postgresql_allowed_flexible_sku" {
  name                = "postgresql_allowed_flexible_sku"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Database for PostgreSQL Flexible allowed SKU"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Use PostgreSQL Flexible allowed SKU",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/allowed_flexible_sku_parameters.json")

  policy_rule = file("./policy_rules/allowed_flexible_sku_policy.json")

}
