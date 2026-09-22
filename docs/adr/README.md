# Architecture Decision Records

This directory records repository-wide architectural decisions and the evidence behind them.

No diagram is provided because this index records decisions rather than a component or execution flow.

## Contents

- [ADR index](#adr-index)
- [Local format](#local-format)
- [Status and supersession](#status-and-supersession)
- [Validation](#validation)

## ADR index

- [ADR-0001: Use a four-domain repository context map](0001-domain-layout.md) - accepted 2026-09-01.

## Local format

- Store records as `NNNN-<slug>.md` and assign the next unused number.
- Start the title with `# ADR-NNNN:` followed by the decision title.
- Record `Status`, `Date`, `Deciders`, and `Related` metadata in that order.
- Use `Context and Problem Statement`, `Domain Evidence`, `Decision Drivers`, `Considered Options`, and `Decision Outcome` in that order.
- Add consequences and option analysis only when they preserve material trade-offs.

## Status and supersession

Statuses are `proposed`, `accepted`, `rejected`, `deprecated`, or `superseded by ADR-NNNN`.
An accepted ADR body is immutable. A changed accepted decision requires a new numbered ADR, a link in both records, and the old record's status changed to `superseded by ADR-NNNN`.

## Validation

Check that every record follows the local file, metadata, status, and
supersession rules before accepting it. Resolve the index links from this
directory and run the repository documentation checks when they are available.
