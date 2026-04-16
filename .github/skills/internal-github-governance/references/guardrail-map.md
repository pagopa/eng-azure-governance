# GitHub Governance Guardrail Map

Use this reference when the user needs a clearer split between GitHub governance surfaces.

## Quick split

| Need | Use first | Why |
| --- | --- | --- |
| Enforce branch and merge standards broadly | rulesets or branch protection | Preventive repository guardrail |
| Limit what automations may do | GitHub Apps or Actions permissions | Automation trust boundary |
| Remove long-lived cloud secrets from workflows | OIDC posture | Federated workload access |
| Separate release control from daily development | environments plus approvals | Deployment guardrail |
| Govern AI feature use | Copilot governance | Policy, entitlement, and visibility control |

## Review questions

1. Is this question about where a control lives or what an actor may do?
2. Is the mechanism preventing action, granting action, or constraining automation?
3. Is the scope enterprise, organization, repository set, or environment?
4. What exception path is required, if any?
5. What should be validated before rollout?

## Reminder

- Strategic absorbs light enterprise, org, and repo-shape decisions.
- Governance chooses permissions and guardrails.
- Operations verifies that the chosen governance behaves as intended after rollout.

## GitHub control patterns

| Scenario | Prefer | Why |
| --- | --- | --- |
| Enforce merge, review, and branch standards broadly | Rulesets or branch protection at the appropriate scope | Central preventive guardrail with explicit inheritance |
| Limit what automations may do in repositories | GitHub App or scoped Actions permissions | Keeps automation trust and authorization reviewable |
| Protect production delivery steps | Environments plus approvals and secret boundaries | Separates release control from daily development activity |
| Reduce static cloud secrets in workflows | OIDC posture with cloud-side least privilege | Keeps federation separate from repository permissions |

## Trust-boundary examples

| Need | Primary control | Review note |
| --- | --- | --- |
| Repository automation needs repo-level write operations | GitHub App with narrow repository permissions | Keep installation scope and token privileges explicit |
| Workflow needs cloud access without long-lived credentials | OIDC trust plus environment or branch guardrails | Review both the GitHub trust boundary and the cloud-side role scope |
| Reusable workflow needs elevated deployment rights | Environment approval plus scoped workflow permissions | Avoid giving every workflow the same broad token surface |

## Exception patterns with audit expectations

| Exception type | Pattern | Audit expectation |
| --- | --- | --- |
| Ruleset exception for a subset of repositories | Scoped exception with owner, reason, and review date | Record why the exception exists, where it applies, and when it will be rechecked |
| Temporary environment-bypass or elevated automation access | Time-bounded exception with explicit approver and rollback note | Record who approved it, how long it lasts, and what activity occurred |
| Copilot governance carve-out for a pilot group | Narrow org or repo set with policy note and review point | Record the pilot scope, entitlement reason, and follow-up decision date |
