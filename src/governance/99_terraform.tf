terraform {
  required_version = ">= 1.3.0"
  backend "azurerm" {
    resource_group_name = "io-infra-rg"
    container_name      = "azurermstate"
    key                 = "azure-governance.tfstate"
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 3.31.0"
    }

    time = {
      source  = "hashicorp/time"
      version = "~> 0.7.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
  }
}
