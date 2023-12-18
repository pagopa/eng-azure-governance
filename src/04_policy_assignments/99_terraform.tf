terraform {
  required_version = ">=1.3.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 3.77.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_assignments_old.terraform.tfstate"
  }
}
