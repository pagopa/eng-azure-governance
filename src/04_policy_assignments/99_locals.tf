locals {
  iso_27001_2013 = {
    id = "/providers/Microsoft.Authorization/policySetDefinitions/89c6cddc-1c73-4ac1-b19c-54d1a15a42f2"
    policy_dev_waiver_ids = [

    ]
    policy_dev_mitigated_ids = [

    ]
    policy_uat_waiver_ids = [

    ]
    policy_uat_mitigated_ids = [

    ]
    policy_prod_waiver_ids = [
      "PreviewAuditMaximumNumberOfOwnersForASubscription", # A maximum of 3 owners should be designated for your subscription
    ]
    policy_prod_mitigated_ids = [
      "PreviewAuditAccountsWithOwnerPermissionsWhoAreNotMfaEnabledOnASubscription", # MFA should be enabled on accounts with read permissions on your subscription
      "PreviewAuditAccountsWithWritePermissionsWhoAreNotMfaEnabledOnASubscription", # MFA should be enabled for accounts with write permissions on your subscription
      "PreviewAuditAccountsWithReadPermissionsWhoAreNotMfaEnabledOnASubscription",  # MFA should be enabled on accounts with owner permissions on your subscription
    ]
  }
  azure_security_benchmark = {
    id = "/providers/Microsoft.Authorization/policySetDefinitions/1f3afdf9-d0c9-4c3d-847f-89da613e70a8"
    policy_dev_waiver_ids = [
      "identityRemoveExternalAccountWithOwnerPermissionsMonitoring",
      "identityRemoveExternalAccountWithOwnerPermissionsMonitoringNew",
      "identityRemoveExternalAccountWithWritePermissionsMonitoring",
      "identityRemoveExternalAccountWithWritePermissionsMonitoringNew",
      "identityRemoveExternalAccountWithReadPermissionsMonitoring",
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
      "identityRemoveExternalAccountWithReadPermissionsMonitoring",
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
  pci_dss_v4 = {
    id = "/providers/Microsoft.Authorization/policySetDefinitions/c676748e-3af9-4e22-bc28-50feed564afb"
  }
  dns = {
    id = "/providers/Microsoft.Management/managementGroups/pagopa/providers/Microsoft.Authorization/policySetDefinitions/dns"
    policy = {
      dns_required_caa_record_id = "10417603381492996527"
    }
  }
  networking = {
    ddosplanid = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-ddos/providers/Microsoft.Network/ddosProtectionPlans/sec-p-ddos-protection"
  }
}
