from src.comitato.comitato_azure_retirements_v2.domain.retirements import (
    AggregateId,
    AggregateMembership,
    SourceEventKey,
    aggregate_id_for,
    build_source_events,
)


def test_aggregate_id_uses_length_delimited_sorted_complete_keys() -> None:
    left = aggregate_id_for((SourceEventKey("a", "bc"), SourceEventKey("ab", "c")))
    right = aggregate_id_for((SourceEventKey("a", "b"), SourceEventKey("ab", "c")))
    assert isinstance(left, AggregateId)
    assert left != right
    assert left == aggregate_id_for((SourceEventKey("ab", "c"), SourceEventKey("a", "bc")))


def test_aggregate_id_is_run_independent() -> None:
    assert aggregate_id_for((SourceEventKey("advisor", "recommendation-1"),)).value.islower()


def test_source_events_group_only_by_explicit_source_identity() -> None:
    advisor = (
        {"advisor_recommendation_id": "rec-1", "recommendation_type_id": " Type-A ", "raw_record_ref": "a-1"},
        {"advisor_recommendation_id": "rec-2", "recommendation_type_id": "type-a", "raw_record_ref": "a-2"},
        {"advisor_recommendation_id": "rec-3", "recommendation_type_id": "", "raw_record_ref": "a-3"},
    )
    health = ({"tracking_id": "TRACK-1", "raw_record_ref": "h-1"},)

    events, memberships = build_source_events(advisor, health)

    assert [event.key for event in events] == [
        SourceEventKey("advisor", "rec-3"),
        SourceEventKey("advisor", "type-a"),
        SourceEventKey("service-health", "track-1"),
    ]
    assert memberships == (
        AggregateMembership(SourceEventKey("advisor", "rec-3"), ("a-3",)),
        AggregateMembership(SourceEventKey("advisor", "type-a"), ("a-1", "a-2")),
        AggregateMembership(SourceEventKey("service-health", "track-1"), ("h-1",)),
    )


def test_source_event_keys_and_memberships_are_input_order_independent() -> None:
    first = build_source_events(
        ({"advisor_recommendation_id": "rec-2", "raw_record_ref": "2"}, {"advisor_recommendation_id": "rec-1", "raw_record_ref": "1"}),
        (),
    )
    second = build_source_events(
        ({"advisor_recommendation_id": "rec-1", "raw_record_ref": "1"}, {"advisor_recommendation_id": "rec-2", "raw_record_ref": "2"}),
        (),
    )
    assert first == second


def test_each_raw_reference_is_represented_once() -> None:
    events, memberships = build_source_events(
        ({"advisor_recommendation_id": "rec-1", "raw_record_ref": "same"},),
        ({"tracking_id": "track-1", "raw_record_ref": "same"},),
    )

    assert events
    assert sum(memberships_item.raw_record_refs.count("same") for memberships_item in memberships) == 1
