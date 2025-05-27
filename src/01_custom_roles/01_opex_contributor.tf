resource "azurerm_role_definition" "opex_contributor" {
  name        = "PagoPA Opex Dashboards Contributor"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Role to manage the Opex Dashboards creation, modification and deletion"

  permissions {
    actions = [
      "Microsoft.Portal/dashboards/write",
      "Microsoft.Portal/dashboards/read",
      "Microsoft.Portal/dashboards/delete",
    ]
  }
}
