---
name: awesome-copilot-codeql
description: Configure and troubleshoot GitHub CodeQL scanning, query suites, SARIF uploads, workflow setup, and CodeQL CLI analysis. Use when working on code scanning workflows, GitHub Advanced Security analysis, CodeQL databases, or security query execution.
---

# CodeQL

Use this skill when the task is about GitHub CodeQL setup, tuning, or troubleshooting.

## Primary Scenarios

- Authoring or reviewing `.github/workflows/codeql.yml`
- Choosing default setup versus advanced setup
- Configuring language matrices and build modes
- Running CodeQL CLI locally
- Uploading SARIF results or interpreting failures
- Tuning query suites, custom packs, or monorepo categories

## Workflow

1. Identify target languages and whether they need build steps.
2. Choose GitHub Actions or CLI execution.
3. Configure permissions and analysis scope.
4. Add query suites or packs only when the default suite is insufficient.
5. Verify results in SARIF or PR annotations.

## Guardrails

- Disable duplicate setup paths; do not keep default and advanced setup fighting each other.
- For compiled languages, validate the build mode explicitly.
- Use categories when multiple scans should coexist cleanly.
- Treat failed extraction as a configuration bug, not a cosmetic warning.

## Troubleshooting Focus

- Missing permissions
- Wrong language identifiers
- Broken build steps
- Oversized or rejected SARIF uploads
- Monorepo scans missing the intended directories
