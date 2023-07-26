output "policy_ids" {
  value = [
    azurerm_policy_definition.kubernetes_required_image_sha256.id,
  ]
}

output "kubernetes_required_image_sha256_id" {
  value = azurerm_policy_definition.kubernetes_required_image_sha256.id
}
