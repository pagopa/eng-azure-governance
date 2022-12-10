data "azurerm_management_group" "pagamenti_servizi_cloud_dev" {
  name = "pagamenti_servizi_cloud_dev"
}

locals {
  pagamenti_servizi_cloud_dev_prefix = "pscd"
}
