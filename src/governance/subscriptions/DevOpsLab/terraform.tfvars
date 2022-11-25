env_short               = "d"
prefix                  = "dvopla"
subscription_foundation = true

tags_subscription = {
  CostCenter   = "TS310 - PAGAMENTI & SERVIZI"
  Environment  = "dev"
  Owner        = "DevOps"
  BusinessUnit = "DevOps Team"
  Renew        = "v1"
}

#
# 💰 BUDGET
#
action_group_budget_resource_group = "dvopla-d-monitor-rg"
action_group_budget_name           = "dvopladerror"

budget_subscription_enabled = true
budget_subscription_resource_group          = "dvopla-d-monitor-rg"
budget_subscription_amount     = 400
budget_subscription_time_grain = "Monthly"

budget_subscription_notifications = [
  {
    enabled        = true
    threshold      = 80
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Actual"
  },
  {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Actual"
  },
  {
    enabled        = true
    threshold      = 110
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Actual"
  },
  {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Forecasted"
  },
]
