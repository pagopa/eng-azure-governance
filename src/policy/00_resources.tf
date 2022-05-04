### CSTAR

data "azurerm_postgresql_server" "cstar_p_postgresql" {
  provider = azurerm.cstar_prod

  name                = "cstar-p-postgresql"
  resource_group_name = "cstar-p-db-rg"
}

### IO

data "azurerm_redis_cache" "io_p_redis_common" {
  provider = azurerm.io_prod

  name                = "io-p-redis-common"
  resource_group_name = "io-p-rg-common"
}

data "azurerm_cosmosdb_account" "io_p_cosmos_api" {
  provider = azurerm.io_prod

  name                = "io-p-cosmos-api"
  resource_group_name = "io-p-rg-internal"
}
