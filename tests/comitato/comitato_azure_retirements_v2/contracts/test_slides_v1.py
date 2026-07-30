import json
from datetime import date, datetime, timezone

from src.comitato.comitato_azure_retirements_v2.contracts.aggregate_v1 import HEADER as AGGREGATE_HEADER
from src.comitato.comitato_azure_retirements_v2.contracts.model import Artifact
from src.comitato.comitato_azure_retirements_v2.contracts.slides_v1 import (
    HEADER,
    SLIDES_V1,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.domain.slides import project_slides


def context() -> RunContext:
    return RunContext(
        run_id="run-1",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.SLIDES),
        scope=Scope(()),
        catalog_identity=CatalogIdentity(1, "a" * 64),
        dependency_plan=DependencyPlan(("scope", "aggregate", "slides")),
    )


def aggregate_row(aggregate_id: str, retirement_date: str) -> dict[str, str]:
    row = {column: "" for column in AGGREGATE_HEADER}
    for column in AGGREGATE_HEADER:
        if column.endswith("_json"):
            row[column] = "{}" if column == "platforms_subscriptions_json" else "[]"
    row.update(
        {
            "schema_version": "1",
            "run_id": "run-1",
            "as_of_date": "2026-07-30",
            "aggregate_id": aggregate_id,
            "source_event_keys_json": json.dumps([f"advisor:{aggregate_id}"]),
            "correlation_candidates_json": "[]",
            "source_systems_json": '["azure"]',
            "record_types_json": '["retirement"]',
            "raw_record_refs_json": json.dumps([f"raw-{aggregate_id}"]),
            "retirement_date": retirement_date,
            "retirement_date_quality": "exact",
            "retirement_dates_json": json.dumps([{"date": retirement_date, "quality": "exact"}]),
            "retirement_date_sources_json": '["structured"]',
            "is_global": "false",
            "platforms_json": '["Platform A"]',
            "platforms_subscriptions_json": '{"Platform A":[{"subscription_id":"11111111-1111-1111-1111-111111111111","subscription_name":"Subscription A"}]}',
            "source_links_json": '["https://example.invalid/retirement"]',
            "provenance_json": json.dumps({"raw_record_refs": [f"raw-{aggregate_id}"]}),
        }
    )
    return row


def aggregate_artifact(*rows: dict[str, str]) -> Artifact:
    from src.comitato.comitato_azure_retirements_v2.contracts.aggregate_v1 import AggregateRecord

    return Artifact(
        contract="aggregate",
        schema_version=1,
        run_id="run-1",
        records=tuple(AggregateRecord.from_mapping(row) for row in rows),
    )


def test_slides_v1_has_exact_utf8_header_and_empty_artifact() -> None:
    assert len(HEADER) == 42
    assert SLIDES_V1.encode(SLIDES_V1.empty_artifact(context())).data == (
        "\t".join(HEADER) + "\n"
    ).encode("utf-8")


def test_project_slides_copies_aggregate_values_and_leaves_refinement_empty() -> None:
    aggregate = aggregate_artifact(aggregate_row("aggregate-1", "2027-01-01"))

    result = project_slides(aggregate, context())

    assert result.is_valid
    assert result.value is not None
    slide = result.value.records[0]
    assert slide["aggregate_schema_version"] == "1"
    for column in AGGREGATE_HEADER:
        if column != "schema_version":
            assert slide[column] == aggregate.records[0][column]
    assert [slide[column] for column in HEADER[-4:]] == ["", "", "", ""]


def test_project_slides_orders_by_date_then_id_and_rejects_no_duplicates() -> None:
    aggregate = aggregate_artifact(
        aggregate_row("aggregate-b", "2027-01-01"),
        aggregate_row("aggregate-a", "2027-01-01"),
        aggregate_row("aggregate-c", "2026-07-30"),
    )

    result = project_slides(aggregate, context())

    assert result.is_valid
    assert result.value is not None
    assert [(row["retirement_date"], row["aggregate_id"]) for row in result.value.records] == [
        ("2026-07-30", "aggregate-c"),
        ("2027-01-01", "aggregate-a"),
        ("2027-01-01", "aggregate-b"),
    ]


def test_project_slides_returns_header_only_for_zero_row_selection() -> None:
    result = project_slides(
        aggregate_artifact(aggregate_row("aggregate-old", "2026-07-29")),
        context(),
    )

    assert result.is_valid
    assert result.value is not None
    assert result.value.records == ()
    assert SLIDES_V1.encode(result.value).data == ("\t".join(HEADER) + "\n").encode()
