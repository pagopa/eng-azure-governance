data "azurerm_management_group" "pagopa" {
  name = "pagopa"
}

data "azurerm_management_group" "landing_zones" {
  name = "landing_zones"
}

data "azurerm_management_group" "platform_zones" {
  name = "platform_zones"
}

data "azurerm_management_group" "root_sl_pagamenti_servizi" {
  name = "root_sl_pagamenti_servizi"
}

data "azurerm_management_group" "dev_sl_pagamenti_servizi" {
  name = "dev_sl_pagamenti_servizi"
}

data "azurerm_management_group" "uat_sl_pagamenti_servizi" {
  name = "uat_sl_pagamenti_servizi"
}

data "azurerm_management_group" "prod_sl_pagamenti_servizi" {
  name = "prod_sl_pagamenti_servizi"
}

data "azurerm_management_group" "devops_sl_pagamenti_servizi" {
  name = "devops_sl_pagamenti_servizi"
}
