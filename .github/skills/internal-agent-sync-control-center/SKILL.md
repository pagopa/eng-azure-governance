---
name: internal-agent-sync-control-center
description: Use when maintaining the sync-managed `.github/` catalog behind `internal-sync-control-center`, especially for keep/update/extract/retire decisions, approved external refreshes, and governance-drift checks.
---

# Internal Agent Sync Control Center

Use this skill as the default operating engine for `.github/agents/internal-sync-control-center.agent.md`.

This skill owns the reusable catalog-governance procedure behind that agent. Keep the agent focused on routing, managed scope, approval posture, and output contract. Keep the reusable sync workflow, decision rules, and anti-drift checks here.

Use the current repository state as evidence and starting context, but anchor decisions to the declared contract in the relevant agent, root `AGENTS.md`, and `.github/copilot-instructions.md`.

Use `internal-skill-creator` first when a sync decision requires creating, replacing, or materially rewriting one repository-owned skill. It is the canonical local entrypoint for repository-owned skill work in this repository.

Use `openai-skill-creator` only for the remaining bundle anatomy, helper scripts, progressive disclosure, `agents/openai.yaml`, or structural validation work after `internal-skill-creator` has established the repository-owned skill boundary and decided the local ownership outcome.

Use `internal-agent-development` when the sync changes the control-center agent, rewrites agent routing boundaries, or changes how the agent/skill split is structured.

When deterministic change detection matters, read `references/fingerprinting-contract.md`, use the canonical repository implementation in `.github/scripts/lib/fingerprinting.py`, and use `scripts/sync_resource_fingerprint.py` from this skill only as a thin workflow wrapper.

## Goals

- Keep one clear canonical asset per intent across the managed `.github/` catalog.
- Make `internal-sync-control-center` visibly depend on one named operating engine instead of an implicit catalog skill.
- Refresh only approved in-scope external-prefixed assets without expanding scope accidentally.
- Move reusable sync procedure into this skill instead of bloating the agent body.
- Keep naming, frontmatter, links, descriptions, and governance references deterministic.
- Remove fallback, alias, deprecated, or compatibility-only drift in the same pass that introduces the canonical replacement.
- Keep low-frequency imported or internal capabilities documented as on-demand depth when they still add distinct value and do not justify a repository-owned wrapper.
- Keep governance review of root `AGENTS.md` and `.github/copilot-instructions.md` explicit, never implied.
- Provide a deterministic fingerprinting workflow that distinguishes real content change from formatting noise.

## Agent Coupling Contract

For `internal-sync-control-center`, keep the split strict:

- Agent owns routing, scope boundaries, managed resource map, approval posture, and output expectations.
- This skill owns audit order, keep/update/extract/retire decisions, anti-overlap heuristics, and sync execution discipline.
- `internal-agent-development` owns structural changes to the agent itself, including mandatory engine-skill architecture and boundary rewrites.
- `internal-skill-creator` owns repository-owned skill authoring and should be the first local route when one concrete skill needs creation, replacement, or major redesign.
- `openai-skill-creator` covers only the remaining bundle mechanics during that work; it should not replace the local decision gate or duplicate repository-owned routing logic.

Do not collapse these roles back into one file just because the current task touches all of them.

## Decision Order

1. Check the declared managed scope in `internal-sync-control-center` plus the live local inventory and nearby trigger space.
2. Decide whether the capability should remain an `internal-*` asset, remain an approved in-scope external-prefixed asset, or be retired.
3. Prefer consolidation over coexistence when two assets compete for the same trigger space.
4. Repair broken references only when the asset still adds distinct value to the declared catalog.
5. Apply the canonical change first, then remove deprecated duplicates, stale references, and hollow dependencies in the same pass.
6. Re-check root `AGENTS.md` and `.github/copilot-instructions.md` whenever catalog meaning, routing, or governance language changed.

## Classification Matrix

| Case | Action |
| --- | --- |
| Repo-specific sync workflow or governance logic | Create or update an `internal-*` asset |
| Control-center reusable operating logic | Keep it in this skill |
| Installed external-prefixed asset still useful and declared in scope | Refresh in place |
| Thin alias, fallback copy, or deprecated variant | Delete the weaker asset |
| Broken or stale asset with no unique value | Retire it |
| Installed capability is still distinct but low-frequency or on-demand | Keep it as dormant support depth and document why; do not wrap it unless the root wrapper threshold is met |
| Agent body becoming procedural or duplicative | Extract procedure into this skill or the right internal skill |
| Agent routing or engine-skill split changing materially | Use `internal-agent-development` |

Load `references/catalog-decision-checklist.md` when you need the detailed keep/update/extract/retire heuristics or overlap tests.

## Workflow

### 1. Inventory Before Editing

- Read the target asset and the closest competing assets.
- Compare `description:` lines first. Trigger overlap starts there.
- Check whether the repository already has a stronger internal equivalent.
- Check whether the asset references files that do not exist.
- Check whether nearby agents, skills, instructions, `AGENTS.md`, or `.github/copilot-instructions.md` still route to the asset.
- Check whether the asset still belongs to the declared managed scope or only survives due to repository drift.

### 2. Pick the Right Outcome

Use these heuristics:

- Keep both only when they serve clearly different intents.
- Merge only when the surviving asset becomes easier to trigger and easier to maintain.
- Delete when one asset is just a noisier, thinner, or less structured version of another.
- Keep dormant imported or internal capabilities when they still provide distinct on-demand value and the root wrapper threshold is not met.
- Create or update an internal asset when the capability is strategic for this repository and should not depend on external wording or lifecycle.
- Refresh an in-scope external-prefixed asset only when it still adds distinct value to the declared managed catalog.

### 3. Author or Refresh Carefully

Required frontmatter for skills:

```yaml
---
name: internal-example
description: Clear trigger language that says when the skill should be used.
---
```

Rules:

- `name:` must match the directory name exactly.
- Put trigger language in `description:`, not buried in the body.
- Keep `description:` focused on triggering conditions; do not summarize the workflow there.
- Keep repository-facing text in English.
- Keep the local canonical identifier when refreshing an installed external-prefixed asset.
- Do not keep runtime-specific clutter, compatibility prose, or history-preserving aliases unless policy explicitly requires them.

### 4. Keep Sync Evidence Deterministic

When a sync workflow needs evidence that a managed resource truly changed:

- Prefer deterministic comparison over visual or memory-based judgment.
- Read `references/fingerprinting-contract.md` before changing the comparison contract.
- Use `scripts/sync_resource_fingerprint.py snapshot ...` to build a retained manifest when the workflow benefits from repeatable evidence.
- Use `scripts/sync_resource_fingerprint.py diff ...` to compare two manifests instead of hand-reviewing large file sets.
- Compare normalized content, not only the raw fetched file.
- Record source, target path, normalization version, and content hash when a retained manifest materially improves safety.
- Keep any retained sync evidence under repository-root `tmp/` and treat it as auxiliary workflow output, not catalog policy.
- Do not introduce hashing manifests or helper scripts as decorative machinery; add them only when they clearly reduce false positives, repeated work, or unsafe refresh decisions.
- Use the normalization rules, manifest schema, and output defaults from `references/fingerprinting-contract.md` instead of forking them inline.

### 5. Re-check Governance Immediately

After catalog changes:

- Re-check root `AGENTS.md` for routing, naming, bridge, and canonical-owner drift.
- Re-check `.github/copilot-instructions.md` for repo-wide projection drift.
- Re-check `.github/INVENTORY.md` for exact path accuracy.
- Re-check nearby agents and skills for stale references, decorative declarations, or broken ownership assumptions.

## Validation

Before finishing:

- Confirm `name:` equals the folder name.
- Confirm every referenced local file exists.
- Confirm representative bundled scripts run successfully when added or changed.
- Confirm the description is specific enough to trigger, but not broad enough to collide with half the catalog.
- Confirm the skill remains in English.
- Confirm inventory and governance files do not point to removed paths.
- Confirm the agent still names this skill explicitly as its engine or default operating workflow.
- Confirm the change did not leave decorative skill declarations behind.
- Confirm no fallback alias or compatibility-only duplicate remains beside the canonical asset.

## Anti-Patterns

- Keeping duplicate assets "just in case."
- Refreshing an external asset just because upstream changed when the local catalog does not need it.
- Creating machinery-heavy sync helpers that never become part of a real workflow.
- Creating a control-center engine skill that merely says "see another skill."
- Leaving retired or deprecated assets in the live catalog.
- Hiding important trigger words deep in the body instead of the description.

## Handoff

When this skill is used from `internal-sync-control-center`:

1. Audit the catalog.
2. Decide keep, refresh, replace, extract, or retire.
3. Apply the catalog changes.
4. Re-check root `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/INVENTORY.md`.
5. Run repository validation.
