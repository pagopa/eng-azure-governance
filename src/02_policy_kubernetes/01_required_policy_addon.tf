resource "azurerm_policy_definition" "kubernetes_required_policy_addon" {
  name                = "kubernetes_required_policy_addon"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Kubernetes cluster containers should enable Policy Add-on"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Kubernetes cluster containers should enable Policy Add-on",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/required_policy_addon_parameters.json")

  policy_rule = file("./policy_rules/required_policy_addon_policy.json")
}
