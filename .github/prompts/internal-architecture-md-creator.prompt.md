---
name: "internal-architecture-md-creator"
agent: "agent"
description: "Generate or refresh docs/architecture.md (canonical AI architecture contract) for any repository, evidence-based, repo-shape agnostic"
argument-hint: "Optional target repository path; optional focus, constraints, language. Retained artifacts are English."
---

<!-- markdownlint-disable-file MD041 -->

Target repository (path or name; default = current repository root):
${input:repository:Repository path or name. Leave empty to target the current repository root. Provide one per line if running over multiple repos sequentially.}

Optional focus areas:
${input:focus:Optional focus such as runtime flow, IaC layout, CI/CD, testing, security boundaries, monorepo split, AI-agent risk surface}

Optional constraints or exclusions:
${input:constraints:Optional non-negotiables, prior architectural decisions to preserve, ADRs to honor, sections to skip}

Output language:
${input:language:Match chat language for the chat reply only. Retained artifact content, headings, tables, and filenames must stay in English.}

Use these standards-repository sources first for evidence discipline, planning posture, and challenge gating:

- [AGENTS.md](../../AGENTS.md)
- [.github/copilot-instructions.md](../copilot-instructions.md)
- [.github/INVENTORY.md](../INVENTORY.md)
- [.github/agents/internal-planning-leader.agent.md](../agents/internal-planning-leader.agent.md)
- [.github/agents/internal-critical-master.agent.md](../agents/internal-critical-master.agent.md)
- [.github/skills/internal-writing-plans/SKILL.md](../skills/internal-writing-plans/SKILL.md)

Then produce an evidence-based architecture contract for the target repository with the rules below.

## 1. Mission

Create or refresh, for the target repository, one artifact:

- `<repo>/docs/architecture.md` — canonical, concise, evidence-based architecture contract for AI agents and human maintainers.

The canonical contract must describe the architecture that is actually present in the repository, not a marketing pitch and not a theoretical proposal.

## 2. Repository Resolution

1. Resolve `repository` to a real path in the current workspace. If empty, use the current repository root.
2. If ambiguous or missing, stop and ask only for the unresolved repository.
3. Verify presence on disk using terminal listing (do not rely on editor search alone — `tmp/` and `.gitignore` paths can hide files from the indexer).
4. If multiple repositories are listed, treat each independently. Do not synthesize a cross-repo architecture.

## 3. Mandatory Pre-Analysis Control Pass

Before writing the canonical artifact, confirm on disk:

- Repository root and top-level layout.
- Presence or absence of: `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/`, `docs/`, `docs/architecture.md`, `README.md`, `Makefile`, language manifests (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, …), IaC roots (`*.tf`, `bicep/`, `cloudformation/`, `pulumi/`, `terragrunt.hcl`), CI workflows (`.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml`), test roots (`tests/`, `test/`, `__tests__/`, `spec/`).
- Whether the repo is a **monorepo** (multiple independent roots, numbered prefixes such as `00-`, `10-`, per-service folders, multiple IaC roots, multiple language manifests at top level).
- Existing ADRs, architecture notes, design docs, or standards files to align with and reference.

If `docs/architecture.md` already exists, treat it as the prior canonical version: refresh it in place, preserve still-true claims, and downgrade unsupported claims to `Unknown / To verify` or remove them when evidence contradicts them.

## 4. Operating Rules

1. Inspect the repository before writing.
2. Prefer evidence from source code, configs, tests, workflows, package manifests, IaC files, scripts, and existing docs.
3. Do not invent missing architecture. If unclear, mark `Unknown / To verify`.
4. Do not modify application code, IaC, tests, workflows, or scripts.
5. Create or update only `docs/architecture.md`.
6. Do not modify `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/*`, or `.github/prompts/*` unless the user explicitly asks. Suggest exact snippets instead.
7. Do not store the canonical contract under `.github/`. Keep `.github/` as the activation/instruction layer.
8. Keep the canonical document concise; avoid full file trees and implementation trivia.
9. Favor stable architectural rules over temporary details.
10. Align with existing ADRs/README architecture notes/design docs when present and reference them. Do not auto-create ADRs.
11. If the repository is a monorepo, do not fabricate a single unified architecture. Document the root architecture and call out whether per-service architecture files are needed.
12. Do not expose secret values. Reference only variable names, file names, and high-level handling patterns.
13. Repo-shape agnostic: do not assume a specific language, framework, cloud provider, IaC tool, or even the existence of `src/` or `tests/`. Adapt sections to actual evidence.
14. Do not create `tmp/superpowers/architecture-analysis.md` or any other secondary retained analysis artifact unless the user explicitly asks for one.

## 5. Evidence Model

Classify important architectural claims as one of:

- `Documented`: explicitly stated in existing docs, ADRs, README, configuration, or comments.
- `Evidenced`: directly visible from source code, config, tests, workflows, IaC, or scripts.
- `Inferred`: reasonable conclusion from multiple repository signals, but not explicitly documented.
- `Unknown`: not enough evidence.

Important claims include: module/component boundaries, dependency direction, runtime flow, deployment flow, ownership of responsibilities, validation commands, architectural constraints, risky areas for AI edits.

For `Documented`, `Evidenced`, and `Inferred`, include source paths.

## 6. Analysis Steps

1. Repository purpose: main responsibility, primary users/consumers, main inputs and outputs.
2. Technology stack: languages, frameworks, runtime, build/package, test, IaC/deploy, automation.
3. Repository structure: important folders and what each owns; generated/vendor/test/docs/ops/config/workflow areas.
4. Architectural boundaries: domains/modules/components, public interfaces, internal areas, shared utilities, infrastructure/adapters, test/support layers.
5. Dependency direction: which modules may depend on which; layering rules visible from code or config; what to avoid.
6. Key flows: runtime/CLI/job/worker flow if present; CI/CD; build/test/release; IaC/Terraform/Bicep/Pulumi flow if present; GitHub Actions or other CI flow.
7. Configuration and environment: required env vars/config files, secrets handling pattern, local dev assumptions, deployment assumptions, cloud/provider assumptions.
8. Testing and validation: main commands, test types, what to run after common changes, known gaps.
9. AI-agent modification risks: safe vs risky places to change, files/modules not to refactor casually, when to update docs/tests, when to ask for human review, when to stop and report a conflict.

## 7. Internal Analysis Discipline

Perform the analysis steps before writing `docs/architecture.md`, but do not create a separate retained analysis file.

Keep the working analysis internal and use it only to:

- decide what belongs in each canonical section;
- decide which claims are `Documented`, `Evidenced`, `Inferred`, or `Unknown`;
- identify the top risks and unknowns to surface in section 14 and in the final chat response;
- apply the `internal-critical-master` consistency gate before finalizing the canonical document.

Do not include private chain-of-thought in the chat. Surface only concise evidence-backed outcomes.

## 8. Required Canonical Output

Create or refresh `<repo>/docs/architecture.md` with the following 14 sections. Keep section numbering and titles stable so AI agents can rely on them.

```md
# Architecture

## 1. Purpose

## 2. System overview

## 3. Current vs intended architecture

| Area | Current architecture | Intended architecture | Status | Evidence |
| --- | --- | --- | --- | --- |

## 4. Technology stack

| Area | Technology | Status | Evidence |
| --- | --- | --- | --- |

## 5. Repository map

| Path | Responsibility | Notes |
| --- | --- | --- |

## 6. Architectural boundaries

## 7. Dependency rules

### Allowed direction

### Avoid / forbidden

## 8. Key flows

### Runtime flow

### Build/test flow

### Deployment/operations flow

## 9. Configuration and environment

## 10. Testing and validation

| Change type | Suggested validation | Evidence |
| --- | --- | --- |

## 11. Architectural decisions visible in the repo

## 12. AI-agent working rules

## 13. Last verified

- Date: YYYY-MM-DD
- Agent/tool:
- Files inspected: summary only
- Commands considered/run:
- Confidence: High / Medium / Low

## 14. Unknown / To verify
```

Section content rules:

- Section 2: 5-10 lines. Include an ASCII diagram only if it makes the architecture clearer.
- Section 3: use `Intended architecture` only when explicitly documented; do not present technical debt as intentional design.
- Section 5: include only important paths. No full trees.
- Section 6: for important claims include `Status` and `Evidence`.
- Section 7: if not enough evidence, write `Unknown / To verify`.
- Section 8: include only flows supported by repository evidence. Skip subsections that have no evidence and call them out in section 14.
- Section 9: never expose secret values.
- Section 11: format each item as:
  - Decision: ...
    - Status: Documented / Evidenced / Inferred / Unknown
    - Evidence: `path`
    - Trade-off: ...
    - Related ADR: `path`, if present
- Section 12 baseline (adapt wording, keep intent):
  - Read this file before structural, cross-file, or refactoring changes.
  - Prefer existing repository patterns over new abstractions.
  - Keep changes scoped to the user request.
  - Do not introduce new frameworks, global conventions, or cross-cutting refactors without explicit approval.
  - Do not change module boundaries, dependency direction, runtime flows, deployment flows, or validation commands without updating this file.
  - If a requested change conflicts with this architecture, explain the conflict before editing.
  - Do not treat this file as immutable. If the change intentionally updates architecture, propose the document update explicitly.
  - For risky changes, produce a short plan before modifying files.

## 9. Monorepo Handling

If the pre-analysis control pass identified a monorepo:

- Keep `docs/architecture.md` at the repository root, scoped to the monorepo-level architecture.
- Section 5 must list each top-level service/component root and its responsibility.
- Section 6 must describe inter-component boundaries, not internal per-service detail.
- Section 14 must explicitly state whether per-service `docs/architecture.md` files are recommended.
- Do not create per-service files automatically.

## 10. Activation Snippets to Suggest

After creating the files, suggest these snippets only if the target file already exists or would clearly benefit from it. Do not edit those files.

### Suggested `AGENTS.md` snippet

```md
Before structural, cross-file, or refactoring changes, read `docs/architecture.md` and treat it as the source of truth for repository boundaries, dependency direction, key flows, validation commands, and AI-agent working rules.

If the requested change conflicts with `docs/architecture.md`, explain the conflict before editing. If the change intentionally updates the architecture, propose the required architecture document update explicitly.
```

### Suggested `.github/copilot-instructions.md` snippet

```md
For architectural, cross-file, or refactoring tasks, consult `docs/architecture.md` before editing. If the request conflicts with documented boundaries, dependency rules, key flows, or validation commands, explain the conflict first.
```

### Optional `.github/instructions/architecture.instructions.md` snippet

```md
---
applyTo: "**/*"
---

For structural, cross-file, or refactoring changes, use `docs/architecture.md` as the repository architecture contract. Keep changes scoped, preserve documented boundaries, and update the architecture file when intentional architectural changes are made.
```

Suggest the optional file only if `.github/instructions/` already exists in the repo or path-specific Copilot instructions would clearly help.

## 11. Quality Bar

`docs/architecture.md` must be:

- accurate, concise, evidence-based;
- useful to both humans and AI agents;
- stable enough to survive normal implementation changes;
- short enough to be referenced frequently;
- specific enough to reduce AI-driven drift and unsafe refactors.

Length targets:

- Single-purpose repository: 150-250 lines.
- Monorepo or unusually broad scope: may exceed 250 but must stay under a hard maximum of 400 lines.
- No secondary retained analysis artifact should be created unless explicitly requested by the user.

Markdown hygiene (must pass markdownlint defaults):

- Spaced table separators: `| --- | --- |`, never `|---|---|`.
- Trailing newline at end of file (MD047).
- One H1 per file.
- No fabricated headings beyond the 14 canonical sections.

## 12. Final Consistency Gate (internal-critical-master)

Before finalizing the canonical document, run a brief internal pressure-test using the `internal-critical-master` lens:

- What in the candidate canonical document is most likely correct given on-disk evidence?
- What may be overclaimed, contradictory, or hallucinated, and must be downgraded to `Unknown / To verify`?
- Are any sections forcing structure where evidence does not exist (for example claiming a runtime flow on a pure IaC repo)?
- Is the monorepo decision honest, or is a unified architecture being faked?
- Does section 12 promise constraints the repo cannot actually enforce?

Reconcile the answers before writing the final document:

- Preserve the strongest supported claims with evidence.
- Trim unsupported claims or move them to section 14 (`Unknown / To verify`).
- Reflect any downgrade decisions directly in `docs/architecture.md`, especially in sections 3, 7, 8, 11, 13, and 14 as appropriate.
- Do not route to another lane; this is an internal validation step inside this prompt.

## 13. Final Response Shape

After creating or updating the files, respond with:

1. The created/updated file paths.
2. A short summary of the architecture discovered.
3. The top 3 risks or unknowns found.
4. Whether `AGENTS.md` and `.github/copilot-instructions.md` already exist in the target repo.
5. The suggested snippets to add to those files (only the ones that apply).
6. Commands considered or run for validation.
7. The Critical-Master gate outcome in one or two lines: what was kept, what was downgraded.

Do not paste the full `docs/architecture.md` in the chat unless explicitly requested.
