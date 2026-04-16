# Deprecation Policy

## Purpose
Define a predictable process for deprecating Copilot customization assets (`instructions`, `skills`, `agents`, and templates).

## Lifecycle states
- Active: recommended for current use.
- Deprecated: still available but scheduled for removal.
- Removed: no longer maintained or supported.

## Required process
1. Mark the asset as deprecated in its file header or first section.
2. Record the change in `.github/CHANGELOG.md` with migration guidance.
3. Keep a minimum deprecation window of one release cycle (or 30 days if no release cycle exists).
4. Provide a replacement asset when possible.
5. Remove only after the window ends and no blocking consumers remain.

## Backward compatibility rules
- Instructions: avoid changing mandatory behavior without documenting impact.
- Skills: keep old skill path available during transition.
- Agents: keep objective and restriction semantics stable where possible.

## Emergency exception
Immediate removal is allowed only for security or compliance issues. The removal reason must be documented in `.github/CHANGELOG.md`.

## Current deprecations
- `.github/skills/antigravity-domain-driven-design/SKILL.md`: **Removed**. Consolidated into `.github/skills/internal-ddd/SKILL.md`.
- `.github/skills/internal-data-registry/SKILL.md`: **Removed**. Retired from the live catalog after confirming no remaining live references.
- `scripts/bootstrap-copilot-config.sh`: **Removed**. Replaced by the `internal-sync-global-copilot-configs-into-repo` agent and the `internal-agent-sync-global-copilot-configs-into-repo` skill workflow.
- `skills/internal-terraform-feature/SKILL.md`: **Removed**. Merged into `skills/internal-terraform/SKILL.md`.
- `skills/internal-terraform-module/SKILL.md`: **Removed**. Merged into `skills/internal-terraform/SKILL.md`.
