# Copilot Audit Checklist

Use this reference when the audit needs detailed flagging criteria instead of only the high-level audit order.

## What To Flag

### Frontmatter integrity

Flag an asset when:

- a repository-owned skill or agent does not start with a valid YAML frontmatter block
- YAML parsing fails, so route and metadata checks are no longer trustworthy
- review discussion is focusing on wording even though structural metadata is already broken

### Hollow assets

Flag an asset when:

- it references `resources/` or `references/` files that do not exist
- it tells the model to invoke skills or agents that are not installed
- it depends on assistant-runtime features not supported by the repository target

### Decorative skill contracts

Flag an asset when:

- it declares a skill but never assigns it a concrete workflow role
- it keeps a broad toolbox-style skill list without routing or trigger boundaries
- it treats a skill as available context rather than an expected procedure

### Tool contract problems

Flag a repository-owned internal agent when:

- it omits `tools:` and therefore relies on implicit all-tools access instead of the repository's explicit tool-contract policy for internal agents
- its prompt or routing rules depend on explicit least-privilege or MCP-only behavior, but the frontmatter never declares the corresponding `tools:` or `mcp-servers:` contract
- it copies legacy product-specific tool ids such as `terminalCommand`, `search/codebase`, `search/searchResults`, `search/usages`, `edit/editFiles`, `execute/runInTerminal`, `web/fetch`, or `read/problems` when canonical aliases such as `execute`, `search`, `edit`, `web`, or `read` would express the intent more clearly
- it names MCP tools without `server/tool` or `server/*` namespacing
- it carries a long copied tool catalog even though a short canonical alias list would be clearer

Current GitHub Copilot custom agents allow omitted `tools:` and would then expose all available tools, but repository-owned internal agents in this repository must not rely on that implicit fallback.

Do not flag legacy tool catalogs inside imported non-`internal-*` assets unless the task is explicitly to refresh, replace, or fork that import.

### Retired patterns

Flag an asset when it still contains:

- `infer:`
- `color:`
- runtime-specific wording that should have been normalized to GitHub Copilot terminology

Do not flag `tools:` or `model:` by themselves. Current GitHub Copilot custom agents support both.

### Overlap problems

Flag a pair or group when:

- one asset is a weaker alias of another
- one asset is a workflow bundle built from missing dependencies
- one asset broadens trigger space without adding real capability
- a new internal asset fully supersedes an upstream one

### Skill route quality

Flag a repository-owned skill when:

- `description:` reads like a capability summary or mini workflow instead of a trigger
- `description:` mixes too many adjacent domains or quietly widens the lane with "helpful" wording
- the body widens the boundary beyond what the description should own
- a wrapper skill replays a full upstream workflow instead of enforcing the local gate and pointing to the right references

### Token-shape drift

Flag a repository-owned skill when:

- static lookup tables, starter templates, or taxonomies stay inline even though `references/` would carry them cleanly
- new scripts were added mainly to hold static guidance rather than deterministic repeated execution
- shared owner maps or canonical checklists are copied into multiple wrappers instead of one canonical owner
- a long body is being treated as a problem even though there is no retrieval drift, maintenance drift, or duplicated guidance

### Bridge problems

Flag `AGENTS.md` when:

- it duplicates large sections from `.github/copilot-instructions.md`
- it claims a runtime that should remain abstract
- it routes to agents that do not exist
- its inventory references files that are gone

### Governance review gaps

Flag a sync workflow when:

- it does not report whether `.github/copilot-instructions.md` and root `AGENTS.md` were reviewed
- it marks work as `apply` even though governance review was skipped
- it proceeds to `apply` while `blocking` findings remain

## Flagging examples

- `blocking` / `Patch`: a skill references a missing file under `references/`, so the documented workflow cannot actually be loaded.
- `non-blocking` / `Patch`: `AGENTS.md` still inventories a path that was deleted from `.github/`.
- `non-blocking` / `Keep`: two assets are adjacent in topic area, but their descriptions and trigger boundaries remain distinct.
- `blocking` / `Replace`: a repository-owned internal asset fully supersedes a weaker local fallback that still broadens trigger space.
