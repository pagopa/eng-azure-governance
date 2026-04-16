# AWS Organization Structure Control Surface Map

Use this reference when turning a structural AWS question into the right control surface.

## Core boundary

- **Management account**: reserve for AWS Organizations control, billing and payer responsibilities, trusted access activation, and only those actions that AWS requires there.
- **Delegated administrator accounts**: prefer for day-to-day operation of integrated AWS services when supported.
- **Member accounts**: keep workload execution, service ownership, and most resource-level IAM decisions here.

## Default review checklist

1. Is this a structure choice, a governance control, or an operations concern?
2. Must the management account perform the action, or can it be delegated?
3. Is the change shaping layout, shaping permissions, or rolling out infrastructure?
4. What is the smallest safe rollout unit: one account, one OU, or one region set?
5. What must be validated before broad rollout?
6. What is the rollback path if access, billing, or platform automation breaks?

## Common structural mappings

| Need | Use first | Notes |
| --- | --- | --- |
| Shape preventive boundaries across many accounts | OU design plus `internal-aws-governance` | Keep the structure and the guardrail choice separate |
| Design a central operating account for an AWS service | Delegated admin placement | Use management account only when AWS requires it |
| Roll out a baseline stack across many accounts | StackSets topology | Keep global-resource blast radius explicit |
| Separate finance oversight from platform execution | payer and management responsibility split | Make the ownership model explicit |
| Place shared services or log collection | account-purpose model | Keep workload accounts separate from platform accounts |

## Important AWS-specific reminders

- SCPs do not affect users or roles in the management account.
- Delegated administrator accounts are still member accounts, so SCPs still apply to them.
- StackSets with service-managed permissions do not deploy stacks into the management account.
- Global IAM or S3 naming collisions matter more in multi-region StackSets than they do in single-account templates.

## Starter account and OU patterns

| Pattern | When it fits | Watch for |
| --- | --- | --- |
| Minimal foundation: management, log archive, security tooling, shared services, workload OUs | Early multi-account platforms that need clear separation without a deep OU tree | Do not overload shared services with workload execution or exception access |
| Environment-oriented workload OUs: `prod`, `nonprod`, plus platform accounts | Teams share a common control posture and rollout cadence by environment | Keep deployment-path differences out of OU names when the real split is risk or residency |
| Business-unit OUs with centralized platform accounts | Large organizations need ownership boundaries first and technical standardization second | Make sure central platform capabilities still have a clear delegated admin model |
| Regulated-segment OU alongside general workloads | A subset of accounts needs stronger residency, logging, or approval controls | Keep the regulated segment justified by requirements, not by vague "special" status |

## Delegated administrator placement heuristics

| Question | Prefer | Reason |
| --- | --- | --- |
| Does AWS support delegated admin for this service? | Delegated administrator account | Reduces management-account usage and tightens day-to-day blast radius |
| Does the service operate as a platform capability across many accounts? | A dedicated platform or security account | Keeps service ownership separate from workload accounts |
| Does the service need close alignment with billing or org control actions? | Management account only when AWS requires it | Avoids making the management account the default operator surface |
| Does the service have strong data-sensitivity or incident-response coupling? | Security or logging account with explicit ownership | Keeps investigation and evidence flows separate from application operations |

## Safe rollout-unit examples

| Structural change | Start with | Widen after |
| --- | --- | --- |
| New delegated admin activation | One non-critical OU or one service-owned account set | Service behavior, logging, and guardrails are confirmed |
| OU realignment for workloads | One workload family with a documented rollback path | SCP impact, automation paths, and billing visibility are validated |
| StackSets baseline rollout | One account in one region or one low-risk OU | Global-resource effects and failure handling are observed |
| Shared-services account introduction | One platform capability with named consumers | Ownership, network reachability, and operational evidence are proven |
