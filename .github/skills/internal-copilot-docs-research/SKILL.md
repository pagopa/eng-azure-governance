---
name: internal-copilot-docs-research
description: Use when a `.github/` customization change depends on current GitHub Copilot or MCP platform behavior and repo-local policy alone is not enough.
---

# Internal Copilot Docs Research

Use this skill when a repository customization decision depends on current GitHub Copilot behavior rather than repo-local convention alone.

## Purpose

This skill standardizes how to research GitHub Copilot platform behavior before changing repository-owned customization assets.

It is especially useful when the question touches:

- repository custom instructions
- path-specific instructions
- agent skills
- custom agents
- custom-agent frontmatter fields and environment support
- custom-agent tool aliases and MCP namespacing
- MCP support or MCP server behavior
- environment-specific feature support across GitHub, IDEs, and Copilot CLI

## Core repository inputs

Read the local contract before deciding that the platform should change the repo:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- the relevant local agent, skill, or instruction file being changed
- `references/official-source-map.md`

## Source Priority

Use sources in this order:

1. Local repository contract for repo-specific policy and naming
2. Official GitHub documentation on `docs.github.com`
3. GitHub-owned references explicitly linked from the official docs, such as GitHub-maintained customization examples, only when needed
4. MCP resources, templates, or tools that are actually available in the current session, but only to confirm live session capability or repository-local configuration

Do not assume MCP is configured just because GitHub Copilot supports it.

## Research Workflow

1. Read the local contract first.
2. Open the official GitHub documentation page that is authoritative for the surface involved.
3. For custom agents, prefer the custom-agent configuration reference for frontmatter, tool aliases, retired keys, MCP namespacing, and environment-specific behavior.
4. Re-check feature scope, preview status, and GitHub.com versus IDE differences before drawing conclusions.
5. Detect live MCP capability in the current session only if the change depends on what is configured right now rather than on the product contract.
6. If a relevant MCP server, tool, resource, or template is available, use it for live capability facts or server-specific behavior.
7. If no relevant MCP capability is available, state that explicitly and continue with official documentation.
8. Reconcile the platform behavior with this repository's intentionally narrower implementation contract.
9. Convert the conclusion into precise repo changes and run validation after structural edits.

## Decision Heuristics

- Use repository-wide custom instructions for simple guidance that helps across the whole repository.
- Use path-specific instructions for rules that only matter for certain file families or directories.
- Use skills for detailed, reusable task workflows that should load only when relevant.
- Use agents for recurring orchestration roles with stable routing boundaries.
- Use MCP for live tools, external context, or server-backed workflows only when the current session actually exposes the needed capability.
- When researching custom agents, treat `tools:` as supported, not deprecated. GitHub Copilot allows omitted `tools:`, but this repository's internal-agent policy requires an explicit `tools:` contract for repository-owned internal agents.
- Prefer canonical tool aliases such as `read`, `edit`, `search`, `execute`, `agent`, and `web` over legacy product-specific tool ids from older examples.
- Treat `infer:` as retired. Use `disable-model-invocation` and `user-invocable` when selection behavior must be constrained.
- Treat `mcp-servers:` as GitHub.com and Copilot CLI configuration, not as an IDE-wide guarantee.

## Reconciliation Rule

GitHub Copilot may support broader configuration than this repository chooses to expose.

When that happens:

- treat GitHub Docs as the product-behavior source of truth
- treat the local repository files as the implementation-policy source of truth
- widen the local contract only when the user explicitly wants the repository standard changed

## Output Expectations

- Confirmed platform facts with source links
- Any MCP capability found and whether it was actually used
- Clear distinction between official behavior and repo-local policy
- Frontmatter or tool-contract implications for the target agent or skill
- Specific file updates required to align the repository
- Validation command to run after changes
