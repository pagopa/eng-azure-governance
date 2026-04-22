# Subagent and Orchestration Patterns

Use this file when the agent being authored needs to invoke or be invoked as a subagent, or when designing coordinator/worker workflows.

## Frontmatter Properties for Subagent Control

| Property | Default | Effect |
| --- | --- | --- |
| `agents` | `*` (all) | List of agent names allowed as subagents. Use `[]` to block all subagent use. |
| `user-invocable` | `true` | Set to `false` to hide from the agents dropdown; the agent can still be invoked as a subagent. |
| `disable-model-invocation` | `false` | Set to `true` to prevent the agent from being invoked as a subagent by other agents. |
| `handoffs` | none | Guided sequential workflow buttons that appear after a response completes. |

Key rules:

- Explicitly listing an agent in `agents:` overrides `disable-model-invocation: true` on that target.
- If `agents:` is present, `agent` must be in the `tools:` list.
- `handoffs` and `argument-hint` are VS Code only; GitHub.com ignores them.
- `infer:` is retired. Use `user-invocable` and `disable-model-invocation` instead.
- Context isolation does not mean a subagent starts from zero configuration. By default, a subagent inherits the main session agent, model, and tools; when the subagent is a custom agent, its own configuration overrides those inherited defaults.

## Coordinator and Worker Pattern

A coordinator agent manages the overall task and delegates subtasks to specialized worker agents.

```markdown
---
name: internal-example-coordinator
description: Use this agent when the task requires coordinated multi-step work across specialized workers.
tools: ['agent', 'read', 'search', 'edit']
agents: ['internal-worker-a', 'internal-worker-b', 'internal-worker-c']
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

Worker agents should be hidden from the dropdown and have narrow tool access:

```markdown
---
name: internal-worker-a
description: Specialized worker for domain A tasks.
user-invocable: false
tools: ['read', 'search']
---

Focused instructions for domain A work.
```

## Restricting Subagent Access

### Router with explicit dispatch targets

```yaml
agents: ['internal-delivery-operator', 'internal-planning-leader', 'internal-review-guard', 'internal-critical-master']
```

Only these four agents can be invoked as subagents. The platform enforces this.

### Non-router agents that must not dispatch

```yaml
agents: []
```

This makes the "recommendation-only" boundary a platform-enforced fact, not just prose.

### Rare one-way exception between direct owners

```yaml
agents: ['internal-target-owner']
```

Use this only when all of these are true:

- the exception is explicit, narrow, and one-directional
- ownership remains readable and auditably bounded
- the called owner does not re-route or call back
- the workflow does not create an all-to-all mesh or nested ping-pong
- a user-visible handoff would add more friction than the single bounded exception

Do not use this pattern as a default operational mesh.

### Subagent-only agents

```yaml
user-invocable: false
```

The agent does not appear in the dropdown but can be invoked by any coordinator that lists it in `agents:`.

## Handoff Pattern

Handoffs create guided sequential workflows with user-visible buttons between agent transitions.

```yaml
handoffs:
  - label: Start Implementation
    agent: internal-delivery-operator
    prompt: Implement the plan outlined above.
    send: false
```

When `send: false` (default), the user sees the button and decides whether to proceed. When `send: true`, the prompt submits automatically.

Use handoffs when:

- The workflow has clear sequential phases (plan → implement → review).
- The user should review and approve each transition.
- Context from the previous phase must carry forward.

Do not use handoffs when:

- The delegation should happen autonomously within one turn (use `agents:` + coordinator pattern instead).
- The workflow is GitHub.com only (`handoffs` is VS Code specific).

## Nested Subagents

Disabled by default. Enable with `chat.subagents.allowInvocationsFromSubagents` setting.

- Maximum nesting depth: 5 levels.
- Use for divide-and-conquer patterns where a subagent delegates further.
- A recursive agent lists itself in its own `agents:` property.

Avoid nested subagents unless the task genuinely benefits from recursive delegation. Most repository workflows need at most one level of delegation.

## Anti-Patterns

- Coordinator that performs worker-level work instead of delegating.
- `agents: *` on a router when only four canonical targets exist.
- Worker agents with `user-invocable: true` that clutter the dropdown.
- Using `handoffs` for autonomous delegation that should be a subagent call.
- Nested subagents enabled globally when only one agent needs recursion.
- Missing `agent` in `tools:` when `agents:` is declared.

## Official Documentation

- VS Code subagents: `https://code.visualstudio.com/docs/copilot/agents/subagents`
- VS Code custom agents: `https://code.visualstudio.com/docs/copilot/customization/custom-agents`
- GitHub.com configuration reference: `https://docs.github.com/en/copilot/reference/custom-agents-configuration`
