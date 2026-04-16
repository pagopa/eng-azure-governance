---
name: internal-agent-development
description: Use when creating or materially revising a repository-owned Copilot agent under `.github/agents/`, or when deciding whether behavior belongs in an agent, skill, prompt, or instruction.
metadata:
  short-description: Create, refine, or realign repository-owned Copilot agents
---

# Internal Agent Development

Use this skill when authoring or materially revising repository-owned agents in `.github/agents/`.

Use `internal-skill-creator` first when the main output is a repository-owned skill under `.github/skills/`. It is the canonical local entrypoint for that work and should handle the repo-local decision gate itself. After that gate is clear, delegate only the remaining bundle anatomy, helper-script, `agents/openai.yaml`, or structural-validation work to `openai-skill-creator` instead of duplicating it. Use `internal-agent-sync-control-center` when deciding keep, refresh, replace, or retire outcomes across the sync-managed catalog rather than improving one agent.

Prefer explicit engine-skill architecture for routers and broader command centers:

- keep routing contract, tool contract, boundaries, boundary recommendations, and output shape in the agent
- move long decision matrices, threshold rules, ownership maps, and reusable operating logic into repo-owned engine skills
- when that engine is required for the agent's core behavior, declare it explicitly instead of burying it in optional skill guidance

## Goals

- Build agents that are easy to route to.
- Keep one cohesive operating role per agent.
- Translate imported agent value into repo-local GitHub Copilot form.
- Move reusable procedures into skills instead of bloating agent bodies.
- Prefer explicit mandatory engine skills when an agent depends on reusable routing or decision logic, and make delegation-completion, degraded-mode, and anti-stall behavior explicit for routers and coordinator-style agents.
- Keep any skill guidance explicit and reviewable when it adds value, without implying platform-enforced execution order.
- Preserve evidence-first guidance patterns for fast-moving vendor or platform domains without cargo-culting obsolete tool wiring.
- Use current GitHub Copilot custom-agent frontmatter deliberately instead of stripping supported properties by default.
- Make approval boundaries, auditability, and dangerous-operation gates explicit when an agent or nearby workflow needs them.

## Read First

Load these inputs before finalizing an internal agent:

- `AGENTS.md` for routing language and repository precedence
- `.github/INVENTORY.md` for the live catalog of managed assets
- `.github/copilot-instructions.md` for the non-negotiable behavior layer
- `references/agent-contract.md` when editing frontmatter, `tools:`, engine-skill sections, or subagent controls
- `references/agent-template.md` when drafting a new agent from scratch
- `references/conversion-checklist.md` when normalizing an imported or legacy agent
- `references/design-patterns.md` when broadening, splitting, or strengthening an agent
- `references/example-transformations.md` when you need before-and-after conversion examples
- `references/review-checklist.md` before final validation or when reviewing an existing agent
- `references/subagent-patterns.md` when the agent needs to invoke or be invoked as a subagent, or when designing coordinator/worker workflows
- `internal-copilot-docs-research` and `.github/skills/internal-copilot-docs-research/references/official-source-map.md` when the change depends on current GitHub Copilot or VS Code platform behavior

When the source agent already has a skill-guidance section such as `## Optional Support Skills` or `## Preferred/Optional Skills`, load only the directly relevant skill files before editing the target agent. Treat those lists as curated routing hints shaped by the repository resource model, not as a platform-enforced requirement to use every listed skill.

## Decision Gate

Pick the right artifact before drafting:

| Need | Prefer |
| --- | --- |
| Named operating role with routing responsibility | Agent |
| Front-door router or broad command center with reusable decision logic | Agent + mandatory engine skill |
| Reusable procedure, checklist, or domain workflow | Skill |
| Short repeatable drafting aid | Prompt |
| File-type or stack-wide coding rule | Instruction |

Choose an agent only when the repository benefits from a stable command center or specialist persona. If the draft is mostly procedure, move the procedure into a skill and keep the agent short.

## Agent Contract

Read `references/agent-contract.md` before changing frontmatter, tool scope, engine-skill sections, or subagent controls.

Keep these rules visible while drafting:

- Internal agents keep filename stem, frontmatter `name:`, and command identifier aligned.
- `description:` is the route and should start with `Use this agent when ...`.
- Internal agents declare `tools:` explicitly with a short, role-shaped contract.
- Use `## Mandatory Engine Skills` only for truly required reusable logic and `## Optional Support Skills` only for conditional support.
- Keep delegation controls explicit with `agents:`, `user-invocable`, and `disable-model-invocation` only when they materially enforce the boundary.
- Keep long procedures in skills, not in the agent body.

## Platform Verification Gate

Before changing claims about frontmatter support, tool aliases, MCP behavior, or subagent invocation:

- load `internal-copilot-docs-research` and `.github/skills/internal-copilot-docs-research/references/official-source-map.md`
- verify the authoritative documentation for the exact surface involved
- mark the claim as unverified if the docs are unreachable

## Engine-Skill Pattern

Use this split when authoring command-center agents:

- Agent body:
  - routing sentence
  - role and stance
  - boundary with neighboring agents
  - tool contract
  - boundary definition and user-facing recommendation pattern
  - output expectations
- Engine skill:
  - decision matrix
  - threshold rules for medium or ambiguous tasks
  - old-to-new ownership mapping
   - completion semantics and degraded-mode rules when delegation-based turns stall or return no usable worker result
  - anti-overlap checklist
  - shared workflow steps that would otherwise be duplicated

Good candidates for a dedicated or shared engine skill:

- front-door routers
- planning leaders
- any command center whose main value is ordered classification or procedural reasoning

Weak candidates for a dedicated engine skill:

- small local executors whose behavior is already well covered by OBRA plus domain skills
- lightweight challengers that do not yet have a real reusable framework
- agents where the proposed skill would mostly restate the agent body

An agent may legitimately use:

- no dedicated engine skill
- one shared engine skill
- one shared engine skill plus one existing tactical engine skill

That asymmetry is a feature, not a defect, when it reduces drift.

## Authoring Workflow

1. Define the operating role in one sentence.
   Use behavioral scope, not prestige language.
2. Scan neighboring agents and trigger overlap.
   Compare `description:` lines first and resolve collisions before drafting.
3. Decide whether the behavior belongs in an agent, a skill, or both.
   Extract reusable procedure into a skill if the draft starts becoming a playbook.
4. If the behavior belongs in both, define the split explicitly.
   Keep route, stance, tool contract, and output shape in the agent; keep reusable procedure in the skill.
5. Draft the `description:` before the body.
   If the routing sentence is vague, the rest of the agent will stay vague.
6. Choose the frontmatter and engine-skill strategy intentionally.
   Keep `tools:` explicit, engine skills small, and support skills cohesive.
7. Normalize imported patterns and remove stale baggage.
   Preserve the decision model while deleting obsolete runtime-specific scaffolding.
8. Add real boundaries and measurable output expectations.
   Non-router agents recommend the better owner when the boundary breaks instead of routing automatically.
9. Validate and de-duplicate.
   Run repository validation and re-check whether the new agent makes another one redundant.

## Capability Translation Rules

When learning from richer upstream agents, keep the signal and drop the scaffolding.

- Translate copied legacy tool catalogs into a short modern `tools:` contract with canonical aliases.
- Translate vendor documentation tools or MCP endpoints into docs-first routing rules, dedicated research skills, or explicit MCP namespaces only when the agent truly depends on those tools.
- Keep `tools:` explicit and least-privilege for every repository-owned internal agent.
- Translate governance or trust patterns into concrete approval rules, audit expectations, and routing boundaries instead of framework-specific policy code.
- Translate expertise lists into routing rules, role focus, or output expectations.
- Translate decision frameworks into a compact decision lens only when the named dimensions still improve tradeoff quality.
- Translate long question banks into a few high-value discovery priorities unless the branching logic is genuinely reusable.
- Preserve ordered execution flow or strong response structure only when they materially improve the role.
- Move platform-specific setup or deployment detail into repo-local references only when this repository actually needs it.
- Keep only examples that clarify routing or output shape; move broader examples into references.

## Governance And Trust Boundaries

When the agent being authored can influence risky actions:

- Separate routing scope from execution permissions.
- Prefer explicit allow, deny, or approval boundaries for destructive, privileged, or externally connected actions.
- State when auditability matters, especially for production changes, data access, credentials, or multi-agent delegation.
- Call out the neighboring command center or human review step when the agent should stop before execution.

## Cohesion and Splitting

Split an agent when one file mixes disjoint operating roles, conflicting instructions, or different winning routes.

Good reasons to split:

- The same agent tries to own both governance and delivery.
- The routing sentence needs `and/or` across unrelated domains.
- The declared skills fall into separate clusters with different triggers.
- Different outcomes are expected by different users.

Do not split only because the file is long. First ask whether the reusable procedure belongs in a skill.

## Imported Pattern Normalization

When adapting external agents:

1. Keep the useful mental model or decision sequence.
2. Delete stale runtime-specific frontmatter and copied tool catalog details that do not belong in the internal contract.
3. Rewrite naming into the canonical `internal-*` contract.
4. Replace platform assumptions with repo-local files, skills, and validations.
5. Convert broad expertise claims into concrete routing or output rules.

Do not over-compress a well-structured upstream agent. If its strength comes from a clear requirement gate, decision lens, execution order, or response structure, preserve those patterns in repo-local form instead of reducing everything to flat bullets.

Load `references/design-patterns.md` for command-center structure questions and `references/example-transformations.md` for side-by-side conversion examples.

## Anti-Patterns

- Prestige-first descriptions that never say when the agent wins routing.
- Imported agents copied almost verbatim with stale platform-specific frontmatter or obsolete tool ids.
- Routers or coordinators that stop after naming the selected owner or saying a handoff will happen, without the delegated result or an explicit blocking explanation.
- A skill-list section as a dumping ground for unrelated capabilities.
- A `## Mandatory Engine Skills` section that merely mirrors the agent body without owning real reusable logic.
- Creating one dedicated skill per agent for visual symmetry even when shared or existing engines already solve the problem.
- Starting from the selected agent file alone and skipping the directly relevant optional support or preferred skills that define how that agent should be applied.
- Treating preferred or optional skills as a fake platform-enforced toolchain or as an origin-based priority ladder.
- Treating optional support skills as if they were the required engine.
- Creating a dedicated mirror skill for `internal-fast-executor` or `internal-critical-challenger` when the shared operating-model engine already carries the reusable logic.
- Preserving the route but throwing away the upstream agent's best structure, leaving a compliant internal agent that is harder to use and less decisive.
- Treating `tools:` or `model:` as deprecated in current GitHub Copilot custom agents.
- Copying multi-screen tool lists from older examples instead of normalizing them to canonical aliases and an explicit minimal contract.
- Relying on implicit all-tools access instead of declaring the internal agent's actual tool contract.
- Using retired frontmatter such as `infer:` or unsupported decoration such as `color:`.
- Agent bodies that hide important constraints in long narrative prose.
- Specialist agents that are really just long procedures and should be skills.
- Command centers that own unrelated domains because splitting was deferred.
- Output sections that say nothing measurable about a successful response.

## Validation

- Confirm internal agents keep filename stem, frontmatter `name:`, and command identifier identical.
- Confirm any intentionally non-internal agent has an explicit reason to keep a different external-facing `name:`.
- Confirm the `description:` says when to use the agent instead of restating its workflow.
- Confirm `tools:` exists in every repository-owned internal agent.
- Confirm any explicit `tools:` list uses canonical aliases or MCP namespaces and that the scope is intentional.
- Confirm the `tools:` list is role-shaped and does not rely on implicit all-tools access.
- Confirm retired `infer:` is absent and that `disable-model-invocation` or `user-invocable` is used when selection behavior needs control.
- If the agent includes `## Mandatory Engine Skills`, confirm every listed skill exists on disk and is truly required for the agent's core behavior.
- If the agent includes `## Mandatory Engine Skills`, confirm the engine owns reusable logic that would otherwise bloat the agent or drift across multiple agents.
- Confirm `## Optional Support Skills` does not duplicate `## Mandatory Engine Skills`.
- For canonical operational agents, confirm `## Optional Support Skills` is used instead of `## Preferred/Optional Skills`.
- If the agent includes a skill-list section, confirm the list matches the intended reusable procedures.
- If the agent includes a skill-list section, confirm the wording does not imply that `internal-*` skills automatically outrank imported skills.
- Confirm any existing command-center agent used as a source or workflow anchor had its directly relevant declared skills loaded before final decisions were made.
- Confirm the agent has a meaningful routing boundary and is not just "expert at everything in X."
- Confirm routers keep classification matrices, fallback rules, and old-to-new ownership mapping in an engine skill instead of long body prose when that logic is substantial.
- For routers or coordinator-style agents that delegate within the turn, confirm the contract forbids classification-only completion and defines degraded-mode behavior when delegation does not return usable content.
- Confirm routers are treated as the strongest case for a dedicated engine and that shared operational logic for the four canonical owners stays in a shared engine instead of branching into decorative mirrors.
- Confirm the final internal agent preserved the strongest usable structure from the source pattern when that structure improved requirement discovery, tradeoff analysis, or response quality.
- Confirm reusable procedures live in skills, not in the agent body.
- Confirm the new or changed agent does not make an existing agent redundant.
- Use `references/review-checklist.md` for a final pass when the change broadens scope or imports external patterns.
- Run the repository validation entrypoints that currently exist after changes that affect agent naming or inventory, and report the gap explicitly when no dedicated validator is present.
