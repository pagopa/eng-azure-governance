from src.comitato.comitato_azure_retirements_v2.domain.correlation import (
    CorrelationEdge,
    correlate_source_events,
)
from src.comitato.comitato_azure_retirements_v2.domain.retirements import SourceEvent


def event(source: str, identity: str, recommendation_type: str = "") -> SourceEvent:
    return SourceEvent(
        key=(source, identity),
        source=source,
        record_ref=f"ref-{identity}",
        row={"recommendation_type_id": recommendation_type, "service_health_event_id": identity},
    )


def test_only_explicit_one_to_one_edges_merge_and_ambiguous_candidates_remain_separate() -> None:
    advisor = event("advisor", "a", "type-1")
    health_one = event("service-health", "h1", "type-1")
    health_two = event("service-health", "h2", "type-1")
    result = correlate_source_events(
        (advisor, health_one, health_two),
        (CorrelationEdge(advisor.key, health_one.key, "recommendation_type_id"),),
    )
    assert result.status_by_event[advisor.key] == "ambiguous_unmerged"
    assert len(result.groups) == 3

