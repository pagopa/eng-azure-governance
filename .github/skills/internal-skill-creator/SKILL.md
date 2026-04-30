---
name: internal-skill-creator
description: Use first when creating, splitting, replacing, or materially revising a repository-owned skill under `.github/skills/`, especially when trigger, boundary, or validation decisions must be made locally before `openai-skill-creator`.
---

# Internal Skill Creator

Use this skill as the canonical repository-owned first entrypoint for skill authoring in this repository.

Keep the ownership model explicit:

- `internal-skill-creator` is the canonical local owner for repository-owned `.github/skills/` work.
- `openai-skill-creator` is the core operating engine inside that wrapper for bundle anatomy, reusable resources, `agents/openai.yaml`, initialization workflow, and structural validation.
- This skill adds the repository-specific gate: prove the need, choose reuse versus creation, keep triggers retrieval-safe, harden the result against rationalization and boundary drift, and delegate only the remaining bundle work to OpenAI.

This means `internal-skill-creator` should trigger first for repository-owned skill work, establish the local boundary, and then deliberately hand only the remaining bundle mechanics to `openai-skill-creator` instead of competing with it or duplicating it.

Use `internal-agent-sync-control-center` when the task is broader catalog governance, sync-managed external assets, or inventory-wide retirement and refresh work.

Use `internal-agent-development` when the primary output is an agent change or an agent/skill boundary rewrite.

## Read first

- Read the target `SKILL.md` plus the nearest competing skills that could already own the request.
- Read root `AGENTS.md` and `.github/copilot-instructions.md` before changing repository-owned scope or policy language.
- Read `.github/INVENTORY.md` when a skill may be added, retired, renamed, or replaced.
- Load `references/writing-skills-checklist.md` when creating a new skill or materially revising an existing one.
- Read `openai-skill-creator` only after the local boundary is clear and only for the remaining bundle work that this skill is not meant to repeat.

## When to use

- Creating a new repository-owned skill under `.github/skills/`.
- Replacing or splitting an existing repository-owned skill whose current boundary is wrong.
- Materially revising a repository-owned skill's scope, trigger, structure, bundled resources, or validation.
- Tightening a skill whose description is too broad, too procedural, or too weak to retrieve reliably.

## When not to use

- The task is catalog governance, inventory maintenance, or sync routing. Use `internal-agent-sync-control-center` instead.
- The task is primarily agent authoring or agent/skill architecture. Use `internal-agent-development` instead.
- The task is outside `.github/skills/` or does not change a repository-owned skill.
- The existing skill already covers the need and the change is a pure copyedit that does not affect retrieval, boundary, validation, or bundle structure.

## Division of labor

Treat `internal-skill-creator` and `openai-skill-creator` as complementary, not symmetric.

This skill should do:

- decide whether the task really belongs to a repository-owned skill in this repository
- choose no-op, reuse, revise in place, split, replace, or retire
- define the local ownership boundary and trigger wording
- enforce the failing-baseline rule, token discipline, and skill-type testing expectations
- re-check routing fallout in nearby repository-owned assets

`openai-skill-creator` should do:

- scaffold or normalize the bundle shape
- handle reusable-resource anatomy for `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`
- provide initializer, metadata-generation, and structural-validation workflow

Do not restate the full OpenAI creation workflow here. Use this skill to decide and constrain the work, then hand off only the remainder that OpenAI already handles better.

## Trigger precedence

- For any repository-owned skill work under `.github/skills/`, start with `internal-skill-creator`, not `openai-skill-creator`.
- Use `openai-skill-creator` only after this wrapper has established that the task really belongs to a repository-owned skill in this repository and there is remaining bundle work that should not be duplicated locally.
- If both skills appear relevant, prefer this skill first because its description is the repo-local route and the OpenAI skill is the embedded engine.
- If `openai-skill-creator` is already in play for generic bundle mechanics, hand repository-specific routing, ownership, and retrieval decisions back to this skill instead of letting OpenAI guess the local policy.

## Decision gate

| Situation | Best answer |
| --- | --- |
| Wording cleanup with no change to retrieval, owner, or validation | Update in place or do nothing |
| Same owner, but weak trigger/body/validation is causing misses | Revise the existing skill |
| One skill is handling two intents or colliding with another local owner | Split, replace, or retire the weaker skill |
| The change affects multiple skills, inventory meaning, or sync-managed assets | Use `internal-agent-sync-control-center` |
| The local decision is made and the remaining work is bundle anatomy, reusable resources, `agents/openai.yaml`, or validator usage | Delegate that remainder to `openai-skill-creator` |

## Core rules

- Start by checking whether an existing repository-owned skill can be reused, narrowed, or updated in place.
- Do not create a new skill until you can state the concrete failure, ambiguity, or repeated authoring miss it must prevent.
- Require a baseline failure before a new or materially revised skill is accepted. If the undesired behavior has not been observed, the case is not ready.
- Check frontmatter integrity before debating trigger wording. Broken frontmatter is a structural failure, not a content-polish issue.
- Treat skills as reusable reference guides, not narratives about how one task was solved once.
- Review the nearest competing skills before editing. Retrieval quality is judged against neighboring owners, not in isolation.
- Prefer the smallest change that fixes the local problem.
- Keep `description:` trigger-only. It should say when the skill applies, not summarize the workflow.
- Prefer tightening a description or adding one boundary note over a broad rewrite when that fixes the observed miss.
- Use active, searchable naming when creating a new skill. Prefer direct verbs or action-shaped names over abstract labels when that improves retrieval.
- Make descriptions searchable with concrete terms people would actually type: skill, trigger, `.github/skills/`, `SKILL.md`, create, replace, revise, update, reuse, validation.
- Preserve a working `description:` during token optimization unless the baseline shows the route itself is the problem.
- Keep the body lean. Put only the local contract in `SKILL.md` and move optional depth into references or reusable tools when repeated need justifies it.
- When a skill sits behind a paired agent or local references, keep one owner per detail layer: route and boundary in the agent, reusable workflow in `SKILL.md`, and deep detail in `references/`.
- Prefer `references/` over new `scripts/` for static tables, starter templates, and audit taxonomies. Add scripts only when the workflow is deterministic, repeated, and execution-heavy.
- Keep cross-references explicit instead of duplicating large chunks of generic bundle guidance.
- In source-side skill Markdown, cite only paths that exist on disk in the source repository. When sync materializes a target-only file, prefer the source template path or descriptive prose over the consumer-only materialized path.
- Do not mirror the full OpenAI bundle workflow in this skill. Point to it when the remaining task is already covered there.
- A good outcome may be reuse, narrowing, deletion, or replacement. Do not let the workflow bias toward creating another skill.

## OpenAI handoff points

After the local decision gate is complete, hand off to `openai-skill-creator` only when you need one or more of these:

- new bundle scaffolding
- regeneration or repair of `agents/openai.yaml`
- bundle-shape guidance for `references/`, `scripts/`, or `assets/`
- structural validation via the OpenAI validator

## Baseline evidence

- Iron law: no new skill and no material skill edit without a failing baseline first.
- Accept concrete local evidence such as a failed retrieval, repeated review feedback, trigger overlap, weak discovery wording, stale validation expectations, or a documented miss in `tmp/superpowers/`.
- Reject vague justification such as "this feels reusable", "the repo might need it later", or "the text looks light".
- Treat "it's only wording" as insufficient unless the wording change clearly alters retrieval, boundary, or validation behavior.
- Apply the same standard to edits as to new skills. A major edit without a failing baseline is still missing proof.

## Workflow

1. Prove the need first.
   Record the baseline failure, ambiguity, or repeated authoring miss the skill must prevent.
2. Reject the weakest answer.
   Prefer reuse, tightening an existing trigger, or doing nothing when the evidence does not justify a new repository-owned owner.
3. Set the boundary before writing.
   Decide what this skill owns locally and which adjacent owner should win when the task is really sync governance, agent authoring, or another domain.
4. Isolate the remainder.
   Identify which parts of the job are still local policy work and which parts are now generic OpenAI bundle work.
5. Hand off only the remainder that OpenAI already handles well.
   Load `openai-skill-creator` for scaffolding, resource anatomy, `agents/openai.yaml`, or structural validation, but do not replay its full workflow in this skill.
6. Resume local control for wrapper checks.
   Use `references/writing-skills-checklist.md` to tighten trigger wording, token discipline, loophole closure, and test design.
7. Validate the right thing.
   Ensure OpenAI-side structural checks ran if bundle mechanics changed, then check retrieval quality plus skill-type behavior before treating the skill as done.
8. Re-check routing fallout.
   Update nearby references or paired agent text only when the visible local entrypoint or ownership meaning actually changed.

Use `references/writing-skills-checklist.md` for the anti-rationalization rules, token-discipline reminders, and skill-type testing expectations that this wrapper should enforce.

## Validation

Then confirm:

- `name:` matches the folder name exactly.
- `agents/openai.yaml` exists and still matches the skill's current purpose when bundle metadata was part of the task.
- the skill is repository-owned and still the smallest credible answer to the problem.
- the description matches the real trigger without describing the workflow.
- the description is strong enough that repository-owned skill requests should retrieve this skill before the generic OpenAI one.
- the result makes rejection, reuse, and in-place tightening as natural as creation or replacement.
- the skill still points to the right adjacent owner when the work is actually catalog governance or agent authoring.
- the skill reads like a reusable guide instead of a one-off narrative.
- the edited skill does not repeat agent-owned routing or boundary language.
- the edited skill points to reference-owned deep material instead of copying it back into `SKILL.md`.
- any paired agent or local references still agree with the skill boundary when they exist.
- OpenAI-side scaffolding or validation was invoked only when the remaining work actually required it.
- the retrieval and pressure tests appropriate to the skill type have actually been run.
- the body did not become a maintenance fork of generic OpenAI bundle documentation.

## Repository follow-up

- Update nearby routing or support-skill references when this skill changes the visible local entrypoint.
- Re-check `.github/INVENTORY.md` whenever a repository-owned skill is added, retired, renamed, or replaced.
- Escalate to `internal-agent-sync-control-center` when the change becomes catalog governance instead of one-skill authoring.

## Common mistakes

- Writing a skill because a request feels familiar, not because the repository needs a reusable owner.
- Treating `openai-skill-creator` as irrelevant when it should be the bundle-design core.
- Mixing catalog governance into a repo-owned skill authoring contract.
- Turning every change into a new skill instead of tightening or reusing an existing one.
- Using a long description that tells the agent what to do instead of when to load the skill.
- Skipping `agents/openai.yaml` even though the repository expects it for internal skills.
- Skipping the baseline and rationalizing the change as "small enough".
- Copying OpenAI bundle anatomy or OBRA process weight wholesale into the local wrapper instead of selecting only what improves the repository-owned owner.
