resource "azurerm_role_definition" "dns_takeover" {
  name        = "PagoPA DNS Takeover"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Read resources potentially vulnerable to subdomain takeover"

  permissions {
    actions = [
      "Microsoft.Network/dnsZones/*/read",
      "Microsoft.Network/frontDoors/read",
      "Microsoft.Storage/storageAccounts/read",
      "Microsoft.Cdn/profiles/endpoints/read",
      "Microsoft.Cdn/profiles/customdomains/read",
      "Microsoft.Cdn/profiles/endpoints/customdomains/read",
      "Microsoft.Cdn/profiles/afdendpoints/read",
      "Microsoft.Network/trafficManagerProfiles/read",
      "Microsoft.Network/publicIPAddresses/read",
      "Microsoft.ContainerInstance/containerGroups/read",
      "Microsoft.ApiManagement/service/read",
      "Microsoft.Web/sites/Read",
      "Microsoft.Web/sites/slots/Read",
      "Microsoft.ClassicCompute/domainNames/read",
      "Microsoft.ClassicStorage/storageAccounts/read",
    ]
  }
}
