---
description: Bash scripting standards for safe execution, guard clauses, and consistent runtime logs.
applyTo: "**/*.sh"
excludeAgent: "cloud-agent"
---

# Bash Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Flag missing strict-mode safety where script behavior depends on unchecked failures.
- Verify variable expansion, quoting, and glob usage are safe for spaces and special chars.
- Check guard clauses for required tools, files, and input arguments.
- Report command patterns that can become destructive without explicit user intent.
- Verify logs and error messages are actionable and consistent for operators.
- Flag silent failure paths, swallowed exit codes, or ignored command results.
- Check temporary-file and cleanup handling for leak and collision risks.
- Report unsafe external input use in command construction.
