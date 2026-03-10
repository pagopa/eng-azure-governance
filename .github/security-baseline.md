# Security Baseline for Copilot Customization

## Objective
Provide a portable baseline that teams can apply before enabling repository-wide Copilot customization.

## Minimum controls
- Pin all third-party GitHub Actions by full commit SHA.
- Keep `permissions` minimal in workflows (default to read-only unless write is required).
- Prefer OIDC short-lived credentials over long-lived static secrets.
- Require branch protection and pull request reviews for `.github/**` changes.
- Validate `.github/**` content in CI using `.github/scripts/validate-copilot-customizations.sh`.
- Run `shellcheck` on Bash scripts under `.github/scripts/`.

## Prompt and instruction safety
- Avoid instructions that request hidden or sensitive data.
- Prohibit plaintext tokens, keys, and passwords in examples.
- Use explicit guardrails for destructive operations.
- Require deterministic, reviewable output in prompts.

## Agent safety
- Prefer read-only agents for planning/review.
- Restrict write-capable agents to clearly scoped tasks.
- Require explicit references to policy files for security-sensitive changes.

## Change governance
- Document breaking prompt or instruction changes in `.github/CHANGELOG.md`.
- Use a deprecation window before removing prompts/skills in active use.
- Keep a rollback path for workflow and policy changes.

## Enforcement status
| Control | Status | Tool |
| --- | --- | --- |
| Third-party action SHA pinning | Automated | `validate-copilot-customizations.sh` |
| Minimal workflow permissions | Automated | `validate-copilot-customizations.sh` |
| Validate `.github/**` in CI | Automated | `github-validate-copilot-customizations.yml` |
| `shellcheck` on `.github/scripts/` | Automated | pre-commit + CI |
| Secret placeholder avoidance in prompts/examples | Partial | pre-commit hooks + review |
| OIDC over long-lived secrets | Manual review | `github-actions.instructions.md` |
| Branch protection for `.github/**` | Manual review | repository settings |
| Read-only agents as default | Manual review | agent review |
| Scoped write-capable agents | Manual review | agent review |
| CHANGELOG-based change governance | Manual review | PR review |

## Optional hardening
- Add CODEOWNERS coverage for `.github/**`.
- Add secret scanning and dependency update automation.
- Add repository rulesets for workflow and environment protection.
