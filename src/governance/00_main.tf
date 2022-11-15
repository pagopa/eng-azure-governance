terraform {
  required_version = ">=1.1.1"

  backend "azurerm" {
    resource_group_name = "io-infra-rg"
    container_name      = "azureadstate"
    key                 = "terraform.tfstate"
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.99.0"
    }

    azuread = {
      source  = "hashicorp/azuread"
      version = "=2.10.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.7.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.1.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }

  skip_provider_registration = true
}

data "azurerm_subscription" "current" {}

data "azurerm_client_config" "current" {}
