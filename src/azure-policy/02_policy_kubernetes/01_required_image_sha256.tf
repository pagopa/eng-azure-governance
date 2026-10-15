resource "azurerm_policy_definition" "kubernetes_required_image_sha256" {
  name                = "kubernetes_required_image_sha256"
  policy_type         = "Custom"
  mode                = "Microsoft.Kubernetes.Data"
  display_name        = "PagoPA Kubernetes image must use sha256 tag"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Kubernetes cluster containers should only use sha256 tag"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/required_image_sha256_parameters.json")

  policy_rule = templatefile("./policy_rules/required_image_sha256_policy.json", { templateInfoContent = filebase64("./policy_rules/required_image_sha256_gatekeeper.yaml") })

}
