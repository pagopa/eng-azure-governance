provider "azurerm" {
  skip_provider_registration = true

  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }

  skip_provider_registration = true
}

data "azurerm_subscription" "current" {}

data "azurerm_client_config" "current" {}
