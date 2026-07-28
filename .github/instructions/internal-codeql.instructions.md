---
description: CodeQL review checks for workflow correctness, query coverage, and secure SARIF reporting.
applyTo: "**/.github/codeql/**/*.yml,**/.github/codeql/**/*.yaml,**/.github/workflows/*codeql*.yml,**/.github/workflows/*codeql*.yaml"
excludeAgent: "cloud-agent"
---

# CodeQL Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag language matrices or workflow coverage that omit active repository languages.
- Flag query suite configuration that weakens expected security coverage.
- Flag missing, incorrect, or unsafe SARIF upload wiring in scanning workflows.
- Flag action references that are not pinned to immutable SHAs.
- Flag scan-job permissions that exceed least-privilege or miss required security-events scope.
- Flag build-mode or init/analyze sequencing issues that can invalidate scan results.
