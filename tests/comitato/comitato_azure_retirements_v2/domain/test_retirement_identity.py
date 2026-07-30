from src.comitato.comitato_azure_retirements_v2.domain.retirements import (
    AggregateId,
    SourceEventKey,
    aggregate_id_for,
)


def test_aggregate_id_uses_length_delimited_sorted_complete_keys() -> None:
    left = aggregate_id_for((SourceEventKey("a", "bc"), SourceEventKey("ab", "c")))
    right = aggregate_id_for((SourceEventKey("a", "b"), SourceEventKey("ab", "c")))
    assert isinstance(left, AggregateId)
    assert left != right
    assert left == aggregate_id_for((SourceEventKey("ab", "c"), SourceEventKey("a", "bc")))


def test_aggregate_id_is_run_independent() -> None:
    assert aggregate_id_for((SourceEventKey("advisor", "recommendation-1"),)).value.islower()
