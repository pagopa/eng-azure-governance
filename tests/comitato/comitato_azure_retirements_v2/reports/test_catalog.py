from dataclasses import FrozenInstanceError
from textwrap import dedent

import pytest
import yaml

from src.comitato.comitato_azure_retirements_v2.contracts import AGGREGATE_V1, SLIDES_V1
from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector
from src.comitato.comitato_azure_retirements_v2.reports.advisor import ADVISOR_REPORT
from src.comitato.comitato_azure_retirements_v2.reports.catalog import (
    DEFAULT_REPORT_CATALOG,
    EditorialCatalog,
    EditorialCatalogSource,
    EditorialItem,
    EditorialWorkItem,
    ReportCatalog,
    SelectedReportClosure,
    build_editorial_work_list,
    render_editorial_yaml,
)
from src.comitato.comitato_azure_retirements_v2.domain.retirements import build_source_events
from src.comitato.comitato_azure_retirements_v2.reports.model import (
    ReportDefinition,
    StagedDecodeFailure,
)
from src.comitato.comitato_azure_retirements_v2.reports.service_health import (
    SERVICE_HEALTH_REPORT,
)
from tests.comitato.comitato_azure_retirements_v2.publication.test_empty_publication import (
    empty_candidate,
)


def _renamed_catalog() -> ReportCatalog:
    return ReportCatalog(
        (
            ReportDefinition(
                ReportSelector.ADVISOR,
                "custom-advisor",
                "advisor",
                (),
                ADVISOR_REPORT.contract,
            ),
            ReportDefinition(
                ReportSelector.SERVICE_HEALTH,
                "custom-service-health",
                "service-health",
                (),
                SERVICE_HEALTH_REPORT.contract,
            ),
            ReportDefinition(
                ReportSelector.AGGREGATE,
                "custom-aggregate",
                "aggregate",
                (ReportSelector.ADVISOR, ReportSelector.SERVICE_HEALTH),
                AGGREGATE_V1,
            ),
            ReportDefinition(
                ReportSelector.SLIDES,
                "custom-slides",
                "slides",
                (ReportSelector.AGGREGATE,),
                SLIDES_V1,
            ),
        )
    )


def test_plan_returns_one_immutable_selected_closure() -> None:
    closure = DEFAULT_REPORT_CATALOG.plan(ReportSelector.SLIDES)

    assert isinstance(closure, SelectedReportClosure)
    assert closure.expected_paths == (
        "03_azure_retirements_slide.tsv",
        "azure-retirements-editorial.yaml",
    )
    assert closure.owner_of("03_azure_retirements_slide.tsv").name == "slides"
    assert closure.owner_of("azure-retirements-editorial.yaml").name == "slides"
    with pytest.raises(FrozenInstanceError):
        closure.selector = ReportSelector.ALL


def test_non_default_catalog_closure_preserves_custom_ownership() -> None:
    closure = _renamed_catalog().plan(ReportSelector.ALL)

    assert closure.expected_paths == DEFAULT_REPORT_CATALOG.plan(ReportSelector.ALL).expected_paths
    assert closure.owner_of("01_azure_advisor_retirements_raw.tsv").name == "custom-advisor"
    assert closure.owner_of("03_azure_retirements_slide.tsv").name == "custom-slides"


@pytest.mark.parametrize(
    ("selector", "stages", "published"),
    (
        (
            ReportSelector.ALL,
            ("scope", "catalog", "advisor", "service-health", "aggregate", "slides", "publication"),
            ("advisor", "service-health", "aggregate", "slides"),
        ),
        (
            ReportSelector.ADVISOR,
            ("scope", "catalog", "advisor", "publication"),
            ("advisor",),
        ),
        (
            ReportSelector.SERVICE_HEALTH,
            ("scope", "catalog", "service-health", "publication"),
            ("service-health",),
        ),
        (
            ReportSelector.AGGREGATE,
            ("scope", "catalog", "advisor", "service-health", "aggregate", "publication"),
            ("aggregate",),
        ),
        (
            ReportSelector.SLIDES,
            ("scope", "catalog", "advisor", "service-health", "aggregate", "slides", "publication"),
            ("slides",),
        ),
    ),
)
def test_plan_preserves_dependency_and_publication_order(selector, stages, published):
    plan = DEFAULT_REPORT_CATALOG.plan(selector)
    assert plan.stages == stages
    assert tuple(item.name for item in plan.published) == published


def test_every_declared_path_has_exactly_one_owner():
    paths = DEFAULT_REPORT_CATALOG.all_paths
    assert len(paths) == len(set(paths))
    assert tuple(DEFAULT_REPORT_CATALOG.owner_of(path).name for path in paths) == (
        "advisor",
        "advisor",
        "service-health",
        "service-health",
        "aggregate",
        "slides",
        "slides",
    )


def test_report_definition_verifies_staged_artifacts():
    candidate = empty_candidate()
    definition = DEFAULT_REPORT_CATALOG.owner_of(
        "01_azure_advisor_retirements_raw.tsv"
    )
    payloads = {
        item.logical_path: item.data for item in candidate.artifacts
    }

    assert definition.verify_staged_artifact(
        definition.contract.path, payloads, candidate.context
    ) == ()

    payloads[definition.contract.companion_path] = b"not-json\n"
    with pytest.raises(StagedDecodeFailure) as raised:
        definition.verify_staged_artifact(
            definition.contract.companion_path, payloads, candidate.context
        )
    assert raised.value.logical_path == definition.contract.companion_path


def test_editorial_catalog_loads_stable_items_and_explicit_associations(tmp_path):
    path = tmp_path / "editorial.yaml"
    path.write_text(
        dedent("""schema_version: 1
items:
  - id: item-001
    associations:
      advisor:
        recommendation_type_ids: [advisor-type-001]
      service_health:
        tracking_ids: [health-track-001]
    title: Retire the feature
    description: Move workloads before the retirement.
    suggested_action: Plan the migration.
"""),
        encoding="utf-8",
    )

    catalog = EditorialCatalogSource(path).load()

    assert catalog.item_ids == ("item-001",)
    assert catalog.item_for_source("advisor", "advisor-type-001").item_id == "item-001"
    assert catalog.item_for_source("service-health", "health-track-001").item_id == "item-001"
    assert catalog.item_for_source("advisor", "advisor-type-001").title == "Retire the feature"


def test_editorial_catalog_rejects_duplicate_source_ownership(tmp_path):
    path = tmp_path / "editorial.yaml"
    path.write_text(
        dedent("""schema_version: 1
items:
  - id: item-001
    associations: {advisor: {recommendation_type_ids: [same]}}
  - id: item-002
    associations: {advisor: {recommendation_type_ids: [same]}}
"""),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate source ownership"):
        EditorialCatalogSource(path).load()


def test_editorial_catalog_diagnoses_unassociated_and_ambiguous_source_events():
    catalog = EditorialCatalog(
        1,
        "a" * 64,
        (
            EditorialItem("item-type", (("advisor", ("retirement-type",)),)),
            EditorialItem("item-instance", (("advisor", ("advisor-instance",)),)),
        ),
    )
    events, _ = build_source_events(
        (
            {
                "recommendation_type_id": "retirement-type",
                "advisor_recommendation_id": "advisor-instance",
                "raw_record_ref": "advisor-raw",
            },
        ),
        (
            {
                "tracking_id": "health-unassociated",
                "raw_record_ref": "health-raw",
            },
        ),
    )

    diagnostics = catalog.association_diagnostics(events, run_id="run-1")

    assert [(item.code, item.record_ref) for item in diagnostics] == [
        ("ambiguous_editorial_mapping", "advisor:retirement-type"),
        ("unassociated_editorial_source", "service-health:health-unassociated"),
    ]
    assert all(item.run_id == "run-1" for item in diagnostics)
    assert all("raw" in item.message for item in diagnostics)


def test_editorial_work_list_fingerprint_ignores_run_metadata_and_resource_fanout():
    catalog = EditorialCatalog(
        1,
        "a" * 64,
        (EditorialItem("item-1", (("advisor", ("retirement-type",)),)),),
    )
    base = {
        "recommendation_type_id": "retirement-type",
        "advisor_recommendation_id": "advisor-instance",
        "description": "Move the workload",
        "actions_json": '["Update"]',
        "retirement_date": "2027-01-01",
        "impacted_service": "Compute",
        "impacted_region": "westeurope",
        "run_id": "run-1",
        "raw_record_ref": "advisor-raw",
        "normalized_resource_id": "/subscriptions/a/resourceGroups/one/providers/x/one",
    }
    changed_metadata = {
        **base,
        "run_id": "run-2",
        "raw_record_ref": "advisor-raw-2",
        "normalized_resource_id": "/subscriptions/b/resourceGroups/two/providers/x/two",
    }
    changed_content = {**base, "description": "Migrate the workload"}

    first_events, _ = build_source_events((base,), ())
    metadata_events, _ = build_source_events((changed_metadata,), ())
    content_events, _ = build_source_events((changed_content,), ())

    first = build_editorial_work_list(catalog, first_events)[0]
    metadata = build_editorial_work_list(catalog, metadata_events)[0]
    content = build_editorial_work_list(catalog, content_events)[0]

    assert first.source_fingerprint == metadata.source_fingerprint
    assert first.source_fingerprint != content.source_fingerprint


def test_editorial_work_list_creates_a_stable_draft_for_unassociated_source_event():
    catalog = EditorialCatalog(1, "a" * 64, ())
    events, _ = build_source_events(
        (
            {
                "advisor_recommendation_id": "advisor-instance",
                "description": "Move the workload before the deadline.",
                "actions_json": '[{"text":"Migrate the workload"}]',
                "raw_record_ref": "advisor-raw",
            },
        ),
        (),
    )

    work_items = build_editorial_work_list(catalog, events)

    assert len(work_items) == 1
    assert work_items[0].item_id.startswith("azure-retirement:v1:")
    assert work_items[0].source_ids == ("advisor-raw",)
    assert work_items[0].description == "Move the workload before the deadline."
    assert work_items[0].suggested_action == "Migrate the workload"
    assert work_items[0].review_reason == "missing_editorial_mapping"


def test_render_editorial_yaml_publishes_draft_source_support():
    rendered = render_editorial_yaml(
        "schema_version: 1\nitems: []\n",
        EditorialCatalog(1, "a" * 64, ()),
        (
            EditorialWorkItem(
                item_id="draft-001",
                source_ids=("advisor-raw",),
                title="Retire the feature",
                description="Move the workload before the deadline.",
                suggested_action="Migrate the workload",
                review_reason="missing_editorial_mapping",
                source_fingerprint="b" * 64,
                source_content=(
                    ("description", "Move the workload before the deadline."),
                ),
            ),
        ),
    )

    payload = yaml.safe_load(rendered)

    assert payload["items"] == [
        {
            "id": "draft-001",
            "title": "Retire the feature",
            "description": "Move the workload before the deadline.",
            "suggested_action": "Migrate the workload",
            "source_support": {
                "source_ids": ["advisor-raw"],
                "review_reason": "missing_editorial_mapping",
                "source_fingerprint": "b" * 64,
                "content": [
                    {
                        "field": "description",
                        "value": "Move the workload before the deadline.",
                    }
                ],
            },
        }
    ]
