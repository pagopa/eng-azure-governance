resource "azurerm_policy_definition" "virtual_machine_scale_set_allowed_sku" {
  name                = "virtual_machine_scale_set_allowed_sku"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Virtual Machine Scale Set allowed SKU"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Use Virtual Machine allowed SKU",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/allowed_sku_parameters.json")

  policy_rule = file("./policy_rules/allowed_sku_policy.json")

}