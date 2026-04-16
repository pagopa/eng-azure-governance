---
name: internal-copilot-audit
description: Use when auditing repository-owned GitHub Copilot assets for overlap, hollow references, stale contracts, naming drift, or governance drift across `.github/`.
---

# Internal Copilot Audit

Use this skill when auditing the health of the Copilot customization catalog.

Treat the declared governance contract in the relevant agent, root `AGENTS.md`, and `.github/copilot-instructions.md` as the policy source of truth. Treat the current `.github/` catalog on disk as evidence to compare against that policy.

## Audit Goals

- Detect overlapping skills and agents.
- Detect hollow assets that point to missing local files or missing companion skills.
- Detect declared skills that have no concrete workflow role in the agent or skill surface that declares them.
- Detect retired frontmatter and stale runtime-specific wording.
- Detect stale or misleading tool contracts in repository-owned internal agents.
- Detect weak `AGENTS.md` bridge design.
- Detect sync workflows that skip or fail to report governance review for `.github/copilot-instructions.md` and root `AGENTS.md`.
- Detect naming violations and stale inventory references.
- Detect governance files that still describe removed, renamed, or retired assets.

## Audit Order

1. Check naming and frontmatter.
2. Check tool and MCP contract clarity for repository-owned internal agents.
3. Check broken local references.
4. Check declared skill contracts and decorative skill usage.
5. Check trigger overlap.
6. Check bridge coherence between `AGENTS.md` and `.github/copilot-instructions.md`.
7. Check whether skills or agents became redundant after internal replacements were added.
8. Check whether governance files still describe superseded or removed assets.

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
