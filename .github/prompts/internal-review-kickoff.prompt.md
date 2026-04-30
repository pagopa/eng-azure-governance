---
name: "internal-review-kickoff"
agent: "agent"
description: "Kick off a defect-first review for governance, workflow, or repository-owned catalog changes"
---

<!-- markdownlint-disable-file MD041 -->

Change, diff, or asset to review:
${input:subject:Describe the PR, diff, file set, or asset under review}

Focus area:
${input:focus:Optional focus such as security, regressions, routing, or validation}

Known assumptions or concerns:
${input:concerns:List any risks, assumptions, or reviewer comments already in play}

Use these repository sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-code-review-instructions.md](../copilot-code-review-instructions.md)
- [.github/skills/internal-code-review/SKILL.md](../skills/internal-code-review/SKILL.md)
- [.github/agents/internal-review-guard.agent.md](../agents/internal-review-guard.agent.md)

Produce review findings with:

1. Severity and confidence on every finding
2. Evidence gaps
3. Self-questioning notes for the most severe finding
4. Residual risks if no further changes are made
5. Recommended owner if the task is no longer review-owned
