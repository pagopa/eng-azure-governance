# Azure Retirement Intelligence Context

This context names the repository concepts used to collect, normalize, aggregate, and publish Azure retirement evidence for committee review.

## Language

**Retirement evidence**:
An Azure-published Advisor or Service Health record that supports review of a retiring service or feature.
_Avoid_: inferred impact, executive conclusion

**Raw artifact**:
The TSV output that preserves source-specific Advisor or Service Health observations before aggregation.
_Avoid_: aggregate, slide

**Aggregate artifact**:
The normalized TSV that groups retirement evidence and retains source and traceability fields.
_Avoid_: raw artifact, publication

**Slide artifact**:
The ordered committee-facing TSV projection of the aggregate artifact.
_Avoid_: PowerPoint, executive merged table

**Publication window**:
The inclusive period from `as_of_date` through twelve calendar months after that date used to select current retirement evidence.
_Avoid_: query window, reporting period

**Resource resolution**:
The process of associating a Service Health event with resources using Azure-published evidence sources.
_Avoid_: name matching, inferred impact

**Degraded mode**:
An explicitly enabled run mode that retains bounded evidence and diagnostics when permitted subscription or query failures occur.
_Avoid_: successful run, silent fallback
