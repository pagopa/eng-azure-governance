---
name: internal-code-review
description: Use when a code review is requested, a PR needs reviewing, or the user wants defect-first checks or safe simplification guidance across functionality, security, performance, maintainability, and tests on Python, Bash, Terraform, Java, or Node.js/TypeScript.
---

# Code Review Skill

## When to use

- Perform an exhaustive, nit-level code review on Python, Bash, Terraform, Java, or Node.js/TypeScript files.
- Provide structured findings with per-language anti-pattern detection.
- Complement specialist reviewer agents with deep language-specific checks.

## Standalone quick start

When this skill is used directly instead of through `internal-review-guard`, establish these inputs first:

- the review question or requested scope
- the changed files or diff being reviewed
- the validation already run and the main evidence gaps that remain

Then produce:

- findings grouped by severity
- a file path and line reference for every finding
- a short residual-risk or unverified-area summary

## Context checklist

Establish these review inputs before grading the diff:

- What behavior, requirement, or defect is the change trying to address?
- Which files, tests, or runtime paths carry the change?
- Are there rollout, backward-compatibility, or migration constraints?
- What is the expected validation path, and what is still unverified?

## Severity levels

| Level | Meaning | Action |
|---|---|---|
| `Critical` | Security flaw, data loss risk, or correctness bug | Must fix before merge |
| `Major` | High-risk maintainability issue or deviation from mandatory rules | Should fix before merge |
| `Minor` | Improvement that reduces technical debt or improves clarity | Fix recommended |
| `Nit` | Style inconsistency, naming preference, or cosmetic issue | Fix optional but encouraged |
| `Notes` | Assumptions, open questions, or follow-up suggestions | Informational only |

## Escalation rules

- Any single anti-pattern repeated three or more times in the same diff escalates one severity level (e.g., `Nit` → `Minor`, `Minor` → `Major`).
- Any deviation from the matching `instructions/*.instructions.md` is at minimum a `Nit`.
- Any violation of `security-baseline.md` is at minimum a `Major`.

## Anti-pattern catalogs

Per-language catalogs with ID-tagged patterns, severity, rationale, and good/bad examples are in `references/`:

- `references/anti-patterns-python.md` — PY-C01..PY-N06
- `references/anti-patterns-bash.md` — SH-C01..SH-N05
- `references/anti-patterns-terraform.md` — TF-C01..TF-N05
- `references/anti-patterns-java.md` — JV-C01..JV-N04
- `references/anti-patterns-nodejs.md` — ND-C01..ND-N04

Load the relevant catalog(s) based on file extensions detected in the diff.

## Cross-language checks

These apply regardless of language:

| Severity | Check |
|---|---|
| `Critical` | Hardcoded secrets, tokens, passwords, or API keys |
| `Major` | Missing input validation on external inputs |
| `Major` | Missing error handling on I/O operations |
| `Minor` | Non-English comments, logs, or error messages |
| `Minor` | TODO/FIXME/HACK without linked issue or ticket |
| `Nit` | Trailing whitespace or inconsistent EOF newlines |

## Review lenses

Always cover these dimensions, even when the language-specific catalog is the primary tool:

- Functionality: correctness, edge cases, failure handling, and requirement fit
- Security: input validation, secret handling, privilege boundaries, unsafe interpolation, and dependency risk
- Performance: unnecessary loops, repeated work, hot-path regressions, or avoidable I/O
- Tests: meaningful coverage, edge-case coverage, and whether the validation actually exercises the changed behavior
- Maintainability: naming, cohesion, complexity, dead code, and local convention fit

## Simplification rubric

When the review also asks whether the change can be simplified safely, use this rubric and keep every recommendation behavior-preserving:

- Reuse: prefer an existing helper or shared abstraction over new near-duplicate logic.
- Quality: flag redundant state, parameter sprawl, copy-paste branches, and stringly-typed values when a stronger local contract already exists.
- Efficiency: flag repeated work, duplicate reads, unnecessary recomputation, and overly broad scans that add cost without benefit.
- Clarity: flag deep nesting, weak naming, dead code, redundant comments, and indirection that no longer earns its keep.

Only elevate simplification suggestions when they materially improve maintainability, correctness, or cost. Do not churn code for aesthetic reasons alone.

## Review workflow

1. **Identify languages and changed surfaces** in the diff (auto-detect from file extensions and changed paths).
2. **Read enough nearby context** to understand intent, requirements, and test strategy before judging style or structure.
3. **Load applicable anti-pattern catalogs** from `references/`.
4. **Scan each changed file** against the relevant catalog.
5. **Cross-check the review lenses** for functionality, security, performance, tests, and maintainability.
6. **Self-question each finding**: Is this really wrong, or am I misunderstanding the context? Could the author have a valid reason?
7. **Apply escalation rules** for repeated violations.
8. **Group findings** by severity: `Critical` → `Major` → `Minor` → `Nit` → `Notes`.
9. **Include file path and line reference** for every finding.
10. **Suggest a concrete fix** or reference the "good" example for each finding.
11. **Summarize** total finding count per severity at the end.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Flagging style issues as Major | Dilutes urgency of real problems | Use severity mappings strictly |
| Reviewing only the diff without reading surrounding context | Missing that the "bad" pattern is intentional for backward compat | Read 20-30 lines before/after each change |
| Skipping the requirements or test strategy first | You can flag a deliberate tradeoff as a defect | Establish the context checklist before scoring findings |
| Applying Python rules to Bash or vice versa | Different idioms, different expectations | Always check the file extension first |
| Reporting "missing tests" without checking if tests exist elsewhere | False findings erode trust | Search for test files before flagging |
| Skipping cross-language checks | Secrets and validation gaps cross all languages | Always run the cross-language table |
| Generic "this could be improved" without concrete fix | Not actionable | Every finding must include a fix suggestion |

## Cross-references

- **internal-change-impact-analysis** (`.github/skills/internal-change-impact-analysis/SKILL.md`): for change-set-level impact analysis, architectural evaluation, and blind-spot detection beyond line-level review.
- Use both together: this skill for nit-level anti-patterns first, then `internal-change-impact-analysis` for the bigger picture.

## Delegation

Use this skill as the default review owner, then add a narrower specialist only when the evidence demands it.

- Stay with `internal-code-review` when the main need is defect-first review across mixed Python, Bash, Terraform, Java, or Node.js changes.
- Add `internal-terraform` when the review is primarily about Terraform resource modeling, module interfaces, or drift-safe HCL changes.
- Add `antigravity-golang-pro` when the review is primarily about Go concurrency, service design, or Go performance behavior.
- Add `awesome-copilot-codeql` when the review is primarily about CodeQL workflow setup, SARIF handling, or query-suite coverage rather than the diff itself.
- Add `awesome-copilot-secret-scanning` when the review is primarily about GitHub-native secret scanning, push protection, alert handling, or blocked-push remediation.
- Add language or domain specialists only when they materially improve the finding quality; do not fan out by default.

## Validation

- Verify every finding references a real file path and line from the diff.
- Verify severity assignments match the anti-pattern catalog rules.
- Verify escalation rules are applied for repeated violations (3+ of the same kind).
- Verify cross-language checks are applied regardless of primary language.
