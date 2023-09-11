data "azurerm_management_group" "pagopa" {
  name = "pagopa"
}

data "terraform_remote_state" "policy_resource_lock" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_resource_lock.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_metrics_logs" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_metrics_logs.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_tags_inherit_from_subscription" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_tags_inherit_from_subscription.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_audit_logs" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_audit_logs.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_application_gateway" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_application_gateway.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_event_hub" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_event_hub.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_dns" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_dns.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_app_service" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_app_service.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_redis" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_redis.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_kubernetes" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_kubernetes.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_cosmosdb" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_cosmosdb.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_data_sovereignty" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_data_sovereignty.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_virtual_machine" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_virtual_machine.terraform.tfstate"
  }
}

data "terraform_remote_state" "policy_log_analytics" {
  backend = "azurerm"

  config = {
    resource_group_name  = "common-azure-governance-rg"
    storage_account_name = "commonazuregovernancest"
    container_name       = "tfstate"
    key                  = "policy_log_analytics.terraform.tfstate"
  }
}
