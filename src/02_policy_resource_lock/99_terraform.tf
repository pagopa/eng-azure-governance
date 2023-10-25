terraform {
  required_version = ">=1.3.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 3.77.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_resource_lock.terraform.tfstate"
  }
}
