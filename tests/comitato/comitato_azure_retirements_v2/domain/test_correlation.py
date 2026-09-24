from src.comitato.comitato_azure_retirements_v2.domain.correlation import (
    CorrelationEdge,
    correlate_source_events,
)
from src.comitato.comitato_azure_retirements_v2.domain.retirements import SourceEvent


def event(source: str, identity: str, recommendation_type: str = "") -> SourceEvent:
    row = {"recommendation_type_id": recommendation_type, "service_health_event_id": identity}
    if source == "advisor" and recommendation_type:
        row["provenance_json"] = '{"service_health_tracking_ids":["' + recommendation_type + '"]}'
    elif source == "service-health":
        row["tracking_id"] = recommendation_type
    return SourceEvent(
        key=(source, identity),
        source=source,
        record_ref=f"ref-{identity}",
        row=row,
    )


def test_only_explicit_one_to_one_edges_merge_and_ambiguous_candidates_remain_separate() -> None:
    advisor = event("advisor", "a", "type-1")
    health_one = event("service-health", "h1", "type-1")
    health_two = event("service-health", "h2", "type-1")
    result = correlate_source_events(
        (advisor, health_one, health_two),
        (CorrelationEdge(advisor.key, health_one.key, "tracking_id"),),
    )
    assert result.status_by_event[advisor.key] == "ambiguous_unmerged"
    assert len(result.groups) == 3


def test_valid_explicit_edge_merges_exactly_one_advisor_and_health_event() -> None:
    advisor = event("advisor", "a", "type-1")
    health = event("service-health", "h", "type-1")

    result = correlate_source_events(
        (advisor, health),
        (CorrelationEdge(advisor.key, health.key, "tracking_id"),),
    )

    assert result.groups == ((advisor, health),)
    assert result.status_by_event[advisor.key] == "explicitly_correlated"
    assert result.decision_by_group[0].basis == "tracking_id"


def test_similarity_without_an_explicit_edge_does_not_merge() -> None:
    advisor = event("advisor", "a", "same-title")
    health = SourceEvent(
        key=("service-health", "h"),
        source="service-health",
        record_ref="ref-h",
        row={"title": "same-title", "service_health_event_id": "h"},
    )

    result = correlate_source_events((advisor, health), ())

    assert len(result.groups) == 2
    assert all(value == "single_source" for value in result.status_by_event.values())


def test_native_advisor_tracking_id_links_one_health_event() -> None:
    advisor = SourceEvent(
        key=("advisor", "a"),
        source="advisor",
        record_ref="ref-a",
        row={"source_health_tracking_ids": '["track-7"]'},
    )
    health = SourceEvent(
        key=("service-health", "h"),
        source="service-health",
        record_ref="ref-h",
        row={"tracking_id": "TRACK-7"},
    )

    result = correlate_source_events((advisor, health), ())

    assert result.groups == ((advisor, health),)
    assert result.decision_by_group[0].basis == "tracking_id"


def test_native_advisor_ash_url_links_health_by_its_tracking_id() -> None:
    advisor = SourceEvent(
        key=("advisor", "a"), source="advisor", record_ref="ref-a",
        row={"provenance_json": '{"service_health_ash_urls":["https://app.azure.com/h/track-8/"]}'},
    )
    health = SourceEvent(
        key=("service-health", "h"), source="service-health", record_ref="ref-h",
        row={"tracking_id": "track-8"},
    )

    result = correlate_source_events((advisor, health), ())

    assert result.groups == ((advisor, health),)
    assert result.decision_by_group[0].basis == "ash_url"


def test_recommendation_type_id_alone_does_not_correlate_events() -> None:
    advisor = SourceEvent(
        key=("advisor", "a"), source="advisor", record_ref="ref-a",
        row={"recommendation_type_id": "same-type"},
    )
    health = SourceEvent(
        key=("service-health", "h"), source="service-health", record_ref="ref-h",
        row={"recommendation_type_id": "same-type"},
    )

    result = correlate_source_events((advisor, health), ())

    assert len(result.groups) == 2
    assert all(value == "single_source" for value in result.status_by_event.values())


def test_ambiguous_decision_preserves_candidate_keys_and_rejected_edges() -> None:
    advisor = event("advisor", "a", "type-1")
    health_one = event("service-health", "h1", "type-1")
    health_two = event("service-health", "h2", "type-1")
    edges = (
        CorrelationEdge(advisor.key, health_one.key, "tracking_id"),
        CorrelationEdge(advisor.key, health_two.key, "tracking_id"),
    )

    result = correlate_source_events((advisor, health_one, health_two), edges)

    decision = result.decision_by_event[advisor.key]
    assert decision.status == "ambiguous_unmerged"
    assert decision.candidate_keys == (health_one.key, health_two.key)
    assert decision.rejected_edges == edges
