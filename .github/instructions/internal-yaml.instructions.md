---
description: YAML formatting and clarity conventions for stable, maintainable configuration files.
applyTo: "**/*.yml,**/*.yaml"
excludeAgent: "cloud-agent"
---

# YAML Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Run the bundle-owned checker for syntax and the `key-duplicates` rule before
  reporting automated findings.
- Check indentation, tabs, scalar styles, block scalar/chomping behavior, and
  encoding at the format boundary.
- Review anchors/aliases and merge behavior for explicit, portable intent.
- Treat schema/tag routing as a handoff to the owning platform or domain
  instruction; generic YAML validity is not schema validation.
- Separately review secret exposure, runtime-changing values,
  environment-scope leaks, and domain-policy changes when the changed file
  provides evidence.
- Keep those review-only findings distinct from parser findings and route
  schema-specific conclusions to the owning platform or domain instruction.
