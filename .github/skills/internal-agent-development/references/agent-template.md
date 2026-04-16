# Internal Agent Templates

Use the smallest template that matches the job. Keep the body concise and move reusable procedures into skills.

## 1. Specialist Agent

Use this when the agent owns one clear specialist role.

```markdown
---
name: internal-example
description: Use this agent when the repository needs ...
---

# Internal Example


## Routing Rules

- Use this agent when ...
- Do not use this agent when ...
- Prefer `internal-other-agent` when ...

## Output Expectations

- Objective or scope
- Main risks or tradeoffs
- Recommended next action
```

## 2. Command-Center Agent

Use this when the agent governs a broader recurring workflow and its declared skills are conditional.

```markdown
---
name: internal-example-control-center
description: Use this agent when the repository needs ...
---

# Internal Example Control Center

## Role

## Core Rules

- Keep ...
- Do not ...
- Treat ... as canonical

## Skill Usage Contract

- `internal-skill-a`: Use when ...
- `internal-skill-b`: Use when ...

## Routing Rules

- Use this agent when ...
- Do not use this agent when ...
- If this command center no longer fits, tell the user and recommend `internal-other-agent` instead of routing automatically.

## Execution Workflow

1. Inspect ...
2. Decide ...
3. Apply ...
4. Validate ...

## Output Expectations

- Objective or decision
- Key findings or risks
- Change or recommendation
- Validation status
```

## 3. Coordinator Agent

Use this when the agent delegates subtasks to specialized subagents.

```markdown
---
name: internal-example-coordinator
description: Use this agent when the task requires coordinated multi-step work across specialized workers.
tools: ['agent', 'read', 'search', 'edit']
agents: ['internal-worker-a', 'internal-worker-b']
---

# Internal Example Coordinator

## Role

You coordinate multi-step work by delegating to specialized workers.

## Core Rules

- Delegate subtasks to the listed worker agents.
- Do not perform worker-level work directly.
- Synthesize results from workers into a unified response.

## Routing Rules

- Use this agent when the task spans multiple specialist domains.
- Do not use this agent when the task fits a single specialist.

## Output Expectations

- Summary of delegated subtasks and their results
- Synthesized findings or deliverable
- Any unresolved issues or recommended follow-ups
```

## 4. Subagent-Only Worker

Use this when the agent should only be invoked by a coordinator, not directly by users.

```markdown
---
name: internal-example-worker
description: Specialized worker for domain-specific subtasks.
user-invocable: false
tools: ['read', 'search']
---

# Internal Example Worker

Focused instructions for the worker's domain.
```

## Notes

- `## Skill Usage Contract` is optional. Add it only when the agent owns conditional use of multiple declared skills.
- `## Core Rules` is optional. Add it when the agent governs policy, scope, or sync behavior.
- Repository-owned internal agents should declare `tools:` explicitly. Prefer canonical aliases such as `read`, `edit`, `search`, `execute`, `agent`, and `web`.
- Keep `tools:` short and role-shaped instead of copying long product-specific tool catalogs.
- When an agent dispatches to specific subagents, declare `agents:` with the explicit target list. When an agent must not dispatch, use `agents: []`.
- Use `user-invocable: false` for agents that should only be accessible as subagents.
- If you can remove a section without losing routing clarity, remove it.
- `description:` should describe selection conditions, not prestige or generic expertise.
