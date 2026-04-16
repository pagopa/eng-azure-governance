# Azure Strategic Lens Playbook

Use this reference when the user wants more depth than the base skill should load by default.

## Common lens combinations

| Situation | Start with | Add only if needed |
| --- | --- | --- |
| Landing-zone or platform-topology choice | organization-structure, governance | FinOps, BC/DR |
| Identity or delegated access choice | identity and access, governance | blast radius, compliance |
| Rollout planning across management groups or subscriptions | rollout and rollback, blast radius | operations, BC/DR |
| Cost-sensitive platform decision | FinOps, maintainability | operations, governance |
| Resilience-sensitive design | BC/DR, operations | FinOps, blast radius |

## Signals that another lens should be suggested

- Cost could materially change the recommended option: suggest `FinOps`
- The decision changes management groups, subscriptions, or connectivity layout: suggest `organization-structure`
- The choice changes RBAC, managed identity, or Policy behavior: suggest `governance`
- The rollout adds monitoring, backup, or validation burden: suggest `operations`
- A failure would interrupt critical platform capability: suggest `BC/DR`

## Depth control

- Stay in `Quick answer` mode when one option is clearly better and the user asked a narrow question.
- Upgrade to `Decision note` when at least two viable options exist.
- Upgrade to `Deep analysis` only when the user asks for it or the risk profile justifies it.
