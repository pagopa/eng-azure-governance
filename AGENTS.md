# AGENTS.md - Repository Operating Core

`AGENTS.md` is the primary always-on repository policy entrypoint for coding
agents in this repository. Keep it compact: it should route agents to the
nearest owner, avoid duplicated guidance, and require explicit validation.

## First Move

- Identify the requested target and nearest owner before broad reading.
- Read only the evidence needed to choose the smallest valid change and check.
- Prefer the closest executable validation; report any validation gap explicitly.

## Precedence

- Direct user instructions win for the current task unless they require unsafe,
  destructive, or impossible behavior.
- Resolve conflicts with the smallest valid owner. Treat broader files as
  fallback policy, not permission to override narrower contracts.
- Do not infer active policy from removed files, generated output, historical
  aliases, or past automation unless it exists on disk and is deliberately
  reintroduced.

## User Alignment

- For small, deterministic, low-risk tasks, proceed after identifying the
  target, nearest owner, and validation path.
- For non-trivial, ambiguous, architectural, policy, contract, or multi-step
  work, align with the user before implementation.

## Operating Principles

- Think before acting. Confirm target, nearest owner, bounded evidence, and
  validation path before broad commands.
- Make surgical changes. Preserve user work, avoid unrelated refactors, and tie
  each edit to the requested outcome.
- Fix the controlling issue where practical instead of layering workarounds.
- Work toward verified outcomes. Run the closest available validation and report
  explicit gaps.

## Scope And Placement

- `AGENTS.md` owns stable repository-wide policy, precedence, tactical defaults,
  ownership boundaries, and routing anchors.
- `.github/INVENTORY.md` is the exact live inventory of the GitHub Copilot catalog.
- Do not put long operational procedures, detailed checklists, detailed
  file-shape recipes, command playbooks, or tool-specific workflows here.
- Short, globally safe best-practice defaults may live here when they improve
  baseline behavior without turning this file into a procedure manual.
- `tmp/` is temporary support only. Treat its contents as disposable working
  artifacts and do not commit files from `tmp/`.

## Authoring Defaults

- Use Plain Technical English for repository-owned prose unless a narrower owner
  explicitly overrides it.
- Prefer short sentences, stable terms, active voice, and explicit `must`,
  `should`, and `may` wording.
- Keep required technical names unchanged.

## Tactical Defaults

- Preserve compact working state across turns; avoid rebuilding full context
  unless new evidence invalidates the current state.
- Keep one active primary owner per execution lane; load narrower owners only
  when path, runtime, symptom, or validation evidence proves they are needed.
- Use bounded evidence: inspect changed sections and failing-validator context
  first, then expand only when gaps remain.
- Name the validation path early; if evidence changes it, update the working
  assumption before editing.

## Delivery And Validation

- Be extremely concise in user-facing reporting without sacrificing clarity,
  correctness, safety, required evidence, or actionable next steps. Lead with
  the outcome, omit repetition and incidental process detail, and expand only
  when requested or necessary.
- Reason from repository evidence. Do not invent runtimes, validators, sync
  flows, or tests.
- For non-trivial work, make target state, anti-scope, assumptions, tradeoffs,
  and validation path visible before implementation or handoff.
- When a contract or policy changes, align the owning tests, validators, or docs
  instead of letting stale checks restore the old behavior.

## Code Changes

- Executable or evaluable behavior changes must use a test-first
  red-green-refactor loop: define the failing check, make the smallest
  implementation edit, then rerun the focused check and closest validation.
- Place tests under repository-root `tests/` using paths that make the owning
  source or checked behavior obvious. Keep deeper layout conventions in the
  nearest owner.
- The failing check must exist before the first implementation edit unless a
  pre-code testability exception names the gap and alternate validation path.
- Tests added after implementation are regression coverage only; they must not
  be represented as test-first work.
- Exceptions are limited to prose-only docs, generated inventory, mechanical
  formatting, behavior-neutral renames, read-only validation, or explicit
  pre-code testability exceptions.
- If this gate is skipped, agents must stop, disclose the violation, establish
  the recovery path, and must not claim retroactive red-green-refactor work.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Agent skills

### Issue tracker

Issues and specs are tracked as local Markdown files under `.scratch/`. See
`docs/agents/issue-tracker.md`.

### Triage labels

Triage states use the five canonical Matt Pocock skill labels. See
`docs/agents/triage-labels.md`.

### Domain docs

Domain documentation uses a single-context layout. See `docs/agents/domain.md`.

## Optional Repository-Local Policy

If `AGENTS.local.md` exists next to this file, load and apply it after this
baseline. If it does not exist, continue without error.
