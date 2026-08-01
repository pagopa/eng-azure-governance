import json
from datetime import date, datetime, timezone

from src.comitato.comitato_azure_retirements_v2.contracts.aggregate_v1 import build_aggregate
from src.comitato.comitato_azure_retirements_v2.domain.execution import CatalogIdentity, DependencyPlan, ReportSelector, RunContext, RunRequest, Scope
from src.comitato.comitato_azure_retirements_v2.domain.platforms import PlatformCatalogSnapshot


def test_s04_ambiguous_typed_candidates_remain_three_separate_aggregates() -> None:
    context = RunContext(
        run_id="s04",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.AGGREGATE),
        scope=Scope(()),
        catalog_identity=CatalogIdentity(1, "a" * 64),
        dependency_plan=DependencyPlan(("aggregate",)),
    )
    catalog = PlatformCatalogSnapshot(schema_version=1, sha256="a" * 64, assignments=())
    advisor = {"advisor_recommendation_id": "advisor-1", "recommendation_type_id": "retirement-1", "raw_record_ref": "advisor-ref"}
    service_health = (
        {"service_health_event_id": "health-1", "tracking_id": "health-track-1", "recommendation_type_id": "retirement-1", "raw_record_ref": "health-ref-1", "subscription_evidence_source": "explicit_global"},
        {"service_health_event_id": "health-2", "tracking_id": "health-track-2", "recommendation_type_id": "retirement-1", "raw_record_ref": "health-ref-2", "subscription_evidence_source": "explicit_global"},
    )

    rows = build_aggregate((advisor,), service_health, context=context, catalog=catalog)

    assert len(rows) == 3
    assert sum(row["correlation_status"] == "ambiguous_unmerged" for row in rows) == 3
    advisor_row = next(row for row in rows if json.loads(row["raw_record_refs_json"]) == ["advisor-ref"])
    assert json.loads(advisor_row["correlation_candidates_json"]) == [
        "service-health:health-track-1",
        "service-health:health-track-2",
    ]
