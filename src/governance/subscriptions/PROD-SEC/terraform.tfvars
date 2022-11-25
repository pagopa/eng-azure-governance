env_short               = "p"
env                     = "prod"
prefix                  = "sec"
subscription_foundation = false

#
# 💰 BUDGET
#
action_group_budget_resource_group = "selc-p-monitor-rg"
action_group_budget_name           = "selcperror"

budget_subscription_enabled = false
budget_subscription_resource_group          = "selc-p-monitor-rg"
budget_subscription_amount     = 12000
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
