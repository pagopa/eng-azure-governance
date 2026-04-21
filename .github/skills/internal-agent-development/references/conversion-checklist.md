# Agent Conversion Checklist

Use this checklist when converting an upstream agent or agent-authoring pattern into a repository-owned internal agent.

## Preserve

1. Keep the underlying decision model or workflow value.
2. Keep distinct routing boundaries that still matter in this repository.
3. Keep output shape only when users benefit from that structure.
4. Keep discovery logic only when it changes decisions, not when it is generic interviewing.

## Rewrite

1. Rename into the canonical internal contract: `internal-<name>.agent.md`.
2. Rewrite the `description:` so it explains when the internal agent should be selected.
3. Normalize copied tool catalogs to canonical aliases and declare an explicit `tools:` contract for the internal agent.
4. Replace stale runtime-specific tool assumptions with repository-local files, skills, validators, or current GitHub Copilot frontmatter.
5. Convert expertise lists into routing rules, role focus, or output expectations.
6. Convert multi-step command flows into `## Execution Workflow` only when recurring orchestration is core to the role.

## Remove

1. Retired frontmatter such as `infer:` and unsupported decoration such as `color:`.
2. UI-only metadata, slash-command syntax, or platform-specific tool catalogs.
3. Marketing language, prestige claims, or generic "world-class expert" phrasing.
4. Historical context that no longer affects routing or governance.
5. Technology encyclopedias that belong in a skill or reference instead of an agent body.

## Decide

1. If most of the value is reusable procedure, strengthen or create a skill instead.
2. If the imported role overlaps a current internal agent, merge or narrow the route.
3. If one imported agent spans unrelated roles, split or extract instead of keeping a kitchen-sink rewrite.
4. If the output stays vague after cleanup, the routing contract is still wrong.

## Final Checks

1. Confirm optional frontmatter is still supported by current GitHub Copilot docs and that the internal agent declares `tools:` with canonical aliases or MCP namespaces.
2. Confirm the agent says when not to use it.
3. If the agent is a direct owner rather than a coordinator, confirm it recommends other owners without actively routing or handing off.
4. Confirm output expectations are observable.
5. Confirm the imported pattern no longer depends on stale runtime behavior or obsolete tool ids.
6. Run repository validation before finishing.
