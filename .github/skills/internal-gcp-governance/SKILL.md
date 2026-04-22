---
name: internal-gcp-governance
description: Use when the user needs Google Cloud governance guidance for IAM operating models, workload identity federation, service account boundaries, Org Policy design, inheritance strategy, security guardrails, exception handling, or other controls that define what principals can do after the GCP structure is chosen.
---

# Internal GCP Governance

Use this skill when the next need is to define or review Google Cloud identity, access, and guardrail decisions.

This skill owns governance logic after the broad structure is known. It helps separate org or folder guardrails from project-level grants and keeps permission decisions auditable.

## When to use

- The user needs IAM model guidance across folders or projects.
- The user needs workload identity federation or service account boundary guidance.
- The user needs Org Policy, inheritance, or security-guardrail guidance.
- The user needs a review of guardrail design, exceptions, or access governance.

## When not to use

- The main problem is org, folder, project, or Shared VPC layout.
- The main problem is strategic option framing before the governance surface is clear.
- The main problem is monitoring, reporting, backup, inventory, or post-rollout validation.
- The task is implementation-only.

## Main domains covered

- IAM operating model
- role-binding strategy
- service account boundary design
- workload identity federation
- Org Policy and inheritance strategy
- security guardrails tied to identity and access decisions
- exception handling at governance level

## Core rules

- Keep org or folder guardrails distinct from project-level grants.
- Treat Org Policy as preventive governance, not as permission grants.
- Prefer workload identity federation over long-lived service account keys unless there is a proven reason not to.
- Make scope explicit: org, folder set, or project set.
- Make exception handling explicit when a control is not universal.

Load `references/guardrail-map.md` when the correct governance surface is ambiguous or when the user needs a deeper split between IAM, service accounts, workload identity federation patterns, and Org Policy or CEL-backed guardrail controls.

## Use of current facts

Use current Google Cloud documentation when the answer depends on current IAM semantics, workload identity federation support, Org Policy behavior, or product-specific guardrail limits.

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

- `internal-gcp-strategic`
  Use first when the user still needs option framing or lens selection.
- `internal-gcp-organization-structure`
  Use when the governance question is actually about where a capability should live.
- `internal-gcp-operations`
  Use when the next need is preflight, reporting, validation, inventory, or operational evidence after the governance design is chosen.

## Common mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Treating Org Policy as if it grants access | Preventive governance gets confused with authorization | Pair Org Policy guidance with the IAM path that actually grants access |
| Answering a governance question without naming scope | Org, folder, and project controls behave differently | State the exact governance scope before recommending a mechanism |
| Mixing org-wide guardrails and project-level authorization into one vague recommendation | Reviewers cannot see what prevents versus what grants | Separate Org Policy or inheritance posture from IAM bindings and workload identity design |
| Proposing service account or emergency access without boundaries or audit expectations | Privilege becomes durable and hard to review | Define who can use it, how it is bounded, and what evidence must exist |
| Recommending rollout without staged validation when the blast radius is high | A wide deny or identity failure can interrupt platform operations | Use targeted rollout, explicit rollback, and verification before widening scope |
| Treating workload identity federation as a reason to skip service-account boundary design | Keys may disappear but privilege can still stay too broad | Keep identity mechanism and authorization scope as separate decisions |

## Validation

- Confirm the governance scope is explicit: org, folder set, or project set.
- Confirm the recommended mechanism is clear about whether it prevents, grants, or constrains workload identity.
- Confirm service-account and human-access boundaries are explicit when access crosses project or folder boundaries.
- Confirm staged rollout validation is named before high-blast-radius Org Policy or IAM changes.
- Confirm the answer says when operational proof should move to `internal-gcp-operations`.
