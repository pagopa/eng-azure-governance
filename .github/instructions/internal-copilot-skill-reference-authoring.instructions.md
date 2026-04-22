---
description: Repository-owned skill reference guardrails for deep reusable detail without duplicating paired agent or SKILL.md contracts.
applyTo: ".github/skills/internal-*/references/**/*.md,.github/skills/local-*/references/**/*.md"
---

# Copilot Skill Reference Authoring Instructions

## Workflow

- Use references as the deep owner for reusable tables, templates, and detailed checklists.
- When a reference change rewrites the paired bundle boundary, load `internal-skill-creator` and `internal-agent-development` as needed instead of inventing a parallel split.
- When editing a deep reference, inspect the paired `SKILL.md` and any paired agent before finalizing and fix only the necessary drift in the same change.

## Cohesion

- Keep route and boundary language in the paired agent.
- Keep reusable workflow, anti-scope, and validation posture in `SKILL.md`.
- Use references as the deep owner for reusable tables, templates, and detailed checklists.
- Do not copy the same deep material back into `SKILL.md` or the paired agent.
- If a reference becomes the canonical detail owner, trim matching duplication from the paired bundle in the same change.

## Validation

- Re-check local links and paired-bundle drift before finishing.
- Run the closest existing skill or catalog validation that covers the touched bundle.
