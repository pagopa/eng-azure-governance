resource "azurerm_subscription_policy_assignment" "kubernetes" {
  name                 = substr("${local.prefix}kubernetes", 0, 64)
  display_name         = "PagoPA DEV Kubernetes"
  policy_definition_id = var.policy_set_ids.kubernetes_dev_id
  subscription_id      = var.subscription.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
