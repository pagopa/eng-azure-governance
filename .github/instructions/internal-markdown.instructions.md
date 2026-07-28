---
description: Markdown standards for concise, maintainable documentation and explicit command/path formatting.
applyTo: "**/*.md"
excludeAgent: "cloud-agent"
---

# Markdown Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Use the bundle checker for high-confidence structural findings: MD011 for
  reversed links, MD042 for empty links, MD051 for invalid fragments, MD052
  for undefined references, and MD053 for duplicate or unused references.
- Check fences, local links/fragments, paths, reference definitions, and
  heading structure without treating a Markdown dialect as universal.
- Record dialect awareness when CommonMark, GitHub Flavored Markdown, or a
  tool-specific extension changes the interpretation.
- Separately review technical claims, commands, paths, and examples against
  repository evidence; report stale references, contradictory guidance, or
  behavior presented as enforced without support from code, tests, or validators.
- Report duplicated policy only when its canonical owner is evident. Leave
  external targets, editorial judgment, and broader policy ownership to their owners.
