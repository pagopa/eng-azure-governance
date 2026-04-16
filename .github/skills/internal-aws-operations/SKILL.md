---
name: internal-aws-operations
description: Use when the user needs AWS operational guidance for monitoring, logging, backup and restore, DR validation, preflight checks, post-rollout validation, reporting, or audit evidence after a structure or governance decision has already been made.
---

# Internal AWS Operations

Use this skill when the next need is to validate, observe, or operationalize an AWS platform decision.

This skill owns the operational side of the platform: monitoring, evidence, preflight, and post-rollout verification. It does not replace strategic framing, structure design, or governance design.

## When to use

- The user needs operational readiness guidance after a design choice.
- The user needs monitoring, logging, backup, restore, or DR validation guidance.
- The user needs preflight or post-rollout validation patterns.
- The user needs reporting, export, or audit-evidence guidance.

## When not to use

- The main problem is still choosing the high-level direction.
- The main problem is account, OU, or delegated admin structure.
- The main problem is IAM, SCP, or trust-policy design.
- The task is a narrow implementation change with no operational design question.

## Main domains covered

- monitoring and observability posture
- CloudTrail, Config, and audit evidence
- backup and restore expectations
- DR validation and recovery evidence
- preflight checks before rollout
- post-rollout validation
- export and reporting for platform operations
- operational proof that a governance or structure change behaved as expected

## Core rules

- Keep validation proportional to blast radius.
- Treat backup posture and restore evidence as different things.
- Prefer preflight and staged validation before wide rollout when access or platform automation could break.
- Keep monitoring, evidence, and reporting tied to the decision that needs confirmation.
- Name what is confirmed, what is inferred, and what still needs a real test.

Load `references/validation-and-evidence.md` when the user needs a deeper checklist for preflight, rollout validation, or DR evidence.

## Use of current facts

Use `internal-aws-mcp-research` when the answer depends on current AWS service behavior, current documentation, or safe inspection of real IAM state before rollout.

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

- `internal-aws-strategic`
  Use first when the core decision is still unsettled.
- `internal-aws-organization-structure`
  Use when the operations question is actually about account, OU, or topology placement.
- `internal-aws-governance`
  Use when the operations question is actually about IAM, SCP, trust, or guardrail design rather than validation.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating monitoring as proof that restore or recovery works | Healthy telemetry does not prove recovery viability | Keep backup posture, restore proof, and DR validation as separate evidence lines |
| Skipping preflight for high-blast-radius rollout | Access, logging, or automation regressions are discovered too late | Define preflight checks, rollback trigger, and owner before rollout starts |
| Reporting only control intent without operational evidence | The platform looks compliant on paper but not in practice | Record what was observed in CloudTrail, Config, logs, or recovery tests |
| Mixing validation advice with new governance design instead of keeping the boundary clear | The answer stops being a reliable operations owner | Keep new guardrail design in `internal-aws-governance` and validate the chosen design here |
| Giving a DR answer without making the business criticality assumption visible | Recovery effort may be overbuilt or underbuilt | State the assumed RTO, RPO, or criticality before recommending the evidence path |
| Treating one successful rollout wave as proof for all scopes | Wider OUs, regions, or accounts can still fail differently | Widen only after the first safe unit is validated and recorded |

## Validation

- Confirm the answer distinguishes confirmed evidence from inferred evidence.
- Confirm preflight checks, rollback trigger, and rollout unit are explicit for risky changes.
- Confirm backup proof and restore proof are treated as separate validation paths when state exists.
- Confirm the main operational signals are named for the affected surface, not as a generic checklist.
- Confirm DR or continuity notes are included only when business criticality or recovery posture is actually in scope.
