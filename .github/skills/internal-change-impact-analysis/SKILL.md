---
name: internal-change-impact-analysis
description: Use when the user wants to understand the ripple effects of a change, identify architectural risks in a changeset, review cross-cutting concerns before merge, or needs a holistic pre-merge impact assessment beyond line-level review.
---

# Change Impact Analysis Skill

## When to use
- Analyze a set of repository changes (branch diff, PR, or file list) for correctness, design, and blind spots.
- Evaluate architectural implications and unconsidered aspects of a change.
- Complement line-level code review with systems-level and business-level thinking.

## Relationship to other skills
- **internal-code-review** (`.github/skills/internal-code-review/SKILL.md`): per-line anti-patterns, severity catalogs, nit-level scanning.
- **This skill**: change-set-level impact, architectural implications, unconsidered aspects.
- Use both together: run `internal-code-review` first for detailed findings, then this skill for the bigger picture.

## Analysis dimensions

Dimensions are loaded from `references/analysis-dimensions.md` when deeper checklists are needed. Summary:

1. **Correctness** — Does the code do what the change claims? Edge cases? Error paths? Input validation?
2. **Separation of concerns** — Business vs I/O? Module boundaries? Naming clarity? Dependency direction? Interface stability?
3. **Architecture** — Coupling, cohesion, extensibility, testability, operational readiness?
4. **Blind spots** — Temporal analysis, team dynamics, cross-service impact, operational burden, data implications, security surface, performance cliffs, configuration drift, missing observability, alternative solutions?

## Severity mappings

| Category | Severity | Criteria |
|---|---|---|
| Error | Critical | Security flaw, data loss risk, correctness bug affecting business logic |
| Error | Major | Missing error handling, broken contract, regression risk |
| Improvement | Readability | Code clarity, naming, structure |
| Improvement | Performance | Algorithmic efficiency, resource usage |
| Improvement | Maintainability | Technical debt, coupling, cohesion |
| Improvement | Testability | Test coverage gaps, untestable designs |
| Improvement | Security | Hardening, least privilege, input validation |

| Effort | Meaning |
|---|---|
| Low | Less than 1 hour, isolated change |
| Medium | 1-4 hours, may touch multiple files |
| High | More than 4 hours, may require design discussion |

## Output structure

Present findings directly in conversation (never write files unless the user explicitly asks):

1. **Summary** — 2-4 sentences on what changed and overall assessment.
2. **Errors and defects** — Objectively wrong things with fix suggestions.
3. **Improvement opportunities** — Working code that can be better, with effort estimates.
4. **Open questions** — Ambiguous areas requiring author clarification.
5. **Blind spots** — Things the change does not address but should.
6. **Architecture notes** — Non-binding structural guidance (advisory only).

For empty sections, state "No findings in this category."

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Flagging code style as an architectural issue | Inflates findings, dilutes trust | Use `internal-code-review` for nit-level checks |
| Making ungrounded findings ("this might break X") | Speculation ≠ evidence | Every finding must cite a concrete file and line from the diff |
| Scope creep — analyzing the entire codebase | The user asked about a specific change | Analyze only changed files and their immediate dependencies |
| Reporting without effort estimation | Leaves the author without prioritization signal | Always include Low/Medium/High effort per finding |
| Mixing errors and improvements | Obscures urgency | Errors block merge; improvements are advisory |
| Skipping blind-spot analysis | The most valuable part of this skill gets dropped | Always run all 4 dimensions, even if some are empty |

## Self-questioning

Before presenting findings, verify:
- Is this finding based on evidence in the diff, or am I assuming?
- Could I be wrong about the intent of this change?
- Am I flagging something that is actually fine for this specific context?
- What is the simplest correct interpretation?

## Workflow

1. Identify changed files (diff against default branch or explicit file list).
2. Load applicable instruction files based on detected languages.
3. Read each changed file and its immediate dependencies.
4. Analyze across all dimensions (load `references/analysis-dimensions.md` for detailed checklists).
5. Self-question each finding before including it.
6. Present findings in conversation using the output structure above.

## Validation
- Every finding must reference a concrete file and line number.
- Every finding must include a *why* explanation.
- Every error or improvement must include a *how to fix* suggestion.
- Architecture recommendations must include impact/effort assessment.
