---
name: awesome-copilot-secret-scanning
description: Configure GitHub secret scanning, push protection, custom secret patterns, blocked-push remediation, and alert handling. Use when enabling secret scanning, tuning detection, handling leaked credentials, or designing pre-commit secret controls around GitHub Advanced Security.
---

# Secret Scanning

Use this skill for GitHub-native secret detection and remediation workflows.

## Primary Scenarios

- Enable repository or organization secret scanning
- Turn on push protection
- Design custom secret patterns
- Resolve blocked pushes safely
- Triage or dismiss alerts with audit-quality reasoning

## Workflow

1. Enable scanning and push protection in the right scope.
2. Keep exclusions narrow and documented.
3. Rotate real secrets first; history rewrite comes second.
4. Use dismiss reasons precisely.
5. Keep false-positive tuning separate from real-secret remediation.

## Guardrails

- Do not treat bypass as the default path.
- Removing exposure from history is not a substitute for credential rotation.
- Broad exclusions weaken both alerting and push protection.
- Use custom patterns only when provider patterns and non-provider detection are not enough.

## What to Produce

- Enablement steps
- Safe remediation path
- Optional bypass or delegated-bypass guidance
- Pattern or exclusion examples only when necessary
