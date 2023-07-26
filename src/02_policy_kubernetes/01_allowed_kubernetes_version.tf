resource "azurerm_policy_definition" "kubernetes_allowed_kubernetes_version" {
  name                = "kubernetes_allowed_kubernetes_version"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Kubernetes allowed versions"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Kubernetes allowed versions",
		      "Severity": "High"
        }
    }
METADATA

  # az aks get-versions --location westeurope --output table
  parameters = file("./policy_rules/allowed_kubernetes_version_parameters.json")

  policy_rule = file("./policy_rules/allowed_kubernetes_version_policy.json")

}
