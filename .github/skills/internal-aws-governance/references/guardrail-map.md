# AWS Governance Guardrail Map

Use this reference when the user needs a clearer split between AWS governance surfaces.

## Quick split

| Need | Use first | Why |
| --- | --- | --- |
| Limit what principals can ever do across many accounts | SCP | Org-level preventive guardrail |
| Define what a role or workload can do in one account | IAM policy plus trust policy | Execution-level authorization |
| Constrain delegated builders or automation | Permission boundary or session policy | Limits delegated execution |
| Standardize metadata expectations | Tag policy plus local enforcement | Governance consistency |
| Permit emergency access | Break-glass role design plus audit path | Exceptional access with visibility |

## Review questions

1. Is this question about where a control lives or what a principal may do?
2. Is the mechanism preventing permission, granting permission, or constraining delegated permission?
3. Is the scope root, OU, account set, or single account?
4. What exception path is required, if any?
5. What should be simulated before rollout?

## Reminder

- Structure chooses placement.
- Governance chooses permissions and guardrails.
- Operations verifies that the chosen governance behaves as intended after rollout.

## Placement patterns

| Scenario | Prefer | Why |
| --- | --- | --- |
| Block risky services or regions across many accounts | SCP at root or OU | Central preventive control with explicit blast radius |
| Allow a workload role to use only the resources in one account | IAM policy plus trust policy | Grants the action at the execution boundary |
| Let platform engineers create roles without giving them unrestricted permissions | Permission boundary plus scoped creation role | Limits delegated builders without replacing trust design |
| Standardize required tags for cost or ownership workflows | Tag policy plus enforcement in deployment paths | Keeps metadata expectations central but still operationally enforceable |

## Trust-boundary examples

| Need | Primary control | Review note |
| --- | --- | --- |
| Human access from an external IdP into AWS accounts | Federation plus tightly scoped assume-role paths | Keep identity-source trust separate from account authorization |
| CI or automation assuming deployment roles across accounts | Trust policy constrained to named principals and conditions | Make environment scope and break-glass path explicit |
| Shared security tooling reading logs across accounts | Resource policy or role assumption with read-only scope | Prefer narrow data-access roles over broad admin trust |

## Exception patterns with audit expectations

| Exception type | Pattern | Audit expectation |
| --- | --- | --- |
| Temporary break-glass for incident response | Time-bounded role path with explicit approver and logging | Record who approved, who assumed the role, and when access ended |
| Service team needs an OU-level SCP carve-out | Targeted OU or account exception with expiry review | Record the business reason, compensating controls, and review date |
| Automation cannot yet satisfy a required tag or policy condition | Narrow deployment exception with compensating report | Track affected accounts or resources and the closure plan |
