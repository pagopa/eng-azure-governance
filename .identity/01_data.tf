data "azurerm_management_group" "pagopa" {
  name = "pagopa"
}

data "azurerm_storage_account" "tfinforg" {
  name                = "tfinforg"
  resource_group_name = "terraform-state-rg"
}

data "azurerm_resource_group" "identity" {
  name     = "${local.project}-identity-rg"
}
