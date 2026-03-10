---
description: Create or modify a cloud governance policy (AWS SCP, Azure Policy, GCP Org Policy)
name: TechAICloudPolicy
agent: agent
argument-hint: action=<create|modify> cloud=<aws|azure|gcp> policy_name=<name> purpose=<purpose> [effect=<deny|audit|modify|append|disabled>]
---

# Cloud Governance Policy Task

## Required inputs
- **Action**: ${input:action:create,modify}
- **Cloud**: ${input:cloud:aws,azure,gcp}
- **Policy name**: ${input:policy_name}
- **Purpose**: ${input:purpose}
- **Effect (optional)**: ${input:effect:deny,audit,modify,append,disabled}

## Instructions
1. Use `.github/skills/tech-ai-cloud-policy/SKILL.md`.
2. Reuse existing policy patterns in the target repository.
3. Keep policy logic explicit (scope, conditions, effect).
4. Preserve naming and folder conventions.
5. Keep technical text in English.
6. If `action=modify`, preserve existing behavior unless explicitly changed.

## Minimal example
- Input: `action=create cloud=azure policy_name=deny_public_ip purpose="Block public IPs" effect=deny`
- Expected output:
  - A new policy definition in the repository standard location.
  - Clear `if` conditions and `then.effect = "deny"`.
  - Matching non-README docs update in English if behavior is new.
- Cloud hints:
  - AWS: generate SCP JSON with explicit `Action`/`Resource`/`Condition`.
  - GCP: generate `google_org_policy_policy` with explicit `parent` scope and enforce rule.

## Validation
- Validate syntax for the target cloud policy format.
- Test in non-production first.
- Update non-README docs in English when behavior changes.
