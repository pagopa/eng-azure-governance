# Internal Agent Contract Reference

Use this reference when editing frontmatter, tool scope, engine-skill sections, or subagent controls for repository-owned agents.

## Frontmatter Contract

- GitHub Copilot custom agents currently support `name`, `description`, `target`, `tools`, `model`, `disable-model-invocation`, `user-invocable`, `agents`, `handoffs`, `hooks`, `argument-hint`, `mcp-servers`, and `metadata` in frontmatter.
- `handoffs`, `hooks`, and `argument-hint` are VS Code only; GitHub.com ignores them.
- Repository-owned internal agents must keep `name:` aligned with the filename stem exactly.
- Repository-owned agents that are intentionally non-internal may keep a different `name:` only when route, origin, or compatibility requires it.
- Repository-owned internal agents must use the canonical filename pattern `internal-<agent-name>.agent.md`.
- `description:` is the routing contract and should start with `Use this agent when ...`.
- Keep `name:` and `description:` even though current GitHub Copilot treats `name:` as optional.
- Repository-owned internal agents must declare `tools:` explicitly. Do not rely on implicit all-tools access for internal agents in this repository.
- Add optional frontmatter only when it materially changes environment behavior, selection behavior, or execution model.
- When `tools:` is present, prefer canonical aliases such as `read`, `edit`, `search`, `execute`, `agent`, and `web`, plus explicit MCP namespaces such as `github/*`, `playwright/*`, `server/tool`, or `server/*`.
- Keep `tools:` short and role-shaped instead of copying kitchen-sink catalogs.
- Do not cargo-cult legacy tool ids such as `terminalCommand`, `search/codebase`, `search/searchResults`, `search/usages`, `edit/editFiles`, `execute/runInTerminal`, `web/fetch`, or `read/problems`.
- Use `target:` only when the agent should behave differently between GitHub.com and IDE environments.
- Use `mcp-servers:` only when the agent truly needs agent-local MCP server configuration.
- Prefer `disable-model-invocation` and `user-invocable` over retired `infer:`.
- Never use `color:`.
- Do not depend on `argument-hint`, `handoffs`, or `hooks` for GitHub.com compatibility.

## Skill Section Contract

- When an internal agent depends on repo-owned skills as its required operating engine, add `## Mandatory Engine Skills`.
- Treat `## Mandatory Engine Skills` as a repository-owned contract for the skill or skills that must be loaded before the agent's core routing or decision logic runs.
- Keep mandatory engines short and role-defining. One shared engine or one shared plus one existing tactical engine is normal.
- `## Optional Support Skills` is optional. Use it only when it materially improves routing clarity, discovery, or command-center usability.
- Prefer `## Optional Support Skills` over `## Preferred/Optional Skills` for current internal contracts.
- Use `## Optional Support Skills` only for conditional support skills, not for the required engine.
- When present, a skill-list section is a curated routing and discovery list. List exact canonical skill identifiers, one per bullet, in backticks.
- Do not present a skill-list section as a native GitHub Copilot property or as a guarantee that every listed skill will be invoked automatically.
- When expressing the resource model, treat `obra-*` as the cross-cutting workflow lane, `internal-*` as the canonical repository-owned layer, imported skills as support depth by default, and `local-*` as consumer-local extensions. Do not infer strategic, tactical, or operational role from prefix alone.
- Do not create a 1:1 dedicated skill per agent just for symmetry. Create an engine skill only when it owns real reusable logic that would otherwise bloat the agent or drift.
- Router agents are the strongest default candidate for a dedicated engine skill because their classification matrix, fallback rules, and ownership mapping are highly procedural.

## Delegation And Invocation Controls

- Only router agents should own active downstream routing logic. Canonical non-router agents should recommend a better owner to the user instead of routing on the user's behalf, unless a narrower scoped contract explicitly allows them to invoke `internal-router` as a second parallel lane while leaving downstream owner selection to the router.
- When an agent should dispatch to specific subagents, declare `agents:` with the explicit list of allowed targets.
- When an agent must not dispatch subagents, declare `agents: []` to enforce the recommendation-only boundary.
- When an agent should only be accessible as a subagent and not appear in the user dropdown, set `user-invocable: false`.
- When an agent should never be invoked as a subagent by other agents, set `disable-model-invocation: true`.
- Use `handoffs` only for user-visible sequential transitions, not for autonomous within-turn delegation.
- Load `references/subagent-patterns.md` when designing coordinator/worker orchestration or restricting subagent access.

## Body Contract

- Every agent must explain both positive routing and at least one meaningful boundary.
- Every agent must define `## Output Expectations`.
- Add `## Skill Usage Contract` only when the agent is a broader command center whose listed skills are used conditionally.
- When `## Skill Usage Contract` is present, explain selection criteria and boundaries, not a blanket execution order.
- When an agent can influence external actions, call out where human approval or review gates apply.
- Keep long reusable workflows in skills, not in the agent body.

## Platform Verification Gate

- Before claiming that a frontmatter property is supported, unsupported, deprecated, or behaves in a specific way, verify against the live official documentation.
- Load `internal-copilot-docs-research` and `.github/skills/internal-copilot-docs-research/references/official-source-map.md` to identify the authoritative page.
- Open the authoritative page for the surface involved: VS Code custom agents, GitHub.com custom agents, or subagents.
- If the live docs contradict the current assumption, stop and tell the user what changed before proceeding.
- If the docs are unreachable, state explicitly that the platform claim is unverified and proceed with caution.
- This gate applies whenever the change depends on platform behavior: frontmatter fields, tool aliases, subagent invocation, MCP integration, or environment-specific feature support.
- This gate does not apply when the work is purely repo-local convention with no platform-behavior dependency.
