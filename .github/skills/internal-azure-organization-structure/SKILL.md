---
name: internal-azure-organization-structure
description: Use when the user needs Azure control-plane or platform-structure guidance for tenant hierarchy, management groups, subscription models, landing-zone placement, environment segmentation, platform-level network topology, or other layout decisions that shape how Azure is organized before implementation.
---

# Internal Azure Organization Structure

Use this skill when the next need is to design or review how Azure is structured at tenant and platform level.

This skill owns Azure layout decisions, not generic strategy and not detailed RBAC or monitoring implementation. It helps translate a platform goal into management-group, subscription, landing-zone, topology, and rollout structure.

## When to use

- The user is shaping or reviewing Azure tenant hierarchy.
- The user needs management-group or subscription-model guidance.
- The user is deciding landing-zone placement or environment segmentation.
- The user needs platform-level network or regional structure guidance.
- The user needs rollout-scope guidance for structural Azure change.

## When not to use

- The question is mainly RBAC, PIM, managed identities, or Policy logic.
- The task is mainly monitoring, backup, reporting, or post-rollout validation.
- The user only needs generic strategic comparison with no concrete structure question.
- The task is already implementation-focused.

## Main domains covered

- tenant hierarchy
- management-group layout
- subscription model and subscription purpose
- landing-zone placement
- environment segmentation
- platform-level network topology
- regional structure and residency placement when relevant
- rollout unit and blast radius for structural change

## Working model

- Keep tenant-level hierarchy decisions separate from subscription-level governance decisions.
- Separate structure decisions from governance decisions:
  - structure decides where capabilities live
  - governance decides what controls and permissions apply
- Keep platform subscriptions separate from workload subscriptions when the operating model needs it.
- Name the smallest safe rollout unit for structural change: management group, subscription set, or region set.

## Research and current facts

Use current Microsoft documentation when the answer depends on current landing-zone guidance, management-group behavior, subscription constraints, Azure networking capabilities, or region-sensitive platform limits.

Load `references/topology-map.md` when the structure choice is ambiguous or when the user needs a deeper control-surface split.

## Output expectations

Keep outputs proportional to the question.

For narrow asks, return:

- recommended structure choice
- short reason
- main blast-radius or rollout note

For broader asks, return:

- structural objective
- candidate layouts
- recommended placement model
- smallest safe rollout unit
- main risks
- what should move next to `internal-azure-governance` or `internal-azure-operations`

## Relationship to adjacent skills

- `internal-azure-strategic`
  Use first when the user still needs broader decision framing or lens selection.
- `internal-azure-governance`
  Use when the structural decision is accepted and the next need is RBAC, managed identity, PIM/PAM, Policy, or guardrail definition.
- `internal-azure-operations`
  Use when the structure is accepted and the next need is validation, monitoring, backup, or operational evidence.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Proposing hierarchy or subscription layouts without a rollout scope | Tenant and hierarchy changes are hard to unwind if staged poorly | Name the smallest safe rollout unit: management group, subscription set, or region set |
| Mixing landing-zone placement and RBAC design into one vague answer | Structure and governance review get blurred together | Keep placement here and move authorization or guardrails to `internal-azure-governance` |
| Treating network topology as an operations concern instead of a structure concern | Connectivity design decisions get delayed until after layout is fixed | Keep hub-spoke, Virtual WAN, and regional topology in the structure lane |
| Using structure answers to sneak in Policy or RBAC design without separating the concerns | The ownership boundary becomes unreliable | State where the capability lives and hand off what controls or permissions apply |
| Ignoring region or residency implications when they materially shape layout | Subscription or landing-zone placement can violate real requirements | Make sovereignty, region pairing, and continuity assumptions explicit |
| Recommending platform subscriptions without naming their operating purpose | Platform estates become catch-all containers with unclear ownership | State whether the subscription is for connectivity, identity, management, or shared services |

## Validation

- Confirm the placement model is explicit: management group, subscription family, landing zone, or platform topology.
- Confirm the smallest safe rollout unit is named and matches the proposed structural change.
- Confirm region or residency implications are explicit when they shape hierarchy, subscription, or topology choices.
- Confirm platform ownership and workload ownership are separated when both appear in the recommendation.
- Confirm the next handoff is clear when the user now needs governance controls or operational proof.
