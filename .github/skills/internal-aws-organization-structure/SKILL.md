---
name: internal-aws-organization-structure
description: Use when the user needs AWS control-plane or multi-account structure guidance for Organizations, OUs, account models, delegated administrator placement, StackSets topology, network topology at platform level, or other organization-shaping decisions that affect how AWS is laid out before implementation.
---

# Internal AWS Organization Structure

Use this skill when the next need is to design or review how AWS is structured at organization and platform level.

This skill owns AWS layout decisions, not generic strategy and not detailed IAM or monitoring implementation. It helps translate a platform goal into account, OU, delegated admin, network, and rollout structure.

## When to use

- The user is shaping or reviewing AWS Organizations layout.
- The user needs account, OU, or payer-management separation guidance.
- The user is deciding delegated administrator placement.
- The user needs StackSets topology or rollout-scope guidance.
- The user needs network placement or multi-region layout at platform level.

## When not to use

- The question is mainly IAM, SCP, federation, or guardrail logic.
- The task is mainly monitoring, backup, reporting, or post-rollout validation.
- The user only needs generic strategic comparison with no concrete structure question.
- The task is already implementation-focused.

## Main domains covered

- AWS Organizations hierarchy
- OU design and safe rollout scope
- management account versus payer responsibilities
- account segmentation and account purpose
- shared services, security, and log archive account layout
- delegated administrator placement
- StackSets topology and blast radius at structure level
- platform-level network topology
- multi-account and multi-region structural decisions

## Working model

- Keep the management account minimal unless AWS explicitly requires otherwise.
- Distinguish financial ownership from operational ownership.
- Prefer delegated administration when it materially reduces blast radius.
- Separate structure decisions from governance decisions:
  - structure decides where capabilities live
  - governance decides what controls and permissions apply
- Name the smallest safe rollout unit for structural change: account, OU, or region set.

## Research and current facts

Use `internal-aws-mcp-research` when the answer depends on current AWS service support, delegated admin capabilities, StackSets behavior, or region-sensitive platform constraints.

Load `references/control-surface-map.md` for the control-surface split and default review checklist when the structure choice is ambiguous.

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
- what should move next to `internal-aws-governance` or `internal-aws-operations`

## Relationship to adjacent skills

- `internal-aws-strategic`
  Use first when the user still needs a broader decision framing or lens selection.
- `internal-aws-governance`
  Use when the structural decision is accepted and the next need is IAM, SCP, trust, federation, or guardrail definition.
- `internal-aws-operations`
  Use when the structure is accepted and the next need is validation, monitoring, backup, or operational evidence.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating the management account as the default operating account | It increases blast radius and weakens separation of duties | Keep the management account minimal and prefer delegated administrator accounts when AWS supports them |
| Mixing payer responsibility with day-to-day operational ownership without making the reason explicit | Finance and platform controls drift together and are harder to change safely | State the financial owner and the operational owner separately |
| Proposing OU or account layouts without a rollout scope | Structural changes become hard to stage or roll back | Name the smallest safe rollout unit: account, OU, or region set |
| Hiding global-resource or cross-region blast radius in StackSets discussions | Failures spread further than the rollout plan suggests | Make regional scope, global resources, and rollback boundaries explicit |
| Using structure answers to sneak in IAM or SCP design without separating the concerns | The lane boundary blurs and review gets weaker | Keep placement decisions in this skill and hand guardrail logic to `internal-aws-governance` |
| Recommending shared services placement without naming service ownership | Central accounts become generic dumping grounds | State which platform capability lives centrally and which workload teams still own their execution accounts |

## Validation

- Confirm the placement model is explicit: management account, delegated administrator, shared-services account, or member account.
- Confirm the smallest safe rollout unit is named and matches the proposed structural change.
- Confirm blast radius is explicit for OU moves, delegated admin changes, StackSets rollout, or regional topology shifts.
- Confirm financial ownership and operational ownership are separated when both appear in the answer.
- Confirm the next handoff is clear when the user now needs guardrails or operational validation.
