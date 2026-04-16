# Caching and Artifacts

Use cache for reproducible dependency reuse across runs. Use artifacts for explicit handoffs or human review between jobs.

| Need | Prefer | Why |
| --- | --- | --- |
| Restore dependency state across runs | Cache | Keyed reuse is automatic and disposable |
| Pass reviewed output to another job or stage | Artifact | Named handoff with retention and download semantics |
| Keep logs or plans for human inspection | Artifact | Retention and download are part of the contract |

## Deterministic cache example

```yaml
- name: Cache npm data
  # actions/cache@v5.0.4
  # https://github.com/actions/cache/releases/tag/v5.0.4
  uses: actions/cache@668228422ae6a00e4ad889ee87cd7109ec5666a7
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      npm-${{ runner.os }}-
```

Use stable inputs like lockfiles, tool versions, or build configuration. Do not use timestamps or raw `github.run_id` in cache keys.

When a cache path needs a runner-scoped location such as `runner.temp`, resolve it in a step key that allows the `runner` context. Do not put `runner.temp` in workflow-root `env` or `jobs.<job_id>.env`.

## Runner temp cache example

```yaml
- name: Restore pre-commit cache
  # actions/cache@v5.0.4
  # https://github.com/actions/cache/releases/tag/v5.0.4
  uses: actions/cache@668228422ae6a00e4ad889ee87cd7109ec5666a7
  with:
    path: ${{ runner.temp }}/pre-commit-cache
    key: pre-commit-${{ runner.os }}-${{ hashFiles('.pre-commit-config.yaml') }}

- name: Use cached path in a shell step
  env:
    PRE_COMMIT_CACHE_DIR: ${{ runner.temp }}/pre-commit-cache
  run: |
    mkdir -p "${PRE_COMMIT_CACHE_DIR}"
    echo "Using cache at ${PRE_COMMIT_CACHE_DIR}"
```

## Artifact handoff example

```yaml
- name: Upload reviewed plan
  # actions/upload-artifact@v7.0.1
  # https://github.com/actions/upload-artifact/releases/tag/v7.0.1
  uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
  with:
    name: terraform-plan-${{ github.sha }}
    path: plan.tfplan
    retention-days: 7
    if-no-files-found: error

- name: Download reviewed plan
  # actions/download-artifact@v8.0.1
  # https://github.com/actions/download-artifact/releases/tag/v8.0.1
  uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c
  with:
    name: terraform-plan-${{ github.sha }}
    path: ./artifacts
```

Keep artifact usage explicit:

- name artifacts for the exact handoff they represent
- set `retention-days` deliberately instead of inheriting defaults
- upload only reviewed or reusable outputs, not hidden mutable state
- prefer job outputs or reusable workflows when the handoff is small and immediate
