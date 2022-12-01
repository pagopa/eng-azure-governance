data "azurerm_resource_group" "monitoring_rg" {
  name = var.budget_subscription_resource_group
}

data "azurerm_monitor_action_group" "budget_ag" {
  resource_group_name = var.action_group_budget_resource_group
  name                = var.action_group_budget_name
}

# ----------------------------------------------------------------------

#https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/consumption_budget_subscription
resource "azurerm_consumption_budget_subscription" "governance_budget" {
  count = var.budget_subscription_enabled ? 1: 0

  name            = "${var.prefix}-${var.env_short}-governance-budget-${var.tags_subscription.Renew}"
  subscription_id = data.azurerm_subscription.current.id

  amount     = var.budget_subscription_amount
  time_grain = var.budget_subscription_time_grain

  #https://learn.microsoft.com/en-us/azure/cost-management-billing/understand/understand-usage#list-of-terms-and-descriptions
  filter {
    dimension {
      #https://learn.microsoft.com/en-us/azure/cost-management-billing/understand/understand-usage#list-of-terms-and-descriptions
      name = "ChargeType"
      values = [
        "Usage"
      ]
    }
  }

  time_period {
    start_date = formatdate("YYYY-MM-01'T'00:00:00Z", timestamp())
  }

  dynamic "notification" {
    for_each = var.budget_subscription_notifications
    content {
      enabled        = notification.value["enabled"]
      threshold      = notification.value["threshold"]
      operator       = notification.value["operator"]
      threshold_type = notification.value["threshold_type"]
      contact_groups = [data.azurerm_monitor_action_group.budget_ag.id]
    }
  }

  lifecycle {
    ignore_changes = [
      # Ignore changes to tags, e.g. because a management agent
      # updates these based on some ruleset managed elsewhere.
      time_period,
    ]
  }
}
