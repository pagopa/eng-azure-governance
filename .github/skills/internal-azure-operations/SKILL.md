---
name: internal-azure-operations
description: Use when the user needs Azure operational guidance for monitoring, logging, backup and restore, Site Recovery or DR validation, preflight checks, post-rollout validation, reporting, or audit evidence after a structure or governance decision has already been made.
---

# Internal Azure Operations

Use this skill when the next need is to validate, observe, or operationalize an Azure platform decision.

This skill owns the operational side of the platform: monitoring, evidence, preflight, and post-rollout verification. It does not replace strategic framing, structure design, or governance design.

## When to use

- The user needs operational readiness guidance after a design choice.
- The user needs Azure Monitor, Log Analytics, backup, restore, or DR validation guidance.
- The user needs preflight or post-rollout validation patterns.
- The user needs reporting, export, compliance evidence, or operational proof.

## When not to use

- The main problem is still choosing the high-level direction.
- The main problem is management-group, landing-zone, or subscription structure.
- The main problem is RBAC, managed identity, PIM, or Policy design.
- The task is a narrow implementation change with no operational design question.

## Main domains covered

- monitoring and observability posture
- Azure Monitor and Log Analytics evidence paths
- backup and restore expectations
- Site Recovery or DR validation
- preflight checks before rollout
- post-rollout validation
- export and reporting for platform operations
- operational proof that a governance or structure change behaved as expected

## Core rules

- Keep validation proportional to blast radius.
- Treat backup posture and restore evidence as different things.
- Prefer preflight and staged validation before wide rollout when identity, policy, or platform automation could break.
- Keep monitoring, evidence, and reporting tied to the decision that needs confirmation.
- Name what is confirmed, what is inferred, and what still needs a real test.

Load `references/validation-and-evidence.md` when the user needs a deeper checklist for preflight, rollout validation, or DR evidence.

## Use of current facts

Use current Microsoft documentation when the answer depends on current Azure Monitor, Backup, Site Recovery, Policy compliance, or service-behavior details.

## Output expectations

For narrow asks, return:

- recommended validation or evidence path
- short reason
- main operational risk

For broader asks, return:

- operational objective
- preflight checks
- rollout-stage validation path
- post-rollout evidence path
- recovery or DR note when relevant
- open operational risks

## Relationship to adjacent skills

- `internal-azure-strategic`
  Use first when the core decision is still unsettled.
- `internal-azure-organization-structure`
  Use when the operations question is actually about management-group, subscription, or topology placement.
- `internal-azure-governance`
  Use when the operations question is actually about RBAC, managed identity, Policy, or guardrail design rather than validation.
- `awesome-copilot-azure-resource-health-diagnose`
  Use as depth support when the Azure resource is already identified and the next need is deep health diagnosis, log and telemetry analysis, or a remediation plan for that specific resource.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating monitoring as proof that restore or recovery works | Healthy dashboards do not prove recovery viability | Keep monitoring evidence, backup proof, and restore proof as separate lines |
| Skipping preflight for high-blast-radius rollout | Policy, identity, or connectivity failures surface too late | Define rollout unit, preflight checks, rollback trigger, and owner before rollout |
| Reporting only control intent without operational evidence | The platform appears compliant without proof that it works | Record what Azure Monitor, Log Analytics, backup, or compliance signals actually showed |
| Mixing validation advice with new governance design instead of keeping the boundary clear | The operations skill stops being a reliable validation owner | Keep new Policy or RBAC design in `internal-azure-governance` and validate it here |
| Giving a DR answer without making the business criticality assumption visible | Recovery guidance can be overbuilt or incomplete | State the assumed criticality, RTO, or RPO before recommending the validation path |
| Treating one successful rollout wave as proof for all subscriptions or regions | Wider inheritance, network, or residency paths can still fail differently | Validate the first safe unit and widen only after recording real evidence |

## Validation

- Confirm the answer distinguishes confirmed evidence from inferred evidence.
- Confirm preflight checks, rollback trigger, and rollout unit are explicit for risky changes.
- Confirm Azure Monitor or Log Analytics signals are named for the affected surface, not as a generic checklist.
- Confirm backup proof and restore proof are treated as separate validation paths when state exists.
- Confirm DR or continuity notes are included only when business criticality or recovery posture is actually in scope.
