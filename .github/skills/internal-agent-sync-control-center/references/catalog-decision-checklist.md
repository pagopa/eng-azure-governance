# Catalog Decision Checklist

Use this reference when a sync review needs detailed keep/update/extract/retire heuristics beyond the main workflow.

## Overlap Review Checklist

Delete or replace an asset when most of these are true:

- the description triggers on the same requests as another installed asset
- the competing asset is more structured or more complete
- the weaker asset adds no distinctive workflow
- the weaker asset routes to missing resources or stale instructions
- the repository already has an internal asset that should own the domain

Keep specialized subskills only when they narrow trigger space instead of broadening collision.

## Refresh Rules

When refreshing an installed external-prefixed asset:

1. Keep the existing local identifier and prefix.
2. Preserve only the capability that still maps to the current repository.
3. Remove stale runtime assumptions, deprecated frontmatter, and broken bundled references.
4. Do not add new sibling assets from the same family unless the user explicitly expands scope.
5. Update governance files only when routing or inventory meaningfully changes.

## Extraction Rules

When `internal-sync-control-center` or a nearby sync asset is turning into a knowledge dump:

1. Keep the agent cohesive around routing, managed scope, approval posture, and orchestration.
2. Move long reusable procedures into this skill or the right existing internal skill.
3. Use `internal-agent-development` if the extraction changes the agent's structural contract.
4. Point the agent at the canonical skill explicitly.
5. Keep the extracted workflow reusable outside the single current task.
