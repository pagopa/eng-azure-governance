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
