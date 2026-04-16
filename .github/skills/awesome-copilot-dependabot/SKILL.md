---
name: awesome-copilot-dependabot
description: Design and optimize `.github/dependabot.yml` with grouped updates, monorepo coverage, scheduling, ignore rules, and security-update strategy. Use when configuring Dependabot, reducing PR noise, or aligning dependency-update policy with GitHub Advanced Security.
---

# Dependabot

Use this skill when the task is about Dependabot configuration or update policy.

## Primary Scenarios

- Create or review `.github/dependabot.yml`
- Model monorepo directory coverage
- Group updates to reduce PR noise
- Separate version updates from security updates
- Tune labels, schedules, ignore rules, and registry settings

## Workflow

1. Detect ecosystems and manifest locations.
2. Decide whether each ecosystem needs its own cadence.
3. Use grouping deliberately to control PR volume.
4. Keep security updates enabled even if version updates are limited.
5. Review ignore rules as risk tradeoffs, not convenience defaults.

## Guardrails

- There is one canonical `dependabot.yml`; do not fragment it.
- Use `directories` when globbing is required.
- Avoid massive grouped PRs that hide risky upgrades.
- Do not disable version updates without explicitly preserving security updates.

## Output Expectations

- A clean configuration shape
- Rationale for grouping and cadence
- Monorepo handling notes
- Any risk introduced by ignore or cooldown rules
