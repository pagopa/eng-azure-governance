# Cloud Policy Templates

## AWS SCP — Region restriction

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnapprovedRegions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": ["eu-south-1", "eu-west-1"]
        }
      }
    }
  ]
}
```

## AWS SCP — Enforce encryption at rest

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedS3",
      "Effect": "Deny",
      "Action": "s3:PutObject",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "aws:kms"
        }
      }
    }
  ]
}
```

## AWS SCP — Tag enforcement

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyMissingCostCenter",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "rds:CreateDBInstance",
        "lambda:CreateFunction"
      ],
      "Resource": "*",
      "Condition": {
        "Null": {
          "aws:RequestTag/CostCenter": "true"
        }
      }
    }
  ]
}
```

## AWS SCP — Essential service exemptions

Always include these exemptions in blanket deny SCPs:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEssentialServices",
      "Effect": "Allow",
      "Action": [
        "iam:*",
        "organizations:*",
        "support:*",
        "sts:*",
        "budgets:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## Azure Policy — Deny public IP addresses

```json
{
  "properties": {
    "displayName": "Deny public IP addresses",
    "description": "Prevents creation of public IP addresses",
    "mode": "All",
    "policyRule": {
      "if": {
        "field": "type",
        "equals": "Microsoft.Network/publicIPAddresses"
      },
      "then": {
        "effect": "deny"
      }
    }
  }
}
```

## Azure Policy — Enforce allowed locations

```json
{
  "properties": {
    "displayName": "Allowed locations",
    "description": "Restrict resource creation to approved regions",
    "mode": "All",
    "parameters": {
      "allowedLocations": {
        "type": "Array",
        "metadata": { "displayName": "Allowed locations" },
        "defaultValue": ["westeurope", "northeurope"]
      }
    },
    "policyRule": {
      "if": {
        "not": {
          "field": "location",
          "in": "[parameters('allowedLocations')]"
        }
      },
      "then": {
        "effect": "deny"
      }
    }
  }
}
```

## Azure Policy — Audit unencrypted storage

```json
{
  "properties": {
    "displayName": "Audit storage accounts without encryption",
    "mode": "All",
    "policyRule": {
      "if": {
        "allOf": [
          { "field": "type", "equals": "Microsoft.Storage/storageAccounts" },
          { "field": "Microsoft.Storage/storageAccounts/encryption.services.blob.enabled", "notEquals": true }
        ]
      },
      "then": {
        "effect": "audit"
      }
    }
  }
}
```

## GCP Org Policy — Disable SA key creation (Terraform)

```hcl
resource "google_org_policy_policy" "disable_sa_key_creation" {
  name   = "organizations/${var.org_id}/policies/iam.disableServiceAccountKeyCreation"
  parent = "organizations/${var.org_id}"
  spec {
    rules { enforce = true }
  }
}
```

## GCP Org Policy — Restrict resource locations (Terraform)

```hcl
resource "google_org_policy_policy" "restrict_locations" {
  name   = "organizations/${var.org_id}/policies/gcp.resourceLocations"
  parent = "organizations/${var.org_id}"
  spec {
    rules {
      values {
        allowed_values = ["in:eu-locations"]
      }
    }
  }
}
```

## GCP Org Policy — Require OS Login (Terraform)

```hcl
resource "google_org_policy_policy" "require_os_login" {
  name   = "organizations/${var.org_id}/policies/compute.requireOsLogin"
  parent = "organizations/${var.org_id}"
  spec {
    rules { enforce = true }
  }
}
```

## Rollout checklist

1. **Draft** → write the policy definition.
2. **Review** → peer review with platform/security team.
3. **Test** → deploy to non-production scope (test OU / sandbox subscription / test folder).
4. **Monitor** → verify expected behavior in CloudTrail / Activity Log / Cloud Audit Logs.
5. **Promote** → apply to production scope.
6. **Document** → record rollback path and owner.
