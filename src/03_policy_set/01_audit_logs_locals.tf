locals {
  audit_logs = {
    reference_ids = {
      api_management           = "api_management"
      app_service              = "app_service"
      application_gateway      = "application_gateway"
      container_registry       = "container_registry"
      cosmos_db                = "cosmos_db"
      event_hub                = "event_hub"
      grafana                  = "grafana"
      keyvault                 = "keyvault"
      kubernetes_cluster       = "kubernetes_cluster"
      log_analytics            = "log_analytics_server"
      postgresql_flexible      = "postgresql_flexible"
      postgresql_single_server = "postgresql_single_server"
      public_ip                = "public_ip"
      subscription             = "subscription_westeurope"
      virtual_network_gateway  = "virtual_network_gateway"
    }
  }
}
