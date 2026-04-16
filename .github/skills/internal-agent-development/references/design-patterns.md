# Agent Design Patterns

Use this file when you need stronger internal agent structure than the base template provides.

It distills reusable patterns from richer external agents without carrying over stale frontmatter or obsolete tool assumptions.

## Table of Contents

- Docs-first specialist
- Discovery-first specialist
- Requirement gate and decision lens
- Capability-to-skill translation
- Command-center workflow
- Negative boundaries
- Output contracts
- Split vs extract

## Docs-First Specialist

Use this pattern when the domain changes quickly and the agent is expected to recommend provider-specific services, limits, or best practices.

Good docs-first characteristics:

- the route says the agent should confirm current official guidance before finalizing recommendations
- tool-specific vendor search is translated into a repo-local research skill or a routing rule about official documentation or configured MCP sources
- the final answer separates documented facts from inferred recommendations

Bad docs-first characteristics:

- copied legacy tool ids or stale runtime wiring in frontmatter
- claims about "latest guidance" with no evidence or verification rule
- provider-specific commands embedded in the agent body

## Discovery-First Specialist

Use this pattern when the agent adds value by framing the problem before proposing action.

Keep only the discovery priorities that materially improve decisions:

- clarify the user's real objective
- inspect the current repository state
- identify constraints, neighboring systems, or risks
- recommend the next action in the correct order

Do not copy long question banks into the agent body. If the questioning logic is reusable and detailed, move it into a skill or prompt.

## Requirement Gate and Decision Lens

Use this pattern when an external specialist is strong because it asks for the right inputs and evaluates options through a stable framework.

Keep the requirement gate compact:

- performance, scale, or availability targets
- security, compliance, or residency constraints
- budget or cost posture
- operational maturity or ownership boundaries
- integration or migration constraints

Translate large framework matrices into a short decision lens:

- state which dimension is being optimized
- state the main tradeoff explicitly
- keep the lens in routing rules or output expectations instead of copying long handbooks

## Capability-to-Skill Translation

External agents often expose long tool lists, framework matrices, or expertise catalogs. Convert them into repository-local constructs.

| Upstream signal | Internal rewrite |
| --- | --- |
| Expertise bullets | `## Role`, `## Routing Rules`, or `## Output Expectations` |
| Tool catalogs | Short explicit `tools:` list with canonical aliases that matches the internal agent's role |
| Platform setup steps | Reference file or skill |
| Slash commands | `## Execution Workflow` when the sequence is core to the role |
| Generic quality checklist | Skill or reference |

Keep only the minimum content needed for routing and operating stance inside the agent.

## Command-Center Workflow

Use `## Execution Workflow` only when the agent repeatedly governs a multi-step operating flow such as sync, audit, rollout guidance, or front-door routing.

Good workflow characteristics:

- 3 to 6 steps
- action verbs first
- repo-local references
- one clear decision point per step

Bad workflow characteristics:

- platform command syntax copied from upstream
- mixed implementation detail and governance policy in the same step
- long nested procedures that belong in a skill

## Negative Boundaries

A strong agent says who should win when it loses.

Include at least one real boundary:

- `Do not use this agent when ...`
- `Prefer \`internal-other-agent\` when ...`
- `If this lane no longer fits, tell the user why and recommend \`internal-other-agent\` instead of routing automatically`
- `Use the matching skill instead when the work is procedural rather than routing-heavy`

If you cannot write a strong negative boundary, the route is probably still too broad.

## Output Contracts

Every strong agent should make success observable in `## Output Expectations`.

Good output contracts are short and role-specific:

- architecture frame, tradeoffs, risks, next step
- findings, severity, recommendation, validation status
- scope, blockers, execution order, follow-up action

Weak output contracts are generic:

- "help the user"
- "provide expertise"
- "be comprehensive"

## Split vs Extract

Split an agent when the routing surface itself is overloaded.

Smells that point to splitting:

- the route sentence needs multiple unrelated domains
- declared skills fall into separate clusters with different triggers
- the body contains conflicting instructions for different audiences
- different tasks would expect different output structures

Extract to a skill when the body is mostly reusable procedure:

- large checklists
- detailed review criteria
- repeated step-by-step methods
- domain knowledge that another agent could also reuse

If the role is still cohesive after extraction, keep one broader agent.
