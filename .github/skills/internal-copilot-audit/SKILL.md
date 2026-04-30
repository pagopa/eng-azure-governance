---
name: internal-copilot-audit
description: Use when auditing repository-owned GitHub Copilot assets for overlap, hollow references, stale contracts, naming drift, or governance drift across `.github/`.
---

# Internal Copilot Audit

Use this skill when auditing the health of the Copilot customization catalog.

This skill is often invoked by planning or sync lanes, but it can also be used directly for a focused repository audit when the user explicitly wants overlap, stale-reference, or governance-drift findings.

Treat the declared governance contract in the relevant agent, root `AGENTS.md`, and `.github/copilot-instructions.md` as the policy source of truth. Treat the current `.github/` catalog on disk as evidence to compare against that policy.

## When to use

- Audit repository-owned GitHub Copilot assets for overlap, hollow references, stale contracts, naming drift, or governance drift.
- Run a focused `.github/` catalog audit from planning or sync work.
- Verify whether governance files still match the live repository catalog on disk.

## Audit Goals

- Detect overlapping skills and agents.
- Detect cleanup recommendations backed only by stale plan paths or files that are absent on the current filesystem.
- Detect hollow assets that point to missing local files or missing companion skills.
- Detect declared skills that have no concrete workflow role in the agent or skill surface that declares them.
- Detect retired frontmatter and stale runtime-specific wording.
- Detect stale or misleading tool contracts in repository-owned internal agents.
- Detect weak `AGENTS.md` bridge design.
- Detect sync workflows that skip or fail to report governance review for `.github/copilot-instructions.md` and root `AGENTS.md`.
- Detect naming violations and stale inventory references.
- Detect governance files that still describe removed, renamed, or retired assets.
- Detect catalog retirements or remaps that were not propagated in the same change to the supported consistency and sync entrypoints, `.github/scripts/check_catalog_consistency.sh` and `.github/scripts/sync_copilot_catalog.sh`.
- Detect token-risk claims that rely on assumed runtime loading behavior instead of observable repository signals such as description length, exact trigger collisions, or repo-profile coverage.

## Audit Order

1. Check naming and frontmatter.
2. Check tool and MCP contract clarity for repository-owned internal agents.
3. Check broken local references.
4. Check declared skill contracts and decorative skill usage.
5. Check trigger overlap.
6. When adding or tightening exact `applyTo` overlap validation, rerun the overlap scan across the whole repository and register every intentional co-load in the allowlist in the same pass.
7. Check bridge coherence between `AGENTS.md` and `.github/copilot-instructions.md`.
8. Check whether skills or agents became redundant after internal replacements were added.
9. Check whether governance files still describe superseded or removed assets.

Before classifying a cleanup as high-evidence, verify the candidate paths exist on the current filesystem. Absent paths are stale plan evidence, not executable deletion work.

Load `references/audit-checklist.md` when you need the detailed issue taxonomy, flagging criteria, or example findings.

## Recommended Outputs

Produce findings with both severity and action:

- Severity: `blocking` or `non-blocking`
- Action: `Delete`, `Replace`, `Patch`, or `Keep`

For each finding, include:

- asset path
- severity
- action
- issue type
- why it matters
- proposed replacement or fix
- tool-contract note when the issue involves explicit tool scope, MCP access, or legacy tool ids

## No-Fallback Rule

When a repository-owned internal replacement exists, prefer deleting the weaker upstream asset instead of keeping a compatibility fallback.

## Anti-Patterns

- Keeping bundle skills that invoke non-existent helper skills
- Keeping source-side command-center assets in consumer sync scope
- Keeping upstream assets whose only value is historical familiarity
- Treating stale inventory references as harmless
- Retiring or remapping managed skills or agents without updating the local sync command center, validator, and sync script in the same change
