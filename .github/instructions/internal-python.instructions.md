---
description: Python standards for both scripts and application code with DDD boundaries, guard clauses, and pytest defaults.
applyTo: "**/*.py"
excludeAgent: "cloud-agent"
---

# Python Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify guard clauses and error handling make failure modes explicit.
- Flag unsafe input handling, shell invocation, or filesystem side effects.
- Check function and module boundaries for readability and cohesion.
- Flag behavioral configuration buried in helpers, services, or library modules instead of centralized at the correct boundary: a script entrypoint, `Configuration` section, settings module, adapter, application factory, or composition root.
- Do not flag stable domain invariants merely because they are constants near domain code.
- Verify type hints and public interfaces stay consistent with call sites.
- Flag manual formatting churn that fights the repository formatter; when Ruff is configured, prefer `ruff format` and Ruff diagnostics over subjective style edits.
- Report dependency usage that is unpinned, unnecessary for the change, or unjustified for the data volume and import or install cost.
- Flag vendored libraries, wheelhouses, copied site-packages, or fallback dependency mirrors.
- Preserve the repository-declared dependency manager. For pip requirements, require exact pins and hashes in the owning requirements file; for another declared dependency manager, require its canonical lock artifact and frozen or locked validation command.
- When behavior changes, verify docs and output contracts stay aligned: filenames, produced artifacts, columns, and other user-visible output details must match reality.
- Check tests for deterministic coverage of changed behavior.
- Flag test setup that bypasses the repository's shared runner, pytest rootdir or testpaths contract, or declared interpreter or virtualenv setup without a reproducibility reason.
- Flag logging or exception messages that may leak sensitive values, raw request or response bodies, or secrets.
