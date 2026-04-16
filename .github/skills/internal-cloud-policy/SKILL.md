---
name: internal-cloud-policy
description: Use when authoring, comparing, or reviewing concrete cloud policy definitions such as AWS SCPs, Azure Policy, or GCP Org Policy, especially for cross-cloud policy shape or rollout safety.
---

# Cloud Policy Skill

## When to use
- Create or modify governance policy definitions (AWS SCP, Azure Policy, GCP Org Policy).
- Update policy scope, conditions, or effects.
- Normalize policy structure for reviewability and rollout safety.

## Boundary
- Use this skill for concrete policy artifacts or cross-cloud policy comparisons.
- When the main question is IAM, RBAC, operating-model, or guardrail strategy rather than the policy definition itself, treat it as a governance-design problem instead of a policy-definition task.

## Mandatory rules
- Keep scope explicit (organization / folder / subscription / project / management group).
- Keep conditions readable and auditable.
- Prefer deny-by-default for high-risk controls.
- Avoid implicit wildcards unless explicitly justified.
- Keep descriptions and metadata in English.
- Document rollback path before production rollout.

## Policy type decision

| Situation | AWS | Azure | GCP |
|---|---|---|---|
| Prevent actions org-wide | SCP (JSON) | Azure Policy (deny effect) | Org Policy constraint |
| Enforce tagging standards | SCP condition on `aws:RequestTag` | Azure Policy (audit/deny) | Custom Org Policy |
| Restrict regions | SCP condition `aws:RequestedRegion` | Azure Policy `allowedLocations` | `constraints/gcp.resourceLocations` |
| Enforce encryption | SCP + resource policy | Azure Policy (deployIfNotExists) | Org Policy + constraint |

## Templates

Load `references/policy-templates.md` for AWS SCP, Azure Policy, GCP Org Policy, and rollout examples.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using wildcard `"Action": "*"` in an SCP without a `Condition` | Denies everything — locks out the entire org | Always scope with conditions (region, service, tag) |
| Deploying policy directly to prod scope | A bad policy locks out legitimate workloads with no rollback | Test in non-prod scope first, then promote |
| Missing `NotAction` exemptions for essential services | Breaks IAM, billing, support access | Always exempt `iam:*`, `organizations:*`, `support:*` from blanket denies |
| Overly broad Azure Policy `deployIfNotExists` | Auto-remediation creates resources you don't expect | Use `audit` first, promote to `deployIfNotExists` after validation |
| No rollback path documented | When policy causes incident, recovery takes hours | Document disable/removal steps before every rollout |
| Hardcoded account/subscription/project IDs in policy | Non-portable across environments | Use variables or parameters |

## Validation
- Validate syntax in the target format (JSON / HCL).
- Validate policy behavior in non-production scope first.
- Document behavioral impact and rollout scope.
- Ensure rollback path is defined before production rollout.
