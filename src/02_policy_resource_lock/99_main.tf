provider "azurerm" {
  subscription_id = var.subscription_id
  features {}
}


data "azurerm_subscription" "current" {}

data "azurerm_client_config" "current" {}
