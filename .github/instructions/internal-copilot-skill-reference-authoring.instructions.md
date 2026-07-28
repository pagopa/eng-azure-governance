---
description: Use when editing internal/local skill references; owns deep reusable detail without duplicating paired agent or SKILL.md contracts.
applyTo: ".github/skills/internal-*/references/**/*.md,.github/skills/local-*/references/**/*.md"
excludeAgent: "cloud-agent"
---

# Skill Reference Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify reference content extends, but does not duplicate, the paired SKILL.md contract.
- Flag contradictions between reference guidance and owning skill boundaries.
- Check links and cross-file references resolve to existing repository paths.
- Report stale procedures, retired owners, or invalid validation commands.
- Verify reusable guidance is concrete, scoped, and free of unnecessary narration.
- Check naming and terminology consistency with the owning skill family.
- Flag guidance that belongs in policy owners rather than deep references.
