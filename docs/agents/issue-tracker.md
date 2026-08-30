# Issue tracker: Local Markdown

Issues and specs live locally as markdown files. No remote issue tracker
operations are used.

## Conventions

- One feature per directory: `tmp/.issues/<feature-slug>/`
- The spec is `tmp/.issues/<feature-slug>/spec.md`
- Issues are `tmp/.issues/<feature-slug>/issues/<NN>-<slug>.md`
- Triage state uses a `Status:` line near the top of each issue
- Comments append under a `## Comments` heading

Publish and fetch work under `tmp/.issues/`. Wayfinder uses
`tmp/.wayfinder/<analysis-slug>/`, with `map.md` and numbered child tickets
under `issues/`.
