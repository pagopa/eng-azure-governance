provider "azurerm" {
  subscription_id = var.subscription_id
  features {}
}


data "azurerm_subscription" "current" {}

data "azurerm_subscriptions" "available" {}

data "azurerm_client_config" "current" {}

data "terraform_remote_state" "policy_set" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_set.terraform.tfstate"
  }
}
