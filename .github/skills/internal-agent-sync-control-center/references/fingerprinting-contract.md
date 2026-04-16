# Fingerprinting Contract

Use this reference when a sync or audit workflow needs deterministic proof that a managed resource changed.

## Purpose

The goal is not to hash files for its own sake. The goal is to reduce false positives and avoid unsafe refresh decisions.

Use fingerprinting when one or more of these are true:

- a managed asset family is large enough that visual diff review is slow
- upstream refreshes are frequent and noisy
- the workflow needs a retained manifest to compare two runs
- the same comparison logic would otherwise be rewritten ad hoc

Do not add or keep manifests when they provide no real safety benefit.

## Manifest Schema

Each resource entry should follow this shape:

```json
{
  "resource_id": "openai/skills/doc",
  "target_path": ".github/skills/openai-docx/SKILL.md",
  "source_ref": "https://github.com/openai/skills/tree/main/skills/.system/doc/SKILL.md",
  "kind": "skill",
  "normalization_version": "v1",
  "hash_algo": "sha256",
  "source_hash": "raw-bytes-hash",
  "content_hash": "normalized-content-hash",
  "metadata": {
    "mapped_name": "openai-docx"
  }
}
```

Manifest-level fields should include:

- `generated_at`
- `root`
- `normalization_version`
- `hash_algo`
- `resources`

## Output Paths

Use these defaults consistently:

- skill-scoped temporary evidence: `tmp/superpowers/internal-agent-sync-control-center.manifest.json`
- other ad hoc fingerprint outputs for this workflow: under `tmp/superpowers/`
- canonical repository sync manifest written by the repo sync flow: `.github/copilot-sync.manifest.json`

Do not treat files under `tmp/` as catalog policy or durable governance state.

## Normalization Rules

For `v1`, normalize text conservatively:

1. convert `CRLF` and `CR` to `LF`
2. strip trailing whitespace from each line
3. collapse repeated trailing blank lines
4. ensure exactly one final newline

Do not reorder sections, markdown bullets, or frontmatter keys in `v1`. Treat order as meaningful until the repository intentionally adopts a stronger canonicalization rule.

## Kind Detection

Infer `kind` from the path when possible:

- `.github/skills/*/SKILL.md` -> `skill`
- `.github/agents/*.agent.md` -> `agent`
- `.github/instructions/*.instructions.md` -> `instruction`
- fallback -> `file`

## Real Change vs Noise

Interpret manifest diffs this way:

- different `source_hash` and different `content_hash`: real content change
- different `source_hash` and same `content_hash`: normalization-only noise
- same `source_hash` and same `content_hash`: unchanged

Treat `normalization-only` as a signal to review the pipeline, not as a default reason to refresh the managed asset.

## Suggested Workflow

1. Generate a baseline snapshot into `tmp/`.
2. Generate a candidate snapshot after refresh or fetch.
3. Diff the two manifests.
4. Use the diff report to decide whether `apply` is justified.

## Bundled Script

Use `scripts/sync_resource_fingerprint.py` for:

- snapshot generation
- normalized hashing
- manifest diffing

Keep the skill contract here and the deterministic execution logic in the script.
