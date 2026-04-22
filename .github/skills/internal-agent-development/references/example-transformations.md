# Example Transformations

Use these examples as patterns, not boilerplate.

They show how to convert richer external agent ideas into repository-owned internal agents that fit the local contract.

## Example 1: Capability-Heavy External Expert to Internal Specialist

### Example 1 Situation

An imported agent has:

- retired frontmatter such as `infer:` or unsupported decoration such as `color:`
- copied legacy tool catalogs from older product examples
- long expertise catalogs
- broad claims about being an expert in a domain

### Example 1 Keep

- the distinct domain
- the decisions the agent should own
- the output shape users expect

### Example 1 Rewrite

- make `description:` say when the route wins
- turn expertise bullets into routing priorities or output expectations
- normalize copied tool ids to canonical aliases and declare a short explicit `tools:` contract

### Example 1 Internal Pattern

```markdown
---
name: internal-example-domain
description: Use this agent when the repository needs domain-specific strategy, tradeoff analysis, and tactical next steps for ...
---

# Internal Example Domain

## Role

You are the specialist command center for ...

## Routing Rules

- Use this agent when ...
- Do not use this agent when implementation delivery is the main task.

## Output Expectations

- Decision frame
- Main tradeoffs
- Top risks
- Recommended next action
```

## Example 2: Workflow-Heavy Scaffold Agent to Internal Control Center

### Example 2 Situation

An imported agent is organized around commands such as bootstrap, validate, migrate, or sync.

### Example 2 Keep

- the ordered workflow
- the governing rules
- the checkpoints that protect correctness

### Example 2 Rewrite

- keep one command-center role
- use `## Core Rules` for policy guardrails
- use `## Skill Usage Contract` only when declared skills are conditional
- rewrite slash commands into repo-local execution steps

### Example 2 Internal Pattern

```markdown
---
name: internal-example-control-center
description: Use this agent when the repository needs ...
---

# Internal Example Control Center

## Role

You are the command center for ...


## Core Rules

- Treat ... as canonical.
- Do not preserve fallback variants.

## Skill Usage Contract

- `internal-audit-skill`: Use when ...
- `internal-authoring-skill`: Use when ...

## Routing Rules

- Use this agent when ...
- Do not use this agent when one-resource authoring is enough.

## Execution Workflow

1. Inspect current state.
2. Classify findings.
3. Apply the canonical change.
4. Validate and report drift.

## Output Expectations

- Objective
- Findings or decisions
- Changes applied or recommended
- Validation status
```

## Example 3: Governance Reviewer to Agent-plus-Skill Split

### Example 4 Situation

An imported agent is mostly made of checklists, policy rules, and enforcement steps.

### Decision

Keep a short agent only if named routing matters. Move the detailed review procedure into a skill when another agent could reuse it.

### Split Pattern

Agent owns:

- when the governance route wins
- which reusable skills it depends on
- how findings should be reported

Skill owns:

- detailed checks
- policy matrices
- step-by-step review workflow
- validation rules

### Smell

If the agent body reads like a long handbook, it is probably a skill pretending to be an agent.

## Example 4: Provider Architect with Tool Catalog to Evidence-First Internal Cloud Agent

### Situation

An imported cloud architect agent has:

- vendor-specific MCP or documentation tools in frontmatter
- a large best-practice checklist
- a framework matrix such as Well-Architected pillars
- a long list of clarifying questions

### Example 4 Keep

- the docs-first decision model
- the critical requirement gate
- the expected tradeoff-heavy output shape

### Example 4 Rewrite

- move stale tool dependencies into repo-local research skills, routing rules about official documentation, or a short current `tools:` list that stays explicit and role-shaped
- turn the framework matrix into a short decision lens in routing rules or output expectations
- compress the clarifying questions into a short list of critical constraints
- keep the route focused on when the provider-specific agent wins

### Example 4 Internal Pattern

```markdown
---
name: internal-example-cloud
description: Use this agent when the task needs provider-specific architecture guidance backed by current official guidance.
---

# Internal Example Cloud

## Role

You are the provider-specific cloud command center for architecture tradeoffs, incident diagnosis, and tactical next steps.


## Routing Rules

- Clarify the critical requirements first: scale, resilience, compliance, budget, and operating constraints.
- Confirm current provider facts with official documentation before finalizing recommendations.
- State the main tradeoff explicitly across security, reliability, performance, cost, or operations.
- Do not use this agent when the question is still provider-agnostic or cross-boundary; prefer `internal-planning-leader`.

## Output Expectations

- Requirement gaps or confirmed constraints
- Confirmed provider facts or documented patterns
- Main tradeoff
- Main risks
- Recommended next action
```
