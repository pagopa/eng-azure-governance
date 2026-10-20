data "azurerm_management_group" "pagopa" {
  name = "pagopa"
}

data "azurerm_policy_definition" "this" {
  for_each = local.custom_policy_definition_names

  name                  = each.value
  management_group_name = data.azurerm_management_group.pagopa.name
}
