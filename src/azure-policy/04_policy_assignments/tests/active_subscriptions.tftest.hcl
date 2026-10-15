mock_provider "azurerm" {
  mock_data "azurerm_management_group" {
    defaults = {
      id   = "/providers/Microsoft.Management/managementGroups/pagopa"
      name = "pagopa"
    }
  }

  mock_data "azurerm_policy_set_definition" {
    defaults = {
      id = "/providers/Microsoft.Management/managementGroups/pagopa/providers/Microsoft.Authorization/policySetDefinitions/test"
      policy_definition_reference = [
        {
          reference_id     = "keyvault_workspaceid"
          parameter_values = "{\"logAnalytics\":{\"value\":\"/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/test/providers/Microsoft.OperationalInsights/workspaces/test\"}}"
        },
        {
          reference_id     = "keyvault_storageid_westeurope"
          parameter_values = "{\"storageAccount\":{\"value\":\"/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/test/providers/Microsoft.Storage/storageAccounts/testwe\"}}"
        },
        {
          reference_id     = "keyvault_storageid_northeurope"
          parameter_values = "{\"storageAccount\":{\"value\":\"/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/test/providers/Microsoft.Storage/storageAccounts/testne\"}}"
        },
        {
          reference_id     = "keyvault_storageid_italynorth"
          parameter_values = "{\"storageAccount\":{\"value\":\"/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/test/providers/Microsoft.Storage/storageAccounts/testit\"}}"
        },
      ]
    }
  }

  mock_data "azurerm_subscriptions" {
    defaults = {
      subscriptions = [for subscription in [
        { name = "DEV-Active", state = "Enabled", number = 1 },
        { name = "DEV-Disabled", state = "Disabled", number = 2 },
        { name = "DEV-Deleted", state = "Deleted", number = 3 },
        { name = "UAT-Active", state = "Enabled", number = 4 },
        { name = "UAT-Warned", state = "Warned", number = 5 },
        { name = "PROD-Active", state = "Enabled", number = 6 },
        { name = "PROD-PastDue", state = "PastDue", number = 7 },
        { name = "DevOpsLab", state = "Enabled", number = 8 },
        { name = "DevOpsAutomation", state = "Enabled", number = 9 },
        { name = "ORG", state = "Enabled", number = "a" },
        { name = "Common", state = "Enabled", number = "b" },
        { name = "GitHub", state = "Enabled", number = "c" },
        { name = "PDA-Migration-PostgreSQL", state = "Enabled", number = "d" },
        { name = "dev-New", state = "Enabled", number = "e" },
        { name = "uat-New", state = "Enabled", number = "f" },
        { name = "Sandbox", state = "Enabled", number = 0 },
        ] : {
        id              = "/subscriptions/00000000-0000-0000-0000-00000000000${subscription.number}"
        subscription_id = "00000000-0000-0000-0000-00000000000${subscription.number}"
        display_name    = subscription.name
        state           = subscription.state
      }]
    }
  }
}

variables {
  subscription_id        = "00000000-0000-0000-0000-000000000001"
  metadata_category_name = "Test"
  location               = "westeurope"
  subscription_environment_overrides = {
    DevOpsLab                = "dev"
    DevOpsAutomation         = "prod"
    ORG                      = "prod"
    Common                   = "prod"
    GitHub                   = "prod"
    PDA-Migration-PostgreSQL = "prod"
    Sandbox                  = "uat"
  }
}

run "active_subscriptions_are_discovered_and_classified" {
  command = plan

  assert {
    condition = (
      toset(keys(module.dev_assignments)) == toset(["DEV-Active", "dev-New", "DevOpsLab"]) &&
      toset(keys(module.uat_assignments)) == toset(["UAT-Active", "uat-New", "Sandbox"]) &&
      toset(keys(module.prod_assignments)) == toset([
        "PROD-Active", "DevOpsAutomation", "ORG", "Common", "GitHub", "PDA-Migration-PostgreSQL"
      ])
    )
    error_message = "Discover all Enabled subscriptions, classify names case-insensitively, and preserve existing module keys."
  }
}

run "blacklist_excludes_names_and_subscription_ids" {
  command = plan

  variables {
    subscription_blacklist = [" dev-active ", "00000000-0000-0000-0000-000000000006", "org", "NOT-PRESENT"]
  }

  assert {
    condition = (
      toset(keys(module.dev_assignments)) == toset(["dev-New", "DevOpsLab"]) &&
      toset(keys(module.uat_assignments)) == toset(["UAT-Active", "uat-New", "Sandbox"]) &&
      toset(keys(module.prod_assignments)) == toset([
        "DevOpsAutomation", "Common", "GitHub", "PDA-Migration-PostgreSQL"
      ])
    )
    error_message = "Blacklist names and IDs must exclude matching subscriptions without affecting other assignments."
  }
}

run "only_inactive_subscriptions_produce_no_environment_modules" {
  command = plan

  override_data {
    target = data.azurerm_subscriptions.available
    values = {
      subscriptions = [for state in ["Disabled", "Deleted", "Warned", "PastDue"] : {
        id              = "/subscriptions/00000000-0000-0000-0000-000000000001"
        subscription_id = "00000000-0000-0000-0000-000000000001"
        display_name    = "DEV-${state}"
        state           = state
      }]
    }
  }

  assert {
    condition = (
      length(module.dev_assignments) == 0 &&
      length(module.uat_assignments) == 0 &&
      length(module.prod_assignments) == 0
    )
    error_message = "Inactive subscriptions must not create any environment modules."
  }
}

run "blacklist_can_exclude_every_active_subscription" {
  command = plan

  variables {
    subscription_blacklist = [
      "DEV-Active", "dev-New", "DevOpsLab", "UAT-Active", "uat-New", "PROD-Active",
      "DevOpsAutomation", "ORG", "Common", "GitHub", "PDA-Migration-PostgreSQL", "Sandbox"
    ]
  }

  assert {
    condition = (
      length(module.dev_assignments) == 0 &&
      length(module.uat_assignments) == 0 &&
      length(module.prod_assignments) == 0
    )
    error_message = "Blacklisting every active subscription must leave no environment modules."
  }
}

run "duplicate_active_subscription_names_are_rejected" {
  command = plan

  override_data {
    target = data.azurerm_subscriptions.available
    values = {
      subscriptions = [for number in [1, 2] : {
        id              = "/subscriptions/00000000-0000-0000-0000-00000000000${number}"
        subscription_id = "00000000-0000-0000-0000-00000000000${number}"
        display_name    = "DEV-Active"
        state           = "Enabled"
      }]
    }
  }

  expect_failures = [output.subscriptions_by_environment]
}

run "subscription_id_override_takes_precedence_over_name" {
  command = plan

  variables {
    subscription_environment_overrides = {
      "00000000-0000-0000-0000-000000000001" = "uat"
      NoPrefix                               = "dev"
    }
  }

  override_data {
    target = data.azurerm_subscriptions.available
    values = {
      subscriptions = [{
        id              = "/subscriptions/00000000-0000-0000-0000-000000000001"
        subscription_id = "00000000-0000-0000-0000-000000000001"
        display_name    = "NoPrefix"
        state           = "Enabled"
      }]
    }
  }

  assert {
    condition = (
      length(module.dev_assignments) == 0 &&
      toset(keys(module.uat_assignments)) == toset(["NoPrefix"]) &&
      length(module.prod_assignments) == 0
    )
    error_message = "An ID override must take precedence over a display-name override."
  }
}

run "unclassified_active_subscriptions_are_rejected" {
  command = plan

  variables {
    subscription_environment_overrides = {}
  }

  override_data {
    target = data.azurerm_subscriptions.available
    values = {
      subscriptions = [{
        id              = "/subscriptions/00000000-0000-0000-0000-000000000001"
        subscription_id = "00000000-0000-0000-0000-000000000001"
        display_name    = "NoPrefix"
        state           = "Enabled"
      }]
    }
  }

  expect_failures = [output.subscriptions_by_environment]
}

run "blacklisted_unclassified_subscriptions_are_ignored" {
  command = plan

  variables {
    subscription_blacklist = ["NoPrefix"]
  }

  override_data {
    target = data.azurerm_subscriptions.available
    values = {
      subscriptions = [{
        id              = "/subscriptions/00000000-0000-0000-0000-000000000001"
        subscription_id = "00000000-0000-0000-0000-000000000001"
        display_name    = "NoPrefix"
        state           = "Enabled"
      }]
    }
  }

  assert {
    condition = (
      length(module.dev_assignments) == 0 &&
      length(module.uat_assignments) == 0 &&
      length(module.prod_assignments) == 0
    )
    error_message = "A blacklisted subscription must not require an environment override."
  }
}
