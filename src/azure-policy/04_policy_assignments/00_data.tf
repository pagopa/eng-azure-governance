data "azurerm_subscriptions" "available" {}

data "azurerm_policy_set_definition" "this" {
  for_each = toset(local.policy_set_names)

  name                  = each.value
  management_group_name = data.azurerm_management_group.pagopa.name
}
