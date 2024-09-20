resource "azurerm_role_definition" "applicationgateway_reader" {
  name        = "PagoPA Application Gateway Reader"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Add reader permissions for application gateway"

  permissions {
    actions = [
      "Microsoft.Network/applicationGatewayAvailableRequestHeaders/read",
      "Microsoft.Network/applicationGatewayAvailableResponseHeaders/read",
      "Microsoft.Network/applicationGatewayAvailableServerVariables/read",
      "Microsoft.Network/applicationGatewayAvailableSslOptions/read",
      "Microsoft.Network/applicationGatewayAvailableSslOptions/predefinedPolicies/read",
      "Microsoft.Network/applicationGatewayAvailableWafRuleSets/read",
      "Microsoft.Network/applicationGateways/read",
      "Microsoft.Network/applicationGateways/backendhealth/action",
      "Microsoft.Network/applicationGateways/getBackendHealthOnDemand/action",
      "Microsoft.Network/applicationGateways/getListenerCertificateMetadata/action",
      "Microsoft.Network/applicationGateways/resolvePrivateLinkServiceId/action",
      "Microsoft.Network/applicationGateways/effectiveNetworkSecurityGroups/action",
      "Microsoft.Network/applicationGateways/effectiveRouteTable/action",
      "Microsoft.Network/applicationGateways/appProtectPolicy/getAppProtectPolicy/action",
      "Microsoft.Network/applicationGateways/privateEndpointConnections/read",
      "Microsoft.Network/applicationGateways/privateLinkConfigurations/read",
      "Microsoft.Network/applicationGateways/privateLinkResources/read",
      "Microsoft.Network/applicationGateways/providers/Microsoft.Insights/logDefinitions/read",
      "Microsoft.Network/applicationGateways/providers/Microsoft.Insights/metricDefinitions/read",
      "Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies/read",
    ]
  }
}

