# Code Review Instructions

## Objective

- Protect the business: find defects, security flaws, and maintainability risks before they reach production.
- Keep findings concise, severity-ordered, and tied to concrete evidence.
- Preserve requested behavior first, then improve security, maintainability, and simplicity.
- Never write review output to files unless the user explicitly asks. All output goes in chat.

## Self-questioning protocol

Every review must include self-questioning:

- Assign a confidence level to every finding: **High**, **Medium**, or **Low**.
- For **Low** confidence findings, explain what context might be missing that could invalidate the finding.
- After producing all findings, re-examine the top 3 most severe ones and ask: "Could this be intentional? Am I sure? Is my suggested fix actually simpler?"
- If self-questioning changes your assessment, update the finding or downgrade its severity.
- Include a brief "Self-questioning notes" section at the end with any revised assessments.

## Priority order

Apply this priority to all reviews:

1. **Correctness** — Does it do what it claims?
2. **Security** — Secrets, injection, privilege, unsafe operations.
3. **Simplicity** — Is this the simplest thing that could work?
4. **Maintainability** — Will this be easy to change in 6 months?

## Review output format

- `Critical`: must-fix issues such as security flaws, correctness bugs, or data-loss risk.
- `Major`: high-risk improvements such as mandatory rule violations, unsafe defaults, or missing validation.
- `Minor`: worthwhile improvements that reduce technical debt or clarify intent.
- `Nit`: style, naming, or small convention inconsistencies.
- `Notes`: assumptions, follow-ups, or scope clarifications.

Every finding must include:

- Severity and confidence level.
- File path and line reference.
- What is wrong and why it matters (impact on business or operations).
- Concrete fix suggestion.

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
- Use `.github/skills/internal-code-review/SKILL.md` as the detailed anti-pattern catalog for Python, Bash, and Terraform.
- Do not inline long language-specific catalogs when the `code-review` skill is available.

## Focus by area

- Terraform: drift risk, lifecycle safety, variable typing, plan readability, provider pinning, and cloud-specific IAM patterns.
- Workflows: SHA pinning, minimal permissions, environment protection, OIDC, and deterministic checks.
- Scripts: input validation, early returns, readable control flow, and English logs.
- Python: type hints, testing, dependency management, script vs application separation.
- Bash: `set -euo pipefail`, quoting, traps, `command -v`, debuggability.
- Java: null safety, resource management, test coverage, unnecessary abstractions.
- Node.js: async safety, unhandled rejections, dependency hygiene, event loop awareness.
- Copilot customization assets: reusable wording, naming consistency, and low-noise token usage.

## Minimum language guardrails

- Python: flag hardcoded secrets, `eval()`/`exec()`, unsafe `pickle`, bare `except`, `shell=True`, and missing tests for new logic.
- Bash: flag hardcoded secrets, `eval`, unsafe temp files, missing `set -euo pipefail`, unquoted variables, and missing dependency checks.
- Terraform: flag hardcoded secrets, wildcard IAM, missing state-locking expectations, unpinned providers, and hardcoded environment-specific identifiers.
- Java: flag hardcoded secrets, SQL injection, unsafe deserialization, unchecked resource leaks, and missing tests.
- Node.js: flag hardcoded secrets, prototype pollution, unhandled rejections, `eval`/`Function()`, and missing tests.
