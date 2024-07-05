resource "azurerm_role_definition" "dns_zone_reader" {
  name        = "PagoPA DNS Zone Reader"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Read DNS Zones"

  permissions {
    actions = [
      "Microsoft.Network/dnsZones/*/read",
    ]
  }
}
