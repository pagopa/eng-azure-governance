---
name: internal-github-operations
description: Use when the user needs GitHub operational guidance for Actions health, runner operations, audit logs, reporting and export, drift checks, preflight checks, post-rollout validation, or operational evidence after a governance or operating-model decision has already been made.
---

# Internal GitHub Operations

Use this skill when the next need is to validate, observe, or operationalize a GitHub platform decision.

This skill owns the operational side of the platform: workflow health, runner evidence, preflight, and post-rollout verification. It does not replace strategic framing or governance design.

## When to use

- The user needs operational readiness guidance after a design choice.
- The user needs Actions health, runner operations, or audit-log guidance.
- The user needs preflight, post-rollout validation, reporting, or export patterns.
- The user needs drift checks or operational proof that a change behaved as expected.

## When not to use

- The main problem is still choosing the high-level direction.
- The main problem is repo-model, Apps strategy, or governance design.
- The task is a narrow implementation change with no operational design question.

## Main domains covered

- Actions health and workflow evidence
- runner operations and runner-fleet checks
- audit-log review and export
- reporting and drift checks
- preflight checks before rollout
- post-rollout validation
- operational proof that a governance or operating-model change behaved as expected

## Core rules

- Keep validation proportional to blast radius.
- Treat workflow success and runner health as different signals.
- Prefer preflight and staged validation before wide rollout when permissions, runners, or release automation could break.
- Keep audit, evidence, and reporting tied to the decision that needs confirmation.
- Name what is confirmed, what is inferred, and what still needs a real test.

Load `references/validation-and-evidence.md` when the user needs a deeper checklist for preflight, rollout validation, runner evidence, or audit proof.

## Use of current facts

Use current GitHub documentation when the answer depends on current Actions behavior, runner support, audit-log capability, reporting exports, or platform-specific validation details.

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
- runner, audit, or continuity note when relevant
- open operational risks

## Relationship to adjacent skills

- `internal-github-strategic`
  Use first when the core decision is still unsettled.
- `internal-github-governance`
  Use when the operations question is actually about rulesets, permissions, OIDC, secret posture, or guardrail design rather than validation.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating workflow success as proof that permissions or guardrails are correct | A single green run can hide excessive privilege or missing failure paths | Check expected permission boundaries, audit trails, and negative cases as separate signals |
| Skipping preflight for high-blast-radius rollout | Ruleset, token, runner, or environment regressions surface too late | Define rollout unit, preflight checks, rollback trigger, and owner before rollout |
| Reporting only intended policy without operational evidence | Governance looks correct on paper without proof that delivery still works | Record what workflows, runners, and audit surfaces actually showed |
| Mixing validation advice with new governance design instead of keeping the boundary clear | The operations skill stops being a reliable validation owner | Keep new guardrail design in `internal-github-governance` and validate it here |
| Giving a continuity answer without making the build or release criticality assumption visible | Continuity guidance can be overbuilt or incomplete | State the assumed pipeline or release criticality before recommending the evidence path |
| Treating one successful rollout wave as proof for all repositories or environments | Wider repo sets or runner groups can still fail differently | Validate the first safe unit and widen only after recording real evidence |

## Validation

- Confirm the answer distinguishes confirmed evidence from inferred evidence.
- Confirm preflight checks, rollback trigger, and rollout unit are explicit for risky changes.
- Confirm workflow, runner, and audit signals are named for the affected surface, not as a generic checklist.
- Confirm permission proof and operational proof are treated as separate validation paths.
- Confirm continuity notes are included only when build, release, or repository criticality is actually in scope.
