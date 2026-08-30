"""Guarded explicit correlation between Advisor and Service Health events."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass

from .retirements import SourceEvent, SourceEventKey


_BASES = frozenset({"recommendation_type_id", "advisor_recommendation_id"})


def _key(value: SourceEventKey | tuple[str, str]) -> SourceEventKey:
    return value if isinstance(value, SourceEventKey) else SourceEventKey(*value)


@dataclass(frozen=True, slots=True)
class CorrelationEdge:
    advisor_key: SourceEventKey | tuple[str, str]
    service_health_key: SourceEventKey | tuple[str, str]
    basis: str

    def __post_init__(self) -> None:
        advisor = _key(self.advisor_key)
        health = _key(self.service_health_key)
        if advisor.source != "advisor" or health.source != "service-health":
            raise ValueError("correlation edges must connect Advisor to Service Health")
        if self.basis not in _BASES:
            raise ValueError("unsupported correlation basis")
        object.__setattr__(self, "advisor_key", advisor)
        object.__setattr__(self, "service_health_key", health)


@dataclass(frozen=True, slots=True)
class CorrelationDecision:
    event_key: SourceEventKey
    status: str
    basis: str = ""
    candidate_keys: tuple[SourceEventKey, ...] = ()
    rejected_edges: tuple[CorrelationEdge, ...] = ()


@dataclass(frozen=True, slots=True)
class CorrelationResult:
    groups: tuple[tuple[SourceEvent, ...], ...]
    decisions: tuple[CorrelationDecision, ...]

    @property
    def decision_by_event(self) -> Mapping[SourceEventKey, CorrelationDecision]:
        return {decision.event_key: decision for decision in self.decisions}

    @property
    def status_by_event(self) -> Mapping[SourceEventKey, str]:
        return {key: decision.status for key, decision in self.decision_by_event.items()}

    @property
    def decision_by_group(self) -> tuple[CorrelationDecision, ...]:
        return tuple(
            next(decision for decision in self.decisions if decision.event_key == group[0].key)
            for group in self.groups
        )


def correlate_source_events(
    events: tuple[SourceEvent, ...] | list[SourceEvent],
    edges: tuple[CorrelationEdge, ...] | list[CorrelationEdge],
) -> CorrelationResult:
    """Merge only complete one-to-one explicit components.

    An ambiguous component is deliberately emitted as singleton groups. Its
    candidate keys and rejected edges remain attached to every affected event.
    """

    by_key = {event.key: event for event in events}
    if len(by_key) != len(events):
        raise ValueError("source-event keys must be unique")
    candidate_edges = list(edges)
    for advisor in events:
        if advisor.source != "advisor":
            continue
        advisor_values = {
            "recommendation_type_id": {
                str(row.get("recommendation_type_id") or row.get("advisor_recommendation_type_id") or "").strip().casefold()
                for row in advisor.records
            },
            "advisor_recommendation_id": {
                str(row.get("advisor_recommendation_id") or "").strip().casefold()
                for row in advisor.records
            },
        }
        for health_event in events:
            if health_event.source != "service-health":
                continue
            for basis in ("recommendation_type_id", "advisor_recommendation_id"):
                health_values = {
                    str(row.get(basis) or (row.get("recommendation_type_id") if basis == "recommendation_type_id" else "") or "").strip().casefold()
                    for row in health_event.records
                }
                if any(value and value in advisor_values[basis] for value in health_values):
                    candidate_edges.append(CorrelationEdge(advisor.key, health_event.key, basis))
                    break
    unique_edges = tuple(sorted(set(candidate_edges), key=lambda edge: (edge.advisor_key, edge.service_health_key, edge.basis)))
    for edge in unique_edges:
        if edge.advisor_key not in by_key or edge.service_health_key not in by_key:
            raise ValueError("correlation edge references an unknown source event")

    advisor_to_health: dict[SourceEventKey, set[SourceEventKey]] = defaultdict(set)
    health_to_advisor: dict[SourceEventKey, set[SourceEventKey]] = defaultdict(set)
    edges_by_event: dict[SourceEventKey, list[CorrelationEdge]] = defaultdict(list)
    for edge in unique_edges:
        advisor_to_health[edge.advisor_key].add(edge.service_health_key)
        health_to_advisor[edge.service_health_key].add(edge.advisor_key)
        edges_by_event[edge.advisor_key].append(edge)
        edges_by_event[edge.service_health_key].append(edge)

    groups: list[tuple[SourceEvent, ...]] = []
    decisions: list[CorrelationDecision] = []
    visited: set[SourceEventKey] = set()
    ordered_events = tuple(sorted(events, key=lambda event: event.key))
    for event in ordered_events:
        if event.key in visited:
            continue
        component = {event.key}
        frontier = [event.key]
        while frontier:
            current = frontier.pop()
            neighbours = set(advisor_to_health.get(current, ())) | set(health_to_advisor.get(current, ()))
            for neighbour in neighbours:
                if neighbour not in component:
                    component.add(neighbour)
                    frontier.append(neighbour)
        visited.update(component)
        component_edges = tuple(sorted(
            {edge for key in component for edge in edges_by_event.get(key, ())},
            key=lambda edge: (edge.advisor_key, edge.service_health_key, edge.basis),
        ))
        advisors = {key for key in component if key.source == "advisor"}
        health = {key for key in component if key.source == "service-health"}
        one_to_one = (
            len(advisors) == 1
            and len(health) == 1
            and len(advisor_to_health[next(iter(advisors))]) == 1
            and len(health_to_advisor[next(iter(health))]) == 1
        )
        if one_to_one:
            advisor_key = next(iter(advisors))
            health_key = next(iter(health))
            basis = next(edge.basis for edge in component_edges if edge.advisor_key == advisor_key and edge.service_health_key == health_key)
            group = (by_key[advisor_key], by_key[health_key])
            groups.append(group)
            decisions.extend(
                (
                    CorrelationDecision(advisor_key, "explicitly_correlated", basis),
                    CorrelationDecision(health_key, "explicitly_correlated", basis),
                )
            )
            continue

        for key in sorted(component):
            candidates = tuple(sorted(
                (health if key.source == "advisor" else advisors),
            ))
            groups.append((by_key[key],))
            decisions.append(
                CorrelationDecision(
                    key,
                    "ambiguous_unmerged" if component_edges else "single_source",
                    "",
                    candidates,
                    component_edges if component_edges else (),
                )
            )

    # The construction above is already key ordered; retain that order as part
    # of the deterministic result and keep decisions aligned by key lookup.
    decision_by_key = {decision.event_key: decision for decision in decisions}
    ordered_groups = tuple(sorted(groups, key=lambda group: group[0].key))
    ordered_decisions = tuple(decision_by_key[key] for key in sorted(decision_by_key))
    return CorrelationResult(ordered_groups, ordered_decisions)


__all__ = [
    "CorrelationDecision",
    "CorrelationEdge",
    "CorrelationResult",
    "correlate_source_events",
]
