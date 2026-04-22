---
name: internal-script-python
description: Use when creating or modifying standalone Python scripts, CLIs, or small operator-facing toolkits whose primary contract is direct execution rather than reusable package or application code.
---

# Python Script Skill

Follow `.github/instructions/internal-python.instructions.md` for the baseline Python rules. This skill adds standalone-script guidance only.

## When to use

- New standalone Python scripts.
- Existing Python scripts that need updates.
- CLI tools, one-off automation, data processing.
- Small multi-entrypoint toolkits whose primary contract is operator-facing execution rather than reusable package APIs.

## Boundary

- This skill covers standalone operational tools, CLI entrypoints, and small script toolkits whose primary contract is direct execution.
- A tool does not become application code just because it has multiple files, a `lib/` folder, or root-level tests.
- Move out of this lane only when the primary contract becomes imported behavior, service boundaries, or framework-owned flows.

## Script-specific guidance

- Standalone tools should default to a dedicated folder or toolkit root, not a loose top-level `.py` file.
- Keep entrypoints thin: parse arguments, resolve paths, orchestrate helpers, and return an exit code through `main() -> int` plus `raise SystemExit(main())`.
- Prefer `argparse`, `pathlib.Path`, and small helper functions for operator-facing tools.
- Keep emoji logs at operator-facing boundaries such as start, success, warning, and failure states; keep reusable helpers free of decorative log formatting.
- When a tool can be called from subdirectories, resolve the repository root explicitly instead of assuming the current working directory.
- Use type hints on non-trivial public helpers and CLI-facing boundaries.
- Use `asyncio` only when the script truly coordinates multiple I/O-bound tasks.
- Reach for `pathlib`, context managers, and small helper functions before adding framework-like structure to a script.
- Add machine-readable output such as `--format json` only when the tool has a real automation consumer. Keep text output as the default operator path.

## Dependency decision note

When the instruction owner requires a dependency decision note, keep it short, for example:

```text
Dependency decision note
- Candidates: argparse (stdlib), click, typer
- Final choice: typer
- Why: cleaner CLI structure, less boilerplate, better help output, and less custom parsing code than argparse for this script.
```

- Keep the note short and task-specific.
- Compare the standard library with realistic third-party candidates.
- If the final choice uses external libraries, create or update the local `requirements.txt` before finishing the task.
- If several entrypoints share the same lock file, record the decision once at the shared toolkit `requirements.txt` rather than repeating it in every script.

## Layout and templates

Load `references/layout-and-templates.md` when you need the default folder layout, a repo-aligned multi-tool toolkit layout, a minimal entry point, a hash-locked `requirements.txt`, or the launcher pattern.

Keep these rules visible while drafting:

- Use a dedicated tool folder or toolkit root rather than a loose top-level `.py` file.
- Add `requirements.txt` and `run.sh` only when external packages are actually needed.
- Generate `requirements.txt` with `pip-compile --generate-hashes` or an equivalent locked workflow.
- Reuse an existing shared runner such as `.github/scripts/run.sh` instead of cloning bootstrap logic into every entrypoint.
- Mirror script or toolkit coverage under the repository-root `tests/` tree; do not create ad-hoc test folders beside the tool.

## Testing

- Follow the repository pytest defaults from the instruction owner.
- Use coverage reports to inspect missing behavior on touched code, not to force blanket 100% coverage.
- For modify tasks: edit implementation first, run existing tests, then update tests only for intentional behavior changes.
- Prefer existing repository commands such as `make lint`, `make test`, or a shared script runner before inventing a one-off validation path.

## Runtime guidance

- Prefer direct, readable orchestration over framework-like structure.
- Keep shared helpers local to the toolkit, not promoted into application-style layering without a real need.
- Centralize repeated environment bootstrap in one shared runner instead of copying `.venv` and `pip install` logic into every wrapper.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Missing `if __name__ == "__main__":` guard | Script runs on import, breaks testing and reuse | Always guard the entry point |
| Using `print()` for errors | Errors go to stdout, mixed with normal output | Use `print(..., file=sys.stderr)` or `logging` |
| Bare `except:` or `except Exception:` at top level | Swallows all errors including KeyboardInterrupt | Catch specific exceptions; let unexpected ones propagate |
| Hardcoded file paths | Non-portable across machines | Use `argparse`, `pathlib`, or environment variables |
| No argument parsing | Caller has to modify script source to change behavior | Use `argparse` for any configurable parameter |
| Installing deps globally or without hash-locked version pinning | Non-reproducible environment and hidden setup drift | Keep dependencies in the local `requirements.txt` with exact pins and hashes |
| Adding an empty `requirements.txt` to a stdlib-only tool | Adds noise and implies missing setup steps | Omit `requirements.txt` when the script uses only the standard library |
| Wrapping a stdlib-only script in Bash | Adds setup indirection without solving a real dependency problem | Document direct `python3 <script>.py` execution and skip the wrapper |
| Shipping a loose `.py` file with undocumented setup steps | Users must guess how to run the tool safely | Generate a self-contained folder and add `run.sh` plus `requirements.txt` only when external packages are needed |
| Treating a multi-entrypoint toolkit as app code just because it has `lib/` and tests | Pushes script tooling into the wrong guidance lane | Keep it in `internal-script-python` when the primary contract is still direct execution |
| Copying the same `.venv` bootstrap and dependency install code into every wrapper | Maintenance drift and inconsistent operator behavior | Use one shared `run.sh` and let thin wrappers delegate to it |
| Assuming the tool will always run from the repository root | Breaks when operators call it from subdirectories or nested paths | Resolve the repo root from an explicit `--root` or path argument when needed |
| Adding JSON output without a real machine consumer | Increases surface area and maintenance cost | Keep text output first and add `--format json` only when automation needs it |
| Defaulting to stdlib without comparing mature libraries | Leaves avoidable boilerplate, edge cases, and custom parsing logic in the script | Write the dependency decision note first and choose the option that makes the final code simpler |
| Rejecting a useful dependency just to keep dependency count low | Optimizes the wrong thing and increases custom code | Optimize for simpler final code and justified value, not dependency minimization |
| Forcing async or framework abstractions into a simple tool | Raises complexity without improving the script | Keep the script synchronous and direct unless concurrency is essential |

## Validation

- `python -m py_compile <script_name>.py` (syntax check)
- `bash -n run.sh` (launcher syntax check, only when `run.sh` exists)
- `pytest tests/` (run tests)
- `python -m compileall <changed_paths>` or the repository's canonical shared runner when the tool already lives inside a maintained toolkit
