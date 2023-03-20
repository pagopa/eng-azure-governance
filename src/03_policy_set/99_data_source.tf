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
