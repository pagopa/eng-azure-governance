terraform {
  required_version = ">=1.1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 3.4.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "= 2.10.0"
    }

  }

  backend "azurerm" {}
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}

### cstar_prod
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
  alias           = "cstar_prod"
  subscription_id = local.cstar_prod_subscription_id
}

### io_prod
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
  alias           = "io_prod"
  subscription_id = local.io_prod_subscription_id
}

data "azurerm_subscription" "current" {}

data "azurerm_client_config" "current" {}
