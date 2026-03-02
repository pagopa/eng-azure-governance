---
name: cloud-policy
description: Create or modify governance policies for AWS SCP, Azure Policy, and GCP Org Policy.
---

# Cloud Policy Skill

## When to use
- Create or modify governance policy definitions.
- Update policy scope, conditions, or effects.
- Normalize policy structure for reviewability and rollout safety.

## Mandatory rules
- Keep scope explicit (organization/folder/subscription/project/management group).
- Keep conditions readable and auditable.
- Prefer deny-by-default for high-risk controls.
- Avoid implicit wildcards unless explicitly justified.
- Keep descriptions and metadata in English.

## Folder placement conventions
- AWS SCP: `src/scp/policies/` or equivalent organization-policy folder.
- Azure Policy: `src/**/policy_rules/` (rule JSON) and policy definition `.tf` in matching module.
- GCP Org Policy: policy customizations in `src/**/policy*` with assignment split by scope.

## Minimal cloud templates

### AWS SCP (JSON)
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

### Azure Policy rule (JSON)
```json
{
  "if": {
    "field": "type",
    "equals": "Microsoft.Network/publicIPAddresses"
  },
  "then": {
    "effect": "deny"
  }
}
```

### GCP Org Policy (Terraform)
```hcl
resource "google_org_policy_policy" "disable_sa_key_creation" {
  name   = "organizations/${var.org_id}/policies/iam.disableServiceAccountKeyCreation"
  parent = "organizations/${var.org_id}"

  spec {
    rules {
      enforce = true
    }
  }
}
```

## Validation
- Validate syntax in the target format (JSON/HCL).
- Validate policy behavior in non-production scope first.
- Document behavioral impact and rollout scope.
- Ensure rollback path is defined before production rollout.
