data "azurerm_management_group" "pagopa" {
  name = "pagopa"
}

data "terraform_remote_state" "policy_resource_lock" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_resource_lock.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_metrics_logs" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_metrics_logs.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_tags" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_tags.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_audit_logs" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_audit_logs.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_application_gateway" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_application_gateway.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_event_hub" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_event_hub.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_dns" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_dns.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_app_service" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_app_service.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_redis" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_redis.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_kubernetes" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_kubernetes.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_cosmosdb" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_cosmosdb.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_data_sovereignty" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_data_sovereignty.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_virtual_machine" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_virtual_machine.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_log_analytics" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_log_analytics.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_virtual_machine_scale_set" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_virtual_machine_scale_set.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_postgresql" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_postgresql.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_networking" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_networking.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_api_management" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_api_management.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_container_apps" {
  backend = "azurerm"

  config = {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfinforg"
    container_name       = "terraform-state"
    key                  = "eng-azure-governance.policy_container_apps.terraform.tfstate"
  }
}
