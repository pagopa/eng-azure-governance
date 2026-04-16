# Action README Template

Use this template when a composite action needs a minimal, repeatable consumer contract.

````md
# <action-name>

One sentence on what the action does and what it does not do.

## Inputs

| Name | Required | Description |
| --- | --- | --- |
| `source-directory` | Yes | Directory to package. |

## Outputs

| Name | Description |
| --- | --- |
| `archive-path` | Archive path produced by the action. |

## Side effects

- Writes an archive under `$RUNNER_TEMP`.
- Requires `tar` on the runner.

## Example

```yaml
steps:
  - uses: ./.github/actions/<action-name>
    with:
      source-directory: dist
```

## Compatibility notes

- Existing input and output names remain stable within a major release.
- Document breaking changes and migration steps in release notes.
````
