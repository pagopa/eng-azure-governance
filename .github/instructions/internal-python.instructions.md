---
description: Python standards for both scripts and application code with DDD boundaries, guard clauses, and pytest defaults.
applyTo: "**/*.py"
---

# Python Instructions

## Mandatory rules

- Use emoji logs for key operator-facing execution states.
- Prefer early return and clear guard clauses.
- Keep code explicit and readable.
- Prefer simple, readable, and easily modifiable code over clever abstractions.
- Unit tests are required for testable logic.
- Python tests must live under the repository-root `tests/` directory, never beside source files or inside standalone tool folders.
- Mirror the covered source path under `tests/` so the owning script or module is obvious from the test location.
- Apply these rules for both create and modify operations.
- For Python template tasks, use Jinja templates named `<file-name>.<extension>.j2`.
- Keep template content complete and externalize only values intentionally passed by the caller.
- Add type hints on public or non-trivial function signatures.
- Follow PEP8 and keep line length <= 120.
- Docstrings, logs, exceptions, and CLI output must be in English.
- For new scripts that may need external packages, write a short dependency decision note comparing the standard library with realistic third-party candidates before coding.
- If external libraries are introduced, lock them in `requirements.txt` with exact pins and hashes.
- Do not add local vendored libraries, wheelhouses, copied site-packages, fallback dependency mirrors, or deprecated alternate dependency paths unless explicitly requested.

## Use the right Python skill

- Load `.github/skills/internal-project-python/SKILL.md` for structured package or application code, reusable library boundaries, async judgment, and application test shape.
- Load `.github/skills/internal-script-python/SKILL.md` for standalone operational tools, toolkit layout, launcher rules, dependency choices, and script runtime orchestration.
- Keep this instruction as the shared auto-loaded baseline; keep the standalone-tool versus structured-package workflow detail in the paired skills.
- Treat `excludeAgent` frontmatter differentiation as a follow-up optimization for this instruction family, not a default requirement. GitHub Docs still document `excludeAgent` for path-specific instructions; re-check the supported agent values before rolling it out here.

## Dependency lock example

Keep pinned requirements readable when the target script uses external packages:

```text
# requests 2.32.3
requests==2.32.3 \
    --hash=sha256:<hash1> \
    --hash=sha256:<hash2>
```

- Generate the locked file with `pip-compile --generate-hashes` or an equivalent workflow that captures the full dependency closure.

## Minimal skeleton

```python
#!/usr/bin/env python3
"""Purpose: Explain what this script does.

Usage examples:
  python3 ./script.py --help
"""
```

## Minimal test example

```python
def test_example() -> None:
    assert 1 + 1 == 2
```
