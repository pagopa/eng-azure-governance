# GCP Governance Guardrail Map

Use this reference when the user needs a clearer split between GCP governance surfaces.

## Quick split

| Need | Use first | Why |
| --- | --- | --- |
| Limit what principals may do across many folders or projects | Org Policy plus scope design | Preventive guardrail |
| Grant execution access to people, groups, or workloads | IAM binding model | Authorization and scope control |
| Remove long-lived workload credentials | workload identity federation | Identity-based runtime access |
| Constrain service account sprawl | service account boundary design | Governance and blast-radius control |
| Standardize security posture | org or folder guardrails plus exceptions | Governance consistency |

## Review questions

1. Is this question about where a control lives or what a principal may do?
2. Is the mechanism preventing action, granting action, or constraining workload identity?
3. Is the scope org, folder set, or project set?
4. What exception path is required, if any?
5. What should be validated before rollout?

## Reminder

- Structure chooses placement.
- Governance chooses permissions and guardrails.
- Operations verifies that the chosen governance behaves as intended after rollout.

## GCP control patterns

| Scenario | Prefer | Why |
| --- | --- | --- |
| Restrict risky services, locations, or default behaviors across many projects | Org Policy at org or folder scope | Central preventive control with visible inheritance |
| Grant operators or workloads access to act in one project set | IAM binding model with explicit scope | Keeps authorization tied to real ownership boundaries |
| Remove external workload keys from delivery systems | Workload identity federation | Keeps trust externalization separate from resource authorization |
| Limit service-account sprawl and privilege creep | Service account boundary design plus scoped IAM | Keeps workload identities purpose-built and reviewable |

## Service-account and federation examples

| Need | Primary control | Review note |
| --- | --- | --- |
| External CI system deploys into GCP | Federation plus narrow project or folder IAM scope | Keep token trust and resource authorization as separate review points |
| Shared automation spans many projects | Purpose-built service account per automation boundary | Avoid one universal service account with broad permissions |
| Human operators need elevated access during incidents | Time-bounded emergency path with explicit approval and logging | Keep routine admin access separate from incident access |

## Exception patterns with audit expectations

| Exception type | Pattern | Audit expectation |
| --- | --- | --- |
| Org Policy exception for a small project set | Scoped exception with reason, owner, and review date | Record business reason, compensating controls, and revalidation date |
| Temporary fallback to service-account keys | Time-bounded exception with rotation and migration plan | Track affected workload, owner, and closure deadline |
| Broader IAM grant required during migration | Narrowly scoped temporary binding with rollback note | Record who approved it, where it applies, and when it expires |
