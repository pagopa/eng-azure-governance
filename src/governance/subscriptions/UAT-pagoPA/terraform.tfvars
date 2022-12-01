env_short = "u"
prefix    = "pagopa"

tags_subscription = {
  CostCenter   = "TS310 - PAGAMENTI & SERVIZI"
  Environment  = "UAT"
  Owner        = "PagoPa"
  BusinessUnit = "PagoPa"
  Renew        = "v1"
}

#
# 💰 BUDGET
#
action_group_budget_resource_group = "pagopa-u-monitor-rg"
action_group_budget_name           = "pagopauerror"

budget_subscription_enabled        = true
budget_subscription_resource_group = "pagopa-u-monitor-rg"
budget_subscription_amount         = 10500
budget_subscription_time_grain     = "Monthly"

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
