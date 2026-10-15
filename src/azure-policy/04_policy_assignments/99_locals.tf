locals {
  azure_security_benchmark = {
    id = "/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8"
    policy_dev_waiver_ids = [
      "identityRemoveExternalAccountWithOwnerPermissionsMonitoringNew",
      "identityRemoveExternalAccountWithWritePermissionsMonitoringNew",
      "identityRemoveExternalAccountWithReadPermissionsMonitoringNew",
      "diagnosticsLogsInKeyVaultMonitoring",
      "diagnosticLogsInAppServicesShouldBeEnabledMonitoringEffect",
      "diagnosticsLogsInKubernetesMonitoring",
      "diagnosticsLogsInEventHubMonitoring",
      "identityDesignateLessThanOwnersMonitoring",
      "kubernetesServiceAuthorizedIPRangesEnabledMonitoring",
      "vnetEnableDDoSProtectionMonitoring",
      "aPIManagementServicesShouldUseAVirtualNetworkMonitoringEffect",
      "azureCacheForRedisShouldUsePrivateEndpointMonitoringEffect",
      "azureCosmosDBAccountsShouldHaveFirewallRulesMonitoringEffect",
      "disableUnrestrictedNetworkToStorageAccountMonitoring",
      "storageAccountsShouldRestrictNetworkAccessUsingVirtualNetworkRulesMonitoringEffect",
      "storageAccountShouldUseAPrivateLinkConnectionMonitoringEffect",
      "firewallShouldBeEnabledOnKeyVaultMonitoringEffect",
      "privateEndpointShouldBeConfiguredForKeyVaultMonitoringEffect",
      "containerRegistriesShouldNotAllowUnrestrictedNetworkAccessMonitoringEffect",
      "containerRegistriesShouldUsePrivateLinkMonitoringEffect",
    ]
    policy_dev_mitigated_ids = [

    ]
    policy_uat_waiver_ids = [
      "identityRemoveExternalAccountWithReadPermissionsMonitoringNew",
      "diagnosticsLogsInKeyVaultMonitoring",
      "diagnosticLogsInAppServicesShouldBeEnabledMonitoringEffect",
      "diagnosticsLogsInKubernetesMonitoring",
      "diagnosticsLogsInEventHubMonitoring",
      "identityDesignateLessThanOwnersMonitoring",
      "vnetEnableDDoSProtectionMonitoring",
      "containerRegistriesShouldNotAllowUnrestrictedNetworkAccessMonitoringEffect",
      "containerRegistriesShouldUsePrivateLinkMonitoringEffect",
    ]
    policy_uat_mitigated_ids = [

    ]
    policy_prod_waiver_ids = [
      "diagnosticsLogsInKubernetesMonitoring",
      "identityDesignateLessThanOwnersMonitoring",
      "containerRegistriesShouldNotAllowUnrestrictedNetworkAccessMonitoringEffect",
      "containerRegistriesShouldUsePrivateLinkMonitoringEffect",
    ]
    policy_prod_mitigated_ids = [

    ]
  }
  dns = {
    id = "/providers/Microsoft.Management/managementGroups/pagopa/providers/Microsoft.Authorization/policySetDefinitions/dns"
    policy = {
      dns_required_caa_record_id = "10417603381492996527"
    }
  }
}

locals {
  subscription_blacklist = toset([
    for entry in var.subscription_blacklist : lower(trimspace(entry))
  ])

  subscription_environment_overrides = {
    for subscription, environment in var.subscription_environment_overrides :
    lower(trimspace(subscription)) => environment
  }

  active_subscriptions_by_name = {
    for subscription in data.azurerm_subscriptions.available.subscriptions :
    subscription.display_name => subscription...
    if subscription.state == "Enabled" &&
    !contains(local.subscription_blacklist, lower(subscription.subscription_id)) &&
    !contains(local.subscription_blacklist, lower(subscription.display_name))
  }

  subscription_environments = {
    for name, subscriptions in local.active_subscriptions_by_name : name => lookup(
      local.subscription_environment_overrides,
      lower(subscriptions[0].subscription_id),
      lookup(
        local.subscription_environment_overrides,
        lower(name),
        try(regex("^(dev|uat|prod)-", lower(name))[0], null)
      )
    )
  }

  subscriptions_by_environment = {
    for environment in ["dev", "uat", "prod"] : environment => {
      for name, subscriptions in local.active_subscriptions_by_name : name => subscriptions[0]
      if local.subscription_environments[name] == environment
    }
  }

  policy_set_names = [
    # Global
    "data_sovereignty_eu",
    "dns",
    "tags",
    # DEV
    "api_management_dev",
    "app_service_dev",
    "cosmosdb_dev",
    "log_analytics_dev",
    "redis_dev",
    "virtual_machine_dev",
    "virtual_machine_scale_set_dev",
    # UAT
    "api_management_uat",
    "app_service_uat",
    "cosmosdb_uat",
    "log_analytics_uat",
    "redis_uat",
    "virtual_machine_uat",
    "virtual_machine_scale_set_uat",
    # PROD
    "api_management_prod",
    "app_service_prod",
    "application_gateway_prod",
    "audit_logs",
    "container_apps_prod",
    "cosmosdb_prod",
    "event_hub_prod",
    "key_vault_prod",
    "kubernetes_prod",
    "log_analytics_prod",
    "networking_prod",
    "postgresql_prod",
    "redis_prod",
    "resource_lock",
    "storage_account_prod",
    "virtual_machine_prod",
    "virtual_machine_scale_set_prod",
  ]

  # Parsed parameter values of the audit_logs policy set, keyed by reference_id.
  audit_logs_reference_parameters = {
    for ref in data.azurerm_policy_set_definition.this["audit_logs"].policy_definition_reference :
    ref.reference_id => jsondecode(ref.parameter_values)
    if contains([
      "keyvault_workspaceid",
      "keyvault_storageid_westeurope",
      "keyvault_storageid_northeurope",
      "keyvault_storageid_italynorth",
    ], ref.reference_id)
  }

  # Map consumed by the modules through var.policy_set_ids.
  policy_set_ids = merge(
    { for name, ps in data.azurerm_policy_set_definition.this : "${name}_id" => ps.id },
    {
      audit_logs_workspace_id           = local.audit_logs_reference_parameters.keyvault_workspaceid.logAnalytics.value
      audit_logs_storage_id_westeurope  = local.audit_logs_reference_parameters.keyvault_storageid_westeurope.storageAccount.value
      audit_logs_storage_id_northeurope = local.audit_logs_reference_parameters.keyvault_storageid_northeurope.storageAccount.value
      audit_logs_storage_id_italynorth  = local.audit_logs_reference_parameters.keyvault_storageid_italynorth.storageAccount.value
    }
  )
}
