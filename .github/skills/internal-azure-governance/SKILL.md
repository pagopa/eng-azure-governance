---
name: internal-azure-governance
description: Use when the user needs Azure governance guidance for RBAC operating models, managed identity boundaries, PIM or PAM posture, Azure Policy and initiatives, naming and tagging guardrails, exception handling, or other controls that define what principals can do after the Azure structure is chosen.
---

# Internal Azure Governance

Use this skill when the next need is to define or review Azure identity, access, and guardrail decisions.

This skill owns governance logic after the broad structure is known. It helps separate tenant or management-group guardrails from subscription or workload grants and keeps permission decisions auditable.

## When to use

- The user needs RBAC model guidance across management groups or subscriptions.
- The user needs managed identity or privileged-access posture guidance.
- The user needs Azure Policy, initiative, naming, or tagging guardrails.
- The user needs a review of guardrail design, exceptions, or access governance.

## When not to use

- The main problem is management-group, landing-zone, or subscription layout.
- The main problem is strategic option framing before the governance surface is clear.
- The main problem is monitoring, reporting, backup, or post-rollout validation.
- The task is implementation-only.

## Main domains covered

- RBAC operating model
- Entra group and role-assignment strategy
- managed identity boundaries
- PIM and PAM posture
- Azure Policy and initiatives
- naming and tagging guardrails
- security baseline tied to identity and access decisions
- exception handling at governance level

## Core rules

- Keep tenant or management-group guardrails distinct from subscription or resource-level grants.
- Treat Azure Policy as preventive or detective governance, not as permission grants.
- Prefer managed identities and federated workload access over long-lived secrets unless there is a proven reason not to.
- Make scope explicit: management group, subscription set, or single subscription.
- Make exception handling explicit when a control is not universal.

Load `references/guardrail-map.md` when the correct governance surface is ambiguous or when the user needs a deeper split between RBAC, managed identities, PIM/PAM, and Policy controls.

## Use of current facts

Use current Microsoft documentation when the answer depends on current Azure RBAC semantics, managed identity support, Policy effects, or privileged-access behavior.

## Output expectations

For narrow asks, return:

- recommended governance mechanism
- short reason
- main risk or validation note

For broader asks, return:

- governance objective
- scope
- candidate mechanisms
- recommended control stack
- exception or blast-radius note
- what should be validated before rollout

## Relationship to adjacent skills

- `internal-azure-strategic`
  Use first when the user still needs option framing or lens selection.
- `internal-azure-organization-structure`
  Use when the governance question is actually about where a capability should live.
- `internal-azure-operations`
  Use when the next need is preflight, reporting, validation, or operational evidence after the governance design is chosen.
- `awesome-copilot-azure-role-selector`
  Use as depth support when the governance boundary is already clear and the next need is least-privilege role selection, custom-role fallback, or assignment artifacts such as CLI commands and Bicep snippets.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating Azure Policy as if it grants access | Preventive controls get confused with authorization paths | Pair Policy guidance with the RBAC or identity model that actually grants access |
| Answering a governance question without naming scope | Management-group, subscription, and resource scopes behave differently | State the exact scope before recommending a mechanism |
| Mixing tenant-wide guardrails and subscription-level authorization into one vague recommendation | Reviewers cannot see what prevents versus what grants | Separate Policy or PIM posture from RBAC assignments and workload identity design |
| Proposing emergency access without boundaries, audit expectations, or privileged-access posture | Break-glass becomes a standing exception instead of controlled elevation | Define who can elevate, how long it lasts, and what evidence must exist |
| Recommending rollout without staged validation when the blast radius is high | Wide RBAC or Policy errors can block operations quickly | Use scoped rollout, compliance checks, and explicit rollback triggers |
| Treating managed identities as a reason to skip scope design | Identity becomes secretless but still over-privileged | Keep identity type and authorization scope as separate decisions |

## Validation

- Confirm the governance scope is explicit: management group, subscription set, or single subscription.
- Confirm the recommended mechanism is clear about whether it prevents, grants, or constrains privileged access.
- Confirm identity boundaries and exception paths are explicit for human and workload access.
- Confirm staged rollout validation is named before high-blast-radius Policy, RBAC, or PIM changes.
- Confirm the answer says when operational proof should move to `internal-azure-operations` and when least-privilege role depth should move to `awesome-copilot-azure-role-selector`.
