---
description: Composite-action-specific standards that extend the GitHub Actions baseline with input validation and safe shell patterns.
applyTo: "**/actions/**/action.y*ml"
excludeAgent: "cloud-agent"
---

# Composite Action Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify all required inputs are validated before use in shell or tooling steps.
- Flag unsafe interpolation, unquoted expansions, or command injection opportunities.
- Check step outputs are deterministic and documented through explicit IDs.
- Verify referenced actions are pinned and not using mutable tags.
- Report missing failure handling for critical setup or cleanup paths.
- Check environment and path mutations for scope leaks across steps.
- Flag undocumented breaking changes in input or output contracts.
