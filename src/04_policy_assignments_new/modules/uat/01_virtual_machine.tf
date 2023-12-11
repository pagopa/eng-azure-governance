resource "azurerm_subscription_policy_assignment" "virtual_machine" {
  name = substr("${local.prefix}virtualmachine", 0, 64)
  display_name         = "PagoPA UAT Virtual Machine"
  policy_definition_id = var.policy_set_ids.virtual_machine_uat_id
  subscription_id  = var.subscription.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
