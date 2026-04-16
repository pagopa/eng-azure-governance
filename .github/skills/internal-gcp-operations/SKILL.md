---
name: internal-gcp-operations
description: Use when the user needs Google Cloud operational guidance for monitoring, logging, backup and restore, DR validation, asset inventory, preflight checks, post-rollout validation, reporting, or audit evidence after a structure or governance decision has already been made.
---

# Internal GCP Operations

Use this skill when the next need is to validate, observe, or operationalize a GCP platform decision.

This skill owns the operational side of the platform: monitoring, evidence, inventory, preflight, and post-rollout verification. It does not replace strategic framing, structure design, or governance design.

## When to use

- The user needs operational readiness guidance after a design choice.
- The user needs Cloud Monitoring, Cloud Logging, backup, restore, or DR validation guidance.
- The user needs asset inventory, reporting, or export guidance.
- The user needs preflight or post-rollout validation patterns.

## When not to use

- The main problem is still choosing the high-level direction.
- The main problem is org, folder, project, or Shared VPC structure.
- The main problem is IAM, workload identity, service account, or Org Policy design.
- The task is a narrow implementation change with no operational design question.

## Main domains covered

- monitoring and observability posture
- Cloud Monitoring and Cloud Logging evidence paths
- backup and restore expectations
- DR validation and recovery evidence
- asset inventory and reporting
- preflight checks before rollout
- post-rollout validation
- operational proof that a governance or structure change behaved as expected

## Core rules

- Keep validation proportional to blast radius.
- Treat backup posture and restore evidence as different things.
- Prefer preflight and staged validation before wide rollout when identity, policy, or shared networking could break.
- Keep monitoring, inventory, evidence, and reporting tied to the decision that needs confirmation.
- Name what is confirmed, what is inferred, and what still needs a real test.

Load `references/validation-and-evidence.md` when the user needs a deeper checklist for preflight, rollout validation, asset inventory, or DR evidence.

## Use of current facts

Use current Google Cloud documentation when the answer depends on current Monitoring, Logging, Backup and DR behavior, asset-inventory capability, or service-specific validation details.

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
- recovery, DR, or inventory note when relevant
- open operational risks

## Relationship to adjacent skills

- `internal-gcp-strategic`
  Use first when the core decision is still unsettled.
- `internal-gcp-organization-structure`
  Use when the operations question is actually about org, project, or topology placement.
- `internal-gcp-governance`
  Use when the operations question is actually about IAM, workload identity, Org Policy, or guardrail design rather than validation.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating monitoring as proof that restore or recovery works | Healthy metrics do not prove recovery viability | Keep monitoring evidence, backup proof, and restore proof as separate lines |
| Skipping preflight for high-blast-radius rollout | IAM, Org Policy, or Shared VPC regressions surface too late | Define rollout unit, preflight checks, rollback trigger, and owner before rollout |
| Reporting only control intent without operational evidence | The platform appears compliant without proof that it works | Record what Monitoring, Logging, asset inventory, or recovery exercises actually showed |
| Mixing validation advice with new governance design instead of keeping the boundary clear | The operations skill stops being a reliable validation owner | Keep new Org Policy or IAM design in `internal-gcp-governance` and validate it here |
| Giving a DR answer without making the business criticality assumption visible | Recovery guidance can be overbuilt or incomplete | State the assumed criticality, RTO, or RPO before recommending the evidence path |
| Treating one successful rollout wave as proof for all folders or projects | Wider inheritance or network paths can still fail differently | Validate the first safe unit and widen only after recording real evidence |

## Validation

- Confirm the answer distinguishes confirmed evidence from inferred evidence.
- Confirm preflight checks, rollback trigger, and rollout unit are explicit for risky changes.
- Confirm Monitoring, Logging, and inventory signals are named for the affected surface, not as a generic checklist.
- Confirm backup proof and restore proof are treated as separate validation paths when state exists.
- Confirm DR or continuity notes are included only when business criticality or recovery posture is actually in scope.
