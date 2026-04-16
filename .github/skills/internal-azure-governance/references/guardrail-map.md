# Azure Governance Guardrail Map

Use this reference when the user needs a clearer split between Azure governance surfaces.

## Quick split

| Need | Use first | Why |
| --- | --- | --- |
| Limit what principals may do across many subscriptions | Azure Policy plus scope design | Preventive or detective guardrail |
| Grant execution access to people or groups | RBAC role assignment model | Authorization and scope control |
| Constrain privileged access | PIM or PAM posture | Time-bound elevation and review |
| Remove long-lived credentials from workloads | managed identity or federation pattern | Identity-based runtime access |
| Standardize metadata expectations | naming and tagging guardrails | Governance consistency |

## Review questions

1. Is this question about where a control lives or what a principal may do?
2. Is the mechanism preventing action, granting action, or constraining privileged access?
3. Is the scope management group, subscription set, or single subscription?
4. What exception path is required, if any?
5. What should be validated before rollout?

## Reminder

- Structure chooses placement.
- Governance chooses permissions and guardrails.
- Operations verifies that the chosen governance behaves as intended after rollout.

## Azure control patterns

| Scenario | Prefer | Why |
| --- | --- | --- |
| Enforce allowed locations, SKUs, or network posture across many subscriptions | Azure Policy or initiative at management-group scope | Central preventive or detective guardrail with visible inheritance |
| Grant engineers or groups access to operate resources | RBAC role assignments with explicit scope | Keeps authorization tied to real ownership boundaries |
| Limit standing privilege for sensitive operations | PIM or PAM posture | Elevation becomes time-bound, reviewable, and auditable |
| Remove secrets from workload-to-service access | Managed identity or federation pattern | Keeps workload identity separate from human access grants |

## Identity and federation examples

| Need | Primary control | Review note |
| --- | --- | --- |
| Workload in Azure needs access to Azure resources | Managed identity plus scoped RBAC | Identity type does not replace least-privilege scope design |
| External CI system deploys into Azure | Federation plus narrow RBAC scope | Keep token trust and resource authorization as separate review points |
| Human operators need elevated production access | PIM-backed role path with approval and duration controls | Keep emergency and routine elevation paths distinct |

## Exception patterns with audit expectations

| Exception type | Pattern | Audit expectation |
| --- | --- | --- |
| Policy exception for a subset of subscriptions | Scoped exemption with reason, owner, and expiry or review date | Record business reason, compensating controls, and revalidation date |
| Temporary elevated operator access | PIM assignment with time bound and approval path | Record approver, duration, and activity evidence |
| Workload cannot yet use managed identity | Time-bounded secret-based fallback with closure plan | Track affected app, owner, rotation path, and migration deadline |
