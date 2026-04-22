---
description: Repository-owned Copilot agent authoring guardrails for boundary clarity, paired-asset coherence, and minimal duplication.
applyTo: ".github/agents/internal-*.agent.md,.github/agents/local-*.agent.md"
---

# Copilot Agent Authoring Instructions

## Workflow

- Load `internal-agent-development` before planning or editing a repository-owned agent, or before redefining the boundary between an agent, skill, prompt, and instruction.
- When the agent depends on a paired skill or local references, inspect those assets before finalizing and fix only the necessary drift in the same change.

## Cohesion

- Keep route, boundary, tool contract, and output expectations in the agent.
- Keep reusable procedure in paired skills and deep reusable detail in references.
- If a paired skill or reference owns the detailed contract, keep the agent summary-level and remove re-listed subtopics.
- Use `## Mandatory Engine Skills` only for required engines and `## Optional Support Skills` only for conditional helpers.
- Use `## Skill Usage Contract` only when declared support skills are genuinely conditional.
- Treat `## Preferred/Optional Skills` as legacy and do not introduce it in repository-owned agents.

## Validation

- Re-check frontmatter alignment, declared skills, and paired-bundle drift before finishing.
- Run the closest existing catalog validation that covers the touched agent.
