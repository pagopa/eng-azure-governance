# Deprecation Policy

## Purpose
Define a predictable process for deprecating Copilot customization assets (`instructions`, `prompts`, `skills`, `agents`, and templates).

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
- Prompts: avoid renaming/removing slash commands without replacement mapping.
- Instructions: avoid changing mandatory behavior without documenting impact.
- Skills: keep old skill path available during transition.
- Agents: keep objective and restriction semantics stable where possible.

## Emergency exception
Immediate removal is allowed only for security or compliance issues. The removal reason must be documented in `.github/CHANGELOG.md`.

## Current deprecations
- None at this time.
