resource "azurerm_policy_definition" "kubernetes_required_defender_profile" {
  name                = "kubernetes_required_defender_profile"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Kubernetes cluster should enable Defender Profile"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Kubernetes cluster should enable Defender Profile",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/required_defender_profile_parameters.json")

  policy_rule = file("./policy_rules/required_defender_profile_policy.json")
}
