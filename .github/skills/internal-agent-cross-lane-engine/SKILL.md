---
name: internal-agent-cross-lane-engine
description: Use when one of the four canonical operational agents needs the shared cross-lane boundary, medium-task, and anti-overlap policy.
---

# Internal Agent Cross-Lane Engine

Use this skill as the shared engine for the four canonical operational agents in the direct-entry operational model.

This skill is intentionally shared. It owns the reusable rules that would otherwise drift across `internal-delivery-operator`, `internal-planning-leader`, `internal-review-guard`, and `internal-critical-master`. It is not a copy of the agents.

## When to use

- One of the four canonical operational agents needs the shared cross-lane boundary and anti-overlap logic.
- A planning, execution, review, or challenge decision depends on the shared medium-task thresholds.
- Canonical-agent ownership drift needs to be resolved without rewriting the same rules into multiple agents.

## Shared Core Rule

Check relevant OBRA skills before starting any task. If a workflow is relevant, it is mandatory, not optional. Do not preload irrelevant workflows.

Implications:

- Apply OBRA only when the task shape actually triggers the workflow.
- Keep small tasks small.
- Do not skip a relevant OBRA workflow just because the agent already knows what to do.

## Boundary Model

| Canonical owner | Owns | Does not own |
| --- | --- | --- |
| `internal-delivery-operator` | Clear, local execution and deterministic repository-owned maintenance or realignment with concrete verification and limited risk | Strategic tradeoffs, ambiguous scope, non-trivial repository-owned authoring, review-first asks, or critical challenge |
| `internal-planning-leader` | Ambiguity resolution, decision records, plans, non-trivial repository-owned authoring, and rollout or governance decisions that remain open | Default local execution once the design is settled, deterministic maintenance whose target state is already known, defect-first review, or pure challenge |
| `internal-review-guard` | Review, validation, merge readiness, regression risk, evidence gaps, and defect-first findings | Implementation, initial design ownership, or open-ended strategic challenge |
| `internal-critical-master` | Pre-mortems, assumption stress tests, alternative framings, failure modes, and strong objections | Implementation, routine technical review, or final operational planning |

## Medium-Task Thresholds

`internal-delivery-operator` stays owner only when all of these are true:

- The outcome is already clear and concrete verification exists.
- The work is deterministic implementation or repository-owned maintenance or realignment with no non-trivial strategy tradeoff.
- File count and adjacent boundary crossing stay within one coherent area, or do not create a new ownership or catalog decision.
- Routing, ownership, naming contracts, and catalog boundaries are being applied rather than redesigned.

File count and adjacent boundary crossing are heuristics, not automatic planning triggers.

A clear realignment across more than two adjacent `.github/` assets can stay with `internal-delivery-operator` when the target state is already known and validation is concrete.

`internal-planning-leader` becomes owner when at least one of these is true:

- Real ambiguity remains about the right shape, contract, or rollout.
- There are `>= 2` credible solution paths with non-trivial tradeoffs.
- The change affects routing, ownership, naming contracts, or catalog boundaries in substance, not just by touching adjacent files.
- The task needs rollout, regression, governance, or rollback decisions.
- The task creates a new repository-owned resource instead of a banal update to an existing one.

## Lane-Change Protocol

The canonical operational model uses direct entry: users select one of the four canonical owners directly, and ambiguous entry fails safe to `internal-planning-leader`.

Once active, each owner stays inside its boundary. When the boundary no longer holds, use `internal-agent-boundary-recommendation-engine` for the user-visible stop-and-recommend behavior instead of cloning that protocol or matrix here.

The four canonical owners are not subagent-invoked by default. Any future exception must be explicit, narrow, one-directional, and must not create an all-to-all mesh or nested ping-pong.

## Mandatory Engine vs Optional Support

Use this policy across all canonical agents:

- `## Mandatory Engine Skills` lists only the skill or skills required before the agent can operate correctly.
- `## Optional Support Skills` lists conditional helpers, tactical specialists, or OBRA workflows that matter only for some tasks.
- Do not place required engines inside the optional list.
- Do not create 1:1 decorative engine skills for symmetry alone.
- A shared engine is preferable when the same reusable rules would otherwise drift across multiple agents.

Load `references/ownership-maps.md` when you need:

- the current canonical skill-to-owner lookup
- the retired-to-canonical owner mapping
- the shorthand rules for cloud and runtime skills inside the operational model

## Relationship Model

- The direct-entry model has no repository-owned front-door router above the four canonical owners.
- `internal-planning-leader` is the safe fallback when the right lane is not clear yet.
- The four canonical owners should stay user-selectable and `disable-model-invocation: true` by default so hidden peer dispatch stays opt-in instead of ambient.
- If a narrower scoped contract ever allows one canonical owner to invoke another, the exception must be explicit, one-directional, auditably bounded, and must not create ping-pong or hidden route selection.
- `internal-planning-leader` absorbs the role previously covered by `internal-ai-resource-creator` when the work is non-trivial repository-owned authoring.
- `internal-review-guard` must reuse `internal-code-review` instead of restating the review playbook in the agent body.
- `internal-delivery-operator` should stay light and load runtime or domain skills only when the task already belongs to execution.
- `internal-critical-master` should stay narrow: challenge the reasoning, reframe hidden constraints when useful, synthesize the pressure test, and tell the user when planning should resume.
- `internal-sync-*` and `awesome-*` assets stay outside this canonical operational model.

## Anti-Overlap Checklist

Before finalizing any operational routing or agent edit, check these questions:

- Is the request primarily execution, planning, review, or challenge?
- Would the same request cause two canonical agents to claim ownership?
- Is a required engine hiding inside `## Optional Support Skills`?
- Is a new skill being created only for symmetry instead of real shared logic?
- Is the agent body repeating logic that belongs in a shared skill?
- Is an imported or sync-only asset being treated as a canonical operational owner?
- Would a power user know when to pick this agent directly without reading three files?

If any answer points to overlap, narrow the agent or move the shared logic into a skill.

## Common Mistakes

| Mistake | Why it matters | Instead |
| --- | --- | --- |
| Letting `internal-delivery-operator` keep medium tasks by momentum | Execution becomes accidental planning | Tell the user the boundary broke and recommend `internal-planning-leader` on the first medium-task threshold hit |
| Treating file count or adjacent boundary crossing as automatic planning triggers | Deterministic realignments get over-routed into planning | Check for real ambiguity, tradeoffs, or ownership change before leaving execution |
| Letting `internal-planning-leader` execute by default | The planner becomes a catch-all generalist | Tell the user when the design is settled and recommend `internal-delivery-operator` |
| Rewriting the review playbook inside `internal-review-guard` | Review logic drifts from the tactical skill | Reuse `internal-code-review` as the mandatory tactical engine |
| Treating challenge as generic negativity | The agent stops producing useful decision pressure | Keep one challenge thread, then synthesize clear failure modes |
| Creating one dedicated engine skill per agent for symmetry | The catalog grows without adding real structure | Use shared engines or existing skills unless a real gap exists |

## Output Expectations

- Current owner and boundary rationale
- Whether the boundary still holds and why
- Which OBRA workflows are relevant for this task
- Which tactical internal skill should be loaded next, if any
