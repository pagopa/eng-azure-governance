---
name: "internal-pre-mortem"
agent: "agent"
description: "Pressure-test a proposal before merge, refactor, or cross-boundary implementation"
---

<!-- markdownlint-disable-file MD041 -->

Proposal or decision under test:
${input:proposal:Describe the proposal, plan, or change you want challenged}

Scope and blast radius:
${input:scope:List the files, repos, systems, or teams affected}

Assumptions to challenge:
${input:assumptions:List the assumptions you want stress-tested}

Constraints or non-negotiables:
${input:constraints:List technical, policy, or rollout constraints}

Use these repository sources first:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/agents/internal-critical-master.agent.md](../agents/internal-critical-master.agent.md)
- [.github/skills/internal-agent-cross-lane-engine/SKILL.md](../skills/internal-agent-cross-lane-engine/SKILL.md)

Return a compact pre-mortem with:

1. Proposal or decision under test
2. Assumptions under test
3. Top failure modes
4. Counter-framing or inversion result
5. Keep, change, or reframe recommendation
6. Residual risk if the proposal still goes ahead
