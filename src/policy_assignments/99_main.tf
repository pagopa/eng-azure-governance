provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}

data "azurerm_subscription" "current" {}

data "azurerm_client_config" "current" {}

data "terraform_remote_state" "policy_set" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_set.terraform.tfstate"
  }
}
