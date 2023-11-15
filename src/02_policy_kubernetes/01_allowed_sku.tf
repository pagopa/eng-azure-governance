resource "azurerm_policy_definition" "kubernetes_allowed_sku" {
  name                = "kubernetes_cluster_allowed_sku"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Kubernetes Cluster allowed SKU"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use Kubernetes Cluster allowed SKU"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_sku_parameters.json")

  policy_rule = file("./policy_rules/allowed_sku_policy.json")

}
