# ADR-0002: Use glossary file names for domain vocabulary

* Status: accepted
* Date: 2026-10-14
* Deciders: Repository owner
* Related: [ADR-0001](0001-domain-layout.md), [glossary map](../../GLOSSARY-MAP.md), [domain documentation](../agents/domain.md)

## Context and Problem Statement

ADR-0001 records the four-domain set through a root `CONTEXT-MAP.md` and one `CONTEXT.md` per context. The upstream domain-modeling convention followed by the repository's engineering skills now names these files `GLOSSARY-MAP.md` and `GLOSSARY.md` and keeps glossaries limited to definitions. The accepted ADR-0001 body cannot be edited, so its file names need a recorded successor.

## Domain Evidence

| Evidence | Finding |
| --- | --- |
| `docs/adr/0001-domain-layout.md` | The accepted decision names `CONTEXT-MAP.md` as the root map. |
| Upstream domain-modeling glossary format | The convention uses `GLOSSARY.md`, `GLOSSARY-MAP.md`, a `## Language` section, and relationships only in the map. |
| `docs/domain/*/GLOSSARY.md` | The four context glossaries already use the `## Language` format with bold terms and `_Avoid_` entries. |

## Decision Drivers

* Keep repository vocabulary files on the convention the engineering skills read.
* Preserve the accepted four-domain set and its evidence.
* Avoid leaving an accepted ADR that names files the repository no longer has.

## Considered Options

* Keep `CONTEXT-MAP.md` and `CONTEXT.md` as legacy names.
* Rename the files to `GLOSSARY-MAP.md` and `GLOSSARY.md`, recording the change in a new ADR.

## Decision Outcome

Chosen option: "Rename the files to `GLOSSARY-MAP.md` and `GLOSSARY.md`, recording the change in a new ADR", because the domain set is unchanged and only the file names follow the upstream convention.

This decision supersedes only the file names in ADR-0001. The four-domain set, its evidence, and its relationships remain accepted. `docs/domain/cross-context/GLOSSARY.md` resolves terms whose meaning differs between contexts; it is listed in the map but is not a domain.
