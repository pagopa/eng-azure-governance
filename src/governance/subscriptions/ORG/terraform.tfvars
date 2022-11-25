env_short = ""
prefix    = "org"

#
# 💰 BUDGET
#
action_group_budget_resource_group = "org-p-monitoring"
action_group_budget_name           = "orgperror"

budget_subscription_enabled = true
budget_subscription_resource_group          = "org-p-monitoring"
budget_subscription_amount     = 70
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
