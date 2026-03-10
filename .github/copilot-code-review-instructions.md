# Code Review Instructions

## Objective
- Keep findings concise, severity-ordered, and tied to concrete evidence.
- Preserve requested behavior first, then improve security, maintainability, and token efficiency.

## Review output format
- `Critical`: must-fix issues such as security flaws, correctness bugs, or data-loss risk.
- `Major`: high-risk improvements such as mandatory rule violations, unsafe defaults, or missing validation.
- `Minor`: worthwhile improvements that reduce technical debt or clarify intent.
- `Nit`: style, naming, or small convention inconsistencies.
- `Notes`: assumptions, follow-ups, or scope clarifications.

## Baseline checks
1. Security and least privilege.
2. No hardcoded secrets or credentials.
3. Consistency with repository naming and structure conventions.
4. Test coverage for testable logic.
5. Documentation updates when behavior changes (excluding `README.md` unless explicitly requested).

## Escalation rules
- Any repeated anti-pattern (3+ times in the same diff) escalates one severity level.
- Any deviation from the matching `instructions/*.instructions.md` file is at minimum a `Nit`.
- Any violation of `security-baseline.md` is at minimum a `Major`.

## Token-aware review protocol
- Load only the diff, directly related files, and the matching instruction files.
- Use `.github/skills/tech-ai-code-review/SKILL.md` as the detailed anti-pattern catalog for Python, Bash, and Terraform.
- Do not inline long language-specific catalogs when the `code-review` skill is available.

## Focus by area
- Terraform: drift risk, lifecycle safety, variable typing, plan readability, and provider pinning.
- Workflows: SHA pinning, minimal permissions, environment protection, and deterministic checks.
- Scripts: input validation, early returns, readable control flow, and English logs.
- Copilot customization assets: reusable wording, prompt/skill/agent consistency, and low-noise token usage.

## Minimum language guardrails
- Python: flag hardcoded secrets, `eval()`/`exec()`, unsafe `pickle`, bare `except`, `shell=True`, and missing tests for new logic.
- Bash: flag hardcoded secrets, `eval`, unsafe temp files, missing `set -euo pipefail`, unquoted variables, and missing dependency checks.
- Terraform: flag hardcoded secrets, wildcard IAM, missing state-locking expectations, unpinned providers, and hardcoded environment-specific identifiers.
