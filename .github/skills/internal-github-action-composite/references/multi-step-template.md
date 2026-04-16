# Multi-Step Composite Template

Use this starter when a composite action must validate input, share state across steps, and expose a caller-visible output.

```yaml
name: Package Directory
description: Validate input, create an archive, and expose the archive path
inputs:
  source-directory:
    description: Directory to package
    required: true
outputs:
  archive-path:
    description: Archive path for later workflow steps
    value: ${{ steps.bundle.outputs.archive-path }}
runs:
  using: composite
  steps:
    - name: Validate source directory
      shell: bash
      env:
        SOURCE_DIRECTORY: ${{ inputs.source-directory }}
      run: |
        set -euo pipefail
        if [[ ! -d "$SOURCE_DIRECTORY" ]]; then
          echo "source-directory does not exist: $SOURCE_DIRECTORY" >&2
          exit 1
        fi
        echo "SOURCE_DIRECTORY=$SOURCE_DIRECTORY" >> "$GITHUB_ENV"
    - name: Define archive path
      id: bundle
      shell: bash
      run: |
        set -euo pipefail
        archive_path="$RUNNER_TEMP/source.tgz"
        echo "archive-path=$archive_path" >> "$GITHUB_OUTPUT"
        echo "ARCHIVE_PATH=$archive_path" >> "$GITHUB_ENV"
    - name: Create archive
      shell: bash
      run: |
        set -euo pipefail
        tar -czf "$ARCHIVE_PATH" -C "$SOURCE_DIRECTORY" .
```

Keep the shape intentional:

- use `$GITHUB_ENV` for intra-action state and `$GITHUB_OUTPUT` for caller-visible data
- give output-producing steps stable `id` values
- extract longer build or deploy logic into a script once the action becomes orchestration-heavy
