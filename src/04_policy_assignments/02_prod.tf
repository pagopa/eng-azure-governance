data "azurerm_management_group" "prod" {
  name = "prod"
}

locals {
  prod_prefix = "prod"
}

resource "azurerm_management_group_policy_assignment" "prod_iso_27001_2013" {
  name                 = "${local.prod_prefix}iso270012013"
  display_name         = "ISO 27001:2013"
  policy_definition_id = local.iso_27001_2013.id
  management_group_id  = data.azurerm_management_group.prod.id

  parameters = jsonencode(
    {
      metricsEnabled-7f89b1eb-583c-429a-8828-af049802c1d9 = {
        value = false
      }
    }
  )

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_exemption" "prod_iso_27001_2013_mitigated" {
  name                            = "${azurerm_management_group_policy_assignment.prod_iso_27001_2013.name}-mitigated"
  management_group_id             = data.azurerm_management_group.prod.id
  policy_assignment_id            = azurerm_management_group_policy_assignment.prod_iso_27001_2013.id
  exemption_category              = "Mitigated"
  description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960596/Azure+Policy+-+ISO+27001+2013"
  policy_definition_reference_ids = local.iso_27001_2013.policy_prod_mitigated_ids
}

resource "azurerm_management_group_policy_exemption" "prod_iso_27001_2013_waiver" {
  name                            = "${azurerm_management_group_policy_assignment.prod_iso_27001_2013.name}-waiver"
  management_group_id             = data.azurerm_management_group.prod.id
  policy_assignment_id            = azurerm_management_group_policy_assignment.prod_iso_27001_2013.id
  exemption_category              = "Waiver"
  description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960596/Azure+Policy+-+ISO+27001+2013"
  policy_definition_reference_ids = local.iso_27001_2013.policy_prod_waiver_ids
}

resource "azurerm_management_group_policy_exemption" "prod_azure_security_benchmark_waiver" {
  name                            = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}${local.prod_prefix}-waiver"
  management_group_id             = data.azurerm_management_group.prod.id
  policy_assignment_id            = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
  exemption_category              = "Waiver"
  description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
  policy_definition_reference_ids = local.azure_security_benchmark.policy_prod_waiver_ids
}

resource "azurerm_management_group_policy_assignment" "prod_resource_lock" {
  name                 = "${local.prod_prefix}resourcelock"
  display_name         = "PagoPA Resource lock"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.resource_lock_id
  management_group_id  = data.azurerm_management_group.prod.id

  location = var.location
  enforce  = true
  identity {
    type = "SystemAssigned"
  }

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_role_assignment" "prod_resource_lock_contributor" {
  scope                = data.azurerm_management_group.prod.id
  role_definition_name = "PagoPA Resource Lock Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_resource_lock.identity[0].principal_id
}

resource "azurerm_management_group_policy_assignment" "prod_audit_logs" {
  name                 = "${local.prod_prefix}auditlogs"
  display_name         = "PagoPA Audit logs"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.audit_logs_id
  management_group_id  = data.azurerm_management_group.prod.id

  location = var.location
  enforce  = true
  identity {
    type = "SystemAssigned"
  }

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_role_assignment" "prod_audit_logs_monitoring_contributor" {
  scope                = data.azurerm_management_group.prod.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "prod_audit_logs_contributor_log_analytics" {
  scope                = data.terraform_remote_state.policy_set.outputs.audit_logs_workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "prod_audit_logs_contributor_storage_westeurope" {
  scope                = data.terraform_remote_state.policy_set.outputs.audit_logs_storage_id_westeurope
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_audit_logs.identity[0].principal_id
}

resource "azurerm_management_group_policy_assignment" "prod_storage_account" {
  name                 = "${local.prod_prefix}storageaccount"
  display_name         = "PagoPA Storage Account"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.storage_account_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_application_gateway" {
  name                 = "${local.prod_prefix}applicationgateway"
  display_name         = "PagoPA Application Gateway"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.application_gateway_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_event_hub" {
  name                 = "${local.prod_prefix}eventhub"
  display_name         = "PagoPA EventHub"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.event_hub_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_kubernetes" {
  name                 = "${local.prod_prefix}kubernetes"
  display_name         = "PagoPA Kubernetes"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.kubernetes_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_app_service" {
  name                 = "${local.prod_prefix}appservice"
  display_name         = "PagoPA App Service"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.app_service_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_redis" {
  name                 = "${local.prod_prefix}redis"
  display_name         = "PagoPA Redis"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.redis_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_cosmosdb" {
  name                 = "${local.prod_prefix}cosmosdb"
  display_name         = "PagoPA CosmosDB"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.cosmosdb_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_networking" {
  name                 = "${local.prod_prefix}networking"
  display_name         = "PagoPA Networking"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.networking_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  location = var.location
  enforce  = true
  identity {
    type = "SystemAssigned"
  }

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_role_assignment" "prod_network_contributor" {
  scope                = data.azurerm_management_group.prod.id
  role_definition_name = "Network Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_networking.identity[0].principal_id
}

resource "azurerm_role_assignment" "prod_network_contributor_ddosplan" {
  scope                = local.networking.ddosplanid
  role_definition_name = "Network Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_networking.identity[0].principal_id
}

resource "azurerm_management_group_policy_assignment" "prod_virtual_machine" {
  name                 = "${local.prod_prefix}virtualmachine"
  display_name         = "PagoPA Virtual Machine"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.virtual_machine_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_virtual_machine_scael_set" {
  name                 = "${local.prod_prefix}vmscaleset"
  display_name         = "PagoPA Virtual Machine Scale Set"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.virtual_machine_scale_set_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_api_management" {
  name                 = "${local.prod_prefix}apimanagement"
  display_name         = "PagoPA Api Management"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.api_management_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_log_analytics" {
  name                 = "${local.prod_prefix}loganalytics"
  display_name         = "PagoPA Log Analytics"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.log_analytics_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_postgresql" {
  name                 = "${local.prod_prefix}postgresql"
  display_name         = "PagoPA PostgreSQL"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.postgresql_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_key_vault" {
  name                 = "${local.prod_prefix}keyvault"
  display_name         = "PagoPA Key Vault"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.key_vault_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_network" {
  name                 = "${local.prod_prefix}network"
  display_name         = "PagoPA network"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.network_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "prod_container_apps" {
  name                 = "${local.prod_prefix}containerapps"
  display_name         = "PagoPA Container Apps"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.container_apps_prod_id
  management_group_id  = data.azurerm_management_group.prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}