# AGENTS.md - Repository Operating Core

`AGENTS.md` is the always-on, portable policy baseline for coding agents. Keep
it generic enough to reuse in any repository; keep repository-specific rules in
`AGENTS.local.md` and specialized guidance with the nearest owner.

## Precedence And Scope

- Direct user instructions win for the current task unless they require unsafe,
  destructive, or impossible behavior.
- Apply the smallest relevant owner. Narrower, target-specific rules override
  broader defaults when they conflict.
- Use only policy that exists on disk. Removed files, generated output,
  historical aliases, and past automation are not active policy.

## Working Agreement

- Identify the target, nearest owner, bounded evidence, and validation path
  before broad reading or commands.
- Match tool depth to task scope. A local naming or configuration question must
  not trigger repository-wide analysis.
- For a question limited to known files, paths, components, or file types, inspect
  the smallest relevant set directly with targeted commands such as `rg --files`
  and `sed`. Honor explicit scope limits and do not invoke graphify.
- Use graphify when the answer requires broad architecture discovery, relationships
  across repository areas, dependency or data-flow tracing, or finding an unknown
  component or call path. The local-scope fast path takes precedence over broader
  tool triggers.
- Proceed directly for deterministic, low-risk work. Align with the user before
  non-trivial, ambiguous, architectural, policy, contract, or multi-step changes.
- Make the smallest change that fixes the controlling issue. Preserve user work
  and avoid unrelated refactors.
- Keep one active primary owner per execution lane. That owner retains material
  decisions and final acceptance; load narrower owners only when evidence shows
  they are needed.
- For non-trivial work, state the target state, anti-scope, assumptions,
  tradeoffs, and validation path before implementation or handoff.
- Reason from repository evidence. Do not invent runtimes, validators, sync
  flows, tests, or policy.
- Downshift for policy-only work. When the target state is a small declared
  policy change in known files, use only the nearest owner, the mandatory
  test-first guardrail, the repository's change-scope validation, and adjacent
  tests. Load graphify, critical review, brainstorming, or external research
  only on concrete ambiguity or contradiction.
- On a dirty working tree, snapshot the initial state, declare the task file
  allowlist, and run targeted checks before global ones. Classify global
  failures outside the allowlist as pre-existing; do not reopen
  implementation for them.
- Before the final answer, re-read the changed files from the working tree
  and compare them with the claims made in the answer. Do not report checks,
  content, or behavior that the final state does not contain.

## Placement And Authoring

- Keep detailed procedures, checklists, file-shape recipes, command playbooks,
  and tool-specific workflows in their owning skills or files.
- Use Plain Technical English for repository-owned prose unless a narrower owner
  explicitly overrides it. Prefer short sentences, stable terms, active voice,
  and explicit `must`, `should`, and `may` wording.
- Keep required technical names unchanged.
- Place native tests with the component and runner that own the behavior. Use
  repository-root `tests/` only for real non-native or cross-boundary behavior.
- Treat `tmp/` as disposable support. Do not commit its contents.

## Validation And Delivery

- Route executable or evaluable behavior changes through a test-first workflow
  before implementation. Define or update the failing check before the fix.
- Name the closest executable validation early. Run it after the change and
  report unavailable checks or evidence gaps explicitly.
- When policy or a contract changes, align its owning tests, validators, and
  documentation so stale checks cannot restore the old behavior.
- Treat prose as guidance, not enforcement. Put hard guarantees in permissions,
  validators, hooks, or CI.

### Human-Facing Responses

- A direct user-requested format or an applicable skill-owned output contract
  controls the response layout, required fields, ordering, length, visual use,
  and machine-readable shape. Apply the following defaults only where that
  narrower contract is silent.
- Do not invent a cross-skill response template. When a skill owns the
  response, use that skill's specialized projection and preserve its field
  order. The root policy is only a fallback for work with no narrower owner.
- Keep analysis, review, diagnosis, comparison, report, and handoff responses
  concise and proportional. Preserve material blockers, risks, uncertainty,
  validation gaps, and the next required action in the locations defined by
  the owning skill.
- For non-trivial flows, sequences, dependencies, ownership models, state
  transitions, or multi-part comparisons, strongly prefer the smallest useful
  Mermaid diagram when it communicates the relationship faster and more
  clearly than prose alone. Skip decorative or redundant visuals. Preserve the
  diagram's controlling conclusion in adjacent text so the response remains
  useful when Mermaid is not rendered.
- Keep full evidence and decision history in an existing retained artifact when
  one already owns that detail. Use the human-facing response for the outcome,
  material delta, risk, and next action. Do not create an artifact solely to
  shorten the response.

## Protected Skill Boundary

- Imported or third-party skill bundles are protected and read-only by default.
  Where a repository uses origin prefixes, treat bundles whose names do not
  start with `internal-` or `local-` as protected.
- Invocation, wrapping, synchronization, dependency, or perceived necessity
  never implies authorization to edit a protected skill.
- Only an explicit instruction in the current user conversation naming the
  exact protected skill or path authorizes an edit.
- Authorization is limited to the requested files and purpose and does not
  carry into later turns.
- An unapproved protected-skill finding is a stop condition; do not create an
  allowlist to bypass it.

## graphify

For any question about this repo's architecture, structure, components, or how to add/modify/find
code, your first action should be `graphify query "<question>"` when `graphify-out/graph.json`
exists. Use `graphify path "<A>" "<B>"` for relationship questions and `graphify explain "<concept>"`
for focused-concept questions. These return a scoped subgraph, usually much smaller than the full
report or raw grep output.

Triggers: "how do I…", "where is…", "what does … do", "add/modify a `<component>`",
"explain the architecture", or anything that depends on how files or classes relate.

If `graphify-out/wiki/index.md` exists, use it for broad navigation. Read `graphify-out/GRAPH_REPORT.md`
only for broad architecture review or when query/path/explain do not surface enough context. Only read
source files when (a) modifying/debugging specific code, (b) the graph lacks the needed detail, or
(c) the graph is missing or stale.

Type `/graphify` in Copilot Chat to build or update the graph.

## Optional Repository-Local Policy

If `AGENTS.local.md` exists next to this file, load and apply it after this
baseline. If it does not exist, continue without error.
