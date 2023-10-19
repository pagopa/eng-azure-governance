output "policy_ids" {
  value = [
    azurerm_policy_definition.kubernetes_required_image_sha256.id,
    azurerm_policy_definition.kubernetes_allowed_kubernetes_version.id,
    azurerm_policy_definition.kubernetes_allowed_sku.id,
    azurerm_policy_definition.kubernetes_required_policy_addon.id,
    azurerm_policy_definition.kubernetes_required_defender_profile.id,
  ]
}

output "kubernetes_required_image_sha256_id" {
  value = azurerm_policy_definition.kubernetes_required_image_sha256.id
}

output "kubernetes_allowed_kubernetes_version_id" {
  value = azurerm_policy_definition.kubernetes_allowed_kubernetes_version.id
}

output "kubernetes_allowed_sku_id" {
  value = azurerm_policy_definition.kubernetes_allowed_sku.id
}

output "kubernetes_required_policy_addon_id" {
  value = azurerm_policy_definition.kubernetes_required_policy_addon.id
}

output "kubernetes_required_defender_profile_id" {
  value = azurerm_policy_definition.kubernetes_required_defender_profile.id
}
