---
description: Use when authoring or revising repository-owned Copilot agents; owns boundary clarity, paired-asset coherence, and minimal duplication.
applyTo: ".github/agents/internal-*.agent.md,.github/agents/local-*.agent.md"
excludeAgent: "cloud-agent"
---

# Agent Authoring Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify agent intent, scope, and boundaries are explicit and non-overlapping.
- Flag routing or escalation language that conflicts with canonical owner contracts.
- Check for duplicated procedural depth that should live in a paired skill or reference.
- Verify referenced prompts and skills exist and names match exactly.
- Report stale capability claims that are not supported by repository assets.
- Check for ambiguous handoff wording that can cause lane confusion.
- Verify constraints and safety language are clear, testable, and evidence-based.
