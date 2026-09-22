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
from src.comitato.comitato_azure_retirements_v2.domain.slides import project_slides, select_slides


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


def aggregate_row(
    aggregate_id: str,
    retirement_date: str,
    *,
    quality: str = "exact",
    claims: object | None = None,
) -> dict[str, str]:
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
            "retirement_date_quality": quality,
            "retirement_dates_json": json.dumps(
                claims if claims is not None else [{"date": retirement_date, "quality": "exact"}]
            ),
            "retirement_date_sources_json": '["structured"]',
            "source_systems_json": '["azure-advisor"]',
            "record_types_json": '["retirement"]',
            "technology_or_service": "Compute",
            "retiring_feature": "Feature A",
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
    assert HEADER == (
        "id_elemento", "titolo_breve", "descrizione_breve", "comitato_priorità",
        "comitato_descrizione", "comitato_retirement_date", "comitato_piattaforme",
        "retirement_date", "stato_data", "tipo_cambiamento", "stato_editoriale",
        "descrizione_originale_completa", "azione_originale", "fonti", "link_fonti",
        "ambito_impatto", "id_advisor", "id_service_health", "risorse_json",
    )
    assert SLIDES_V1.encode(SLIDES_V1.empty_artifact(context())).data == (
        "\t".join(HEADER) + "\n"
    ).encode("utf-8")


def test_project_slides_emits_committee_projection_and_leaves_external_fields_empty() -> None:
    aggregate = aggregate_artifact(aggregate_row("aggregate-1", "2027-01-01"))

    result = project_slides(aggregate, context())

    assert result.is_valid
    assert result.value is not None
    slide = result.value.records[0]
    assert slide["id_elemento"] == "aggregate-1"
    assert slide["titolo_breve"] == "Compute"
    assert slide["descrizione_breve"] == "Draft: Feature A"
    assert slide["comitato_priorità"] == ""
    assert slide["comitato_descrizione"] == ""
    assert slide["comitato_retirement_date"] == ""
    assert slide["retirement_date"] == "2027-01-01"
    assert slide["stato_data"] == "upcoming"
    assert slide["tipo_cambiamento"] == "retirement"
    assert slide["stato_editoriale"] == "draft: missing_editorial_mapping"
    assert slide["fonti"] == "Azure Advisor"
    assert slide["link_fonti"] == "https://example.invalid/retirement"
    assert slide["id_advisor"] == ""
    assert slide["id_service_health"] == ""
    assert list(json.loads(slide["risorse_json"])) == ["Platform A"]


def test_project_slides_orders_by_date_then_id_and_rejects_no_duplicates() -> None:
    aggregate = aggregate_artifact(
        aggregate_row("aggregate-b", "2027-01-01"),
        aggregate_row("aggregate-a", "2027-01-01"),
        aggregate_row("aggregate-c", "2026-07-30"),
    )

    result = project_slides(aggregate, context())

    assert result.is_valid
    assert result.value is not None
    assert [(row["retirement_date"], row["id_elemento"]) for row in result.value.records] == [
        ("2026-07-30", "aggregate-c"),
        ("2027-01-01", "aggregate-a"),
        ("2027-01-01", "aggregate-b"),
    ]


def test_project_slides_keeps_elapsed_rows_as_drafts() -> None:
    result = project_slides(
        aggregate_artifact(aggregate_row("aggregate-old", "2026-07-29")),
        context(),
    )

    assert result.is_valid
    assert result.value is not None
    assert [row["id_elemento"] for row in result.value.records] == ["aggregate-old"]
    assert result.value.records[0]["stato_data"] == "elapsed"


def test_selection_preserves_every_temporal_category_outside_the_slide_view() -> None:
    aggregate = aggregate_artifact(
        aggregate_row("eligible", "2027-01-01"),
        aggregate_row("elapsed", "2026-07-29"),
        aggregate_row("beyond", "2027-07-31"),
        aggregate_row("missing", "", quality="missing", claims=[]),
        aggregate_row("invalid", "not-a-date", quality="invalid", claims=[]),
        aggregate_row("partial", "", quality="partial", claims=[{"raw_value": "2027", "quality": "partial"}]),
        aggregate_row(
            "conflict",
            "",
            quality="conflict",
            claims=[{"date": "2027-01-01"}, {"date": "2027-02-01"}],
        ),
    )

    result = select_slides(aggregate, context())

    assert result.is_valid
    assert result.value is not None
    assert len(aggregate.records) == 7
    assert [row["id_elemento"] for row in result.value.artifact.records] == [
        "elapsed", "eligible", "conflict", "missing", "partial", "invalid"
    ]
    assert set(result.value.excluded_by_reason) == {"beyond_committee_window"}


def test_projection_applies_editorial_values_and_renders_source_singletons() -> None:
    row = aggregate_row("aggregate-1", "2027-01-01")
    row["advisor_recommendation_ids_json"] = '["advisor-1"]'
    row["service_health_tracking_ids_json"] = '["track-1"]'
    row["advisor_problem_descriptions_json"] = '["Advisor body"]'
    row["advisor_actions_json"] = '["Update SDK"]'
    row["service_health_problem_descriptions_json"] = '["Health body"]'
    row["service_health_actions_json"] = '["Migrate"]'
    row["source_systems_json"] = '["azure-advisor", "azure-service-health"]'
    row["source_links_json"] = '["https://example.invalid/advisor", "https://example.invalid/health"]'
    row["platforms_json"] = '["Platform A"]'
    row["platforms_subscriptions_json"] = '{"Platform A":[{"subscription_id":"11111111-1111-1111-1111-111111111111","subscription_name":"Subscription A"}]}'
    row["published_resource_ids_json"] = '["/subscriptions/111/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-1"]'
    row["provenance_json"] = json.dumps({
        "raw_record_refs": ["raw-aggregate-1"],
        "editorial": {
            "item_id": "item-1",
            "title": "Retire SDK",
            "description": "Use the supported SDK.",
            "suggested_action": "Upgrade the SDK.",
            "retirement_date": "2027-02-01",
            "review_state": "ready",
        },
    })

    result = project_slides(aggregate_artifact(row), context())

    assert result.is_valid
    assert result.value is not None
    slide = result.value.records[0]
    assert slide["titolo_breve"] == "Retire SDK"
    assert slide["descrizione_breve"] == "Use the supported SDK."
    assert slide["comitato_descrizione"] == "Use the supported SDK."
    assert slide["comitato_retirement_date"] == "2027-02-01"
    assert slide["stato_editoriale"] == "reviewed"
    assert slide["azione_originale"] == "Advisor: Update SDK\n\nService Health: Migrate"
    assert slide["fonti"] == "Azure Advisor; Azure Service Health"
    assert slide["id_advisor"] == "advisor-1"
    assert slide["id_service_health"] == "track-1"
    assert json.loads(slide["risorse_json"])


def test_populated_committee_refinements_are_valid_but_priority_stays_external() -> None:
    aggregate = aggregate_artifact(aggregate_row("aggregate-1", "2027-01-01"))
    selected = project_slides(aggregate, context()).value
    assert selected is not None
    values = dict(selected.records[0].values)
    values["comitato_descrizione"] = "Reviewed description"
    values["comitato_retirement_date"] = "2027-01-01"
    values["comitato_piattaforme"] = "Platform A"

    populated = selected.__class__(
        contract=selected.contract,
        schema_version=selected.schema_version,
        run_id=selected.run_id,
        records=(selected.records[0].__class__(tuple(values.items())),),
    )
    assert SLIDES_V1.validate(populated, context()).is_valid

    values["comitato_priorità"] = "P1"
    rejected = populated.__class__(
        contract=populated.contract,
        schema_version=populated.schema_version,
        run_id=populated.run_id,
        records=(populated.records[0].__class__(tuple(values.items())),),
    )
    assert not SLIDES_V1.validate(rejected, context()).is_valid
