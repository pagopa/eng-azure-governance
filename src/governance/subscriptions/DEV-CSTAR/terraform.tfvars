env_short = "d"
prefix    = "cstar"

#
# 💰 BUDGET
#
action_group_budget_resource_group = "cstar-d-monitor-rg"
action_group_budget_name           = "cstarderror"

budget_subscription_enabled = true
budget_subscription_resource_group          = "cstar-d-monitor-rg"
budget_subscription_amount     = 1700
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
