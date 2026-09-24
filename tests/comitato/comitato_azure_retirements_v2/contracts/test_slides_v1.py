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
            "record_types_json": '["retirement"]',
            "raw_record_refs_json": json.dumps([f"raw-{aggregate_id}"]),
            "retirement_date": retirement_date,
            "retirement_date_quality": quality,
            "retirement_dates_json": json.dumps(
                claims if claims is not None else [{"date": retirement_date, "quality": "exact"}]
            ),
            "date_events_json": json.dumps([
                {"date": claim.get("date", retirement_date), "kind": "retirement", "source": "advisor"}
                for claim in (claims if claims is not None else [{"date": retirement_date, "quality": "exact"}])
                if claim.get("date", retirement_date) and claim.get("quality", "exact") == "exact"
            ]),
            "retirement_date_sources_json": '["structured"]',
            "source_systems_json": '["azure-advisor"]',
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
        "impatto_microsoft", "comitato_descrizione", "comitato_retirement_date",
        "comitato_piattaforme", "retirement_date", "stato_data",
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
    assert slide["id_elemento"].startswith("azure-retirement:v2:")
    assert slide["titolo_breve"] == "Compute"
    assert slide["descrizione_breve"] == "Feature A"
    assert slide["comitato_priorità"] == ""
    assert slide["comitato_descrizione"] == ""
    assert slide["comitato_retirement_date"] == ""
    assert slide["retirement_date"] == "2027-01-01 — Data di ritiro (Azure Advisor)"
    assert slide["stato_data"] == "In scadenza"
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
    assert [row["stato_data"] for row in result.value.records] == ["In scadenza", "In scadenza", "In scadenza"]
    assert len({row["id_elemento"] for row in result.value.records}) == 3


def test_project_slides_keeps_elapsed_rows_as_drafts() -> None:
    result = project_slides(
        aggregate_artifact(aggregate_row("aggregate-old", "2026-07-29")),
        context(),
    )

    assert result.is_valid
    assert result.value is not None
    assert result.value.records[0]["id_elemento"].startswith("azure-retirement:v2:")
    assert result.value.records[0]["stato_data"] == "Scaduta"


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
    assert len(result.value.artifact.records) == 6
    assert {row["stato_data"] for row in result.value.artifact.records} == {
        "In scadenza", "Scaduta", "Date discordanti", "Data non disponibile"
    }
    assert set(result.value.excluded_by_reason) == {"beyond_committee_window"}


def test_projection_uses_problem_titles_and_renders_source_singletons() -> None:
    row = aggregate_row("aggregate-1", "2027-01-01")
    row["advisor_recommendation_ids_json"] = '["advisor-1"]'
    row["service_health_tracking_ids_json"] = '["track-1"]'
    row["problem_titles_json"] = '["Retire SDK"]'
    row["advisor_impacts_json"] = '["High"]'
    row["advisor_recommendation_type_ids_json"] = '["advisor-type-1"]'
    row["date_events_json"] = '[{"date":"2027-01-01","kind":"retirement","source":"advisor"}]'
    row["advisor_problem_descriptions_json"] = '["Advisor body"]'
    row["advisor_actions_json"] = '["Update SDK"]'
    row["service_health_problem_descriptions_json"] = '["Health body"]'
    row["service_health_actions_json"] = '["Migrate"]'
    row["source_systems_json"] = '["azure-advisor", "azure-service-health"]'
    row["source_links_json"] = '["https://example.invalid/advisor", "https://example.invalid/health"]'
    row["platforms_json"] = '["Platform A"]'
    row["platforms_subscriptions_json"] = '{"Platform A":[{"subscription_id":"11111111-1111-1111-1111-111111111111","subscription_name":"Subscription A"}]}'
    row["published_resource_ids_json"] = '["/subscriptions/111/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-1"]'
    row["provenance_json"] = json.dumps({"raw_record_refs": ["raw-aggregate-1"]})

    result = project_slides(aggregate_artifact(row), context())

    assert result.is_valid
    assert result.value is not None
    slide = result.value.records[0]
    assert slide["descrizione_breve"] == "Retire SDK"
    assert slide["comitato_descrizione"] == ""
    assert slide["comitato_retirement_date"] == ""
    assert slide["comitato_descrizione"] == ""
    assert slide["comitato_retirement_date"] == ""
    assert slide["azione_originale"] == "Advisor: Update SDK\n\nService Health: Migrate"
    assert slide["fonti"] == "Azure Advisor; Azure Service Health"
    assert slide["id_advisor"] == "advisor-type-1"
    assert slide["id_service_health"] == "track-1"
    assert json.loads(slide["risorse_json"])


def test_projection_renders_structured_actions_as_readable_source_text() -> None:
    row = aggregate_row("aggregate-actions", "2027-01-01")
    row["advisor_actions_json"] = json.dumps([
        {
            "caption": "Migrate the workload",
            "label": "Open migration guidance",
            "learnMoreLink": "https://example.invalid/action",
        }
    ])

    result = project_slides(aggregate_artifact(row), context())

    assert result.is_valid
    assert result.value is not None
    action = result.value.records[0]["azione_originale"]
    assert action == "Advisor: Migrate the workload"
    assert "{'caption'" not in action


def test_validator_only_rejects_priority_and_duplicate_ids() -> None:
    aggregate = aggregate_artifact(aggregate_row("aggregate-1", "2027-01-01"))
    selected = project_slides(aggregate, context()).value
    assert selected is not None
    values = dict(selected.records[0].values)
    values["comitato_descrizione"] = "Reviewed description"
    values["comitato_retirement_date"] = "2027-01-01"

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


def test_thirteen_advisor_records_of_one_type_become_one_stable_slide_row() -> None:
    rows = []
    for index in range(13):
        row = aggregate_row(f"aggregate-{index:02}", "2027-01-01")
        row["advisor_recommendation_ids_json"] = json.dumps([f"advisor-{index:02}"])
        row["advisor_recommendation_type_ids_json"] = '["advisor-type-1"]'
        row["problem_titles_json"] = '["One retirement problem"]'
        row["advisor_impacts_json"] = '["High"]'
        row["date_events_json"] = json.dumps([
            {"date": "2027-01-01", "kind": "retirement", "source": "advisor"},
        ])
        rows.append(row)

    result = project_slides(aggregate_artifact(*rows), context())

    assert result.is_valid
    assert result.value is not None
    assert len(result.value.records) == 1
    slide = result.value.records[0]
    assert slide["id_elemento"] == "azure-retirement:v2:371255663d32dcbb300a4458cce2c28f710721e49c23ab37669141f932c38ae0"
    assert slide["id_advisor"] == "advisor-type-1"
    assert slide["descrizione_breve"] == "One retirement problem"


def test_service_health_group_uses_tracking_key_and_keeps_impact_empty() -> None:
    row = aggregate_row("health-aggregate", "2027-03-01")
    row["source_systems_json"] = '["azure-service-health"]'
    row["advisor_recommendation_type_ids_json"] = "[]"
    row["advisor_recommendation_ids_json"] = "[]"
    row["service_health_event_ids_json"] = '["event-1"]'
    row["service_health_tracking_ids_json"] = '["track-1"]'
    row["problem_titles_json"] = '["Storage notice"]'
    row["date_events_json"] = json.dumps([
        {"date": "2027-03-01", "kind": "retirement", "source": "service-health"},
    ])

    result = project_slides(aggregate_artifact(row), context())

    assert result.is_valid and result.value is not None
    slide = result.value.records[0]
    assert slide["id_elemento"] == "azure-retirement:v2:22a79fff2c46c18d6c03cbbd0a39addef718022f4fe8c7f4b5b19c3f8da49940"
    assert slide["id_service_health"] == "track-1"
    assert slide["impatto_microsoft"] == ""
    assert slide["descrizione_breve"] == "Storage notice"


def test_impact_scope_counts_environments_and_compact_resources() -> None:
    row = aggregate_row("impact-aggregate", "2027-01-01")
    entries = [
        {"subscription_id": f"sub-{index}", "subscription_name": name}
        for index, name in enumerate(("PROD-east", "UAT-test", "DEV-lab", "shared"), start=1)
    ]
    row["platforms_subscriptions_json"] = json.dumps({"Platform A": entries})
    row["affected_subscription_names_json"] = json.dumps([entry["subscription_name"] for entry in entries])
    row["impacted_services_json"] = '["Storage"]'
    row["impacted_regions_json"] = '["westeurope"]'
    evidence = [[f"sub-{index}", f"vm-{index}", "rg", f"/subscriptions/sub-{index}/resourceGroups/rg/providers/x/vm-{index}", "matched"] for index in range(1, 5)]
    row["provenance_json"] = json.dumps({"resource_evidence": evidence})

    result = project_slides(aggregate_artifact(row), context())

    assert result.is_valid and result.value is not None
    slide = result.value.records[0]
    assert json.loads(slide["ambito_impatto"]) == {
        "totale_piattaforme": 1,
        "totale_subscription": 4,
        "totale_risorse": 4,
        "ambienti": {"PROD": 1, "UAT": 1, "DEV": 1, "ALTRO": 1},
        "servizi": ["Storage"],
        "regioni": ["westeurope"],
        "piattaforme": {"Platform A": {"subscription": 4, "risorse": 4}},
    }
    assert slide["risorse_json"] == '{"Platform A":{"DEV-lab":{"rg":["vm-3"]},"PROD-east":{"rg":["vm-1"]},"UAT-test":{"rg":["vm-2"]},"shared":{"rg":["vm-4"]}}}'
