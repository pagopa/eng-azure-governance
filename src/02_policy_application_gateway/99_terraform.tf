terraform {
  required_version = ">=1.1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 3.28.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "= 2.29.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_application_gateway.terraform.tfstate"
  }
}
