import json
from types import SimpleNamespace
from datetime import date, datetime, timezone

from src.comitato.comitato_azure_retirements_v2.contracts.aggregate_v1 import (
    AGGREGATE_V1,
    build_aggregate,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.domain.platforms import (
    PlatformAssignment,
    PlatformCatalogSnapshot,
    SubscriptionId,
)


SUBSCRIPTION = "11111111-1111-1111-1111-111111111111"


def context() -> RunContext:
    return RunContext(
        run_id="run-1",
        as_of_date=date(2026, 7, 30),
        created_at=datetime(2026, 7, 30, tzinfo=timezone.utc),
        request=RunRequest(ReportSelector.AGGREGATE),
        scope=Scope((SUBSCRIPTION,)),
        catalog_identity=CatalogIdentity(1, "a" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "aggregate")),
    )


def catalog() -> PlatformCatalogSnapshot:
    return PlatformCatalogSnapshot(
        schema_version=1,
        sha256="a" * 64,
        assignments=(PlatformAssignment(SubscriptionId(SUBSCRIPTION), "Platform A", "Subscription A"),),
    )


def test_build_aggregate_preserves_membership_and_catalog_projection() -> None:
    records = build_aggregate(
        (
            {
                "run_id": "run-1",
                "as_of_date": "2026-07-30",
                "advisor_recommendation_id": "rec-1",
                "recommendation_type_id": "retirement-1",
                "subscription_id": SUBSCRIPTION,
                "subscription_name": "Azure A",
                "service_name": "Compute",
                "retiring_feature": "Feature A",
                "retirement_date": "2027-01-01",
                "retirement_date_quality": "exact",
                "description": "Advisor detail",
                "actions_json": '["Update"]',
                "raw_record_ref": "advisor-ref",
            },
        ),
        (),
        context=context(),
        catalog=catalog(),
    )

    assert len(records) == 1
    row = records[0]
    assert json.loads(row["raw_record_refs_json"]) == ["advisor-ref"]
    assert json.loads(row["platforms_json"]) == ["Platform A"]
    assert json.loads(row["platforms_subscriptions_json"]) == {
        "Platform A": [{"subscription_id": SUBSCRIPTION, "subscription_name": "Subscription A"}]
    }
    assert row["is_global"] == "false"
    assert AGGREGATE_V1.validate(
        AGGREGATE_V1.empty_artifact(context()).__class__(
            contract="aggregate", schema_version=1, run_id="run-1", records=tuple(records)
        ),
            context(),
    ).is_valid


def test_empty_aggregate_encodes_exact_header() -> None:
    encoded = AGGREGATE_V1.encode(AGGREGATE_V1.empty_artifact(context()))
    assert encoded.data == ("\t".join(AGGREGATE_V1.header) + "\n").encode()


def test_build_aggregate_preserves_conflicting_retirement_evidence() -> None:
    records = build_aggregate(
        (),
        (
            {
                "service_health_event_id": "event-1",
                "source_system": "azure_service_health",
                "tracking_id": "track-1",
                "subscription_id": SUBSCRIPTION,
                "retirement_date": "",
                "retirement_date_raw": "conflict:2026-09-30,2026-10-01",
                "retirement_date_source": "conflicting:properties.description,properties.title",
                "retirement_date_quality": "conflict",
                "raw_record_ref": "health-ref",
            },
        ),
        context=context(),
        catalog=catalog(),
    )

    assert records[0]["retirement_date_quality"] == "conflict"
    claims = json.loads(records[0]["retirement_dates_json"])
    assert claims == [
        {
            "date": "",
            "raw_value": "conflict:2026-09-30,2026-10-01",
            "quality": "conflict",
            "raw_record_refs": ["health-ref"],
            "source_path": "conflicting:properties.description,properties.title",
            "source_system": "azure_service_health",
        }
    ]


def test_build_aggregate_preserves_partial_retirement_evidence() -> None:
    records = build_aggregate(
        (),
        (
            {
                "service_health_event_id": "event-1",
                "source_system": "azure_service_health",
                "tracking_id": "track-1",
                "subscription_id": SUBSCRIPTION,
                "retirement_date": "",
                "retirement_date_raw": "2026-09",
                "retirement_date_source": "properties.article.articleContent",
                "retirement_date_quality": "partial",
                "raw_record_ref": "health-ref",
            },
        ),
        context=context(),
        catalog=catalog(),
    )

    assert records[0]["retirement_date_quality"] == "partial"
    claims = json.loads(records[0]["retirement_dates_json"])
    assert claims[0]["raw_value"] == "2026-09"
    assert claims[0]["quality"] == "partial"




def test_aggregate_projects_titles_impacts_dates_and_normalized_source_links() -> None:
    advisor_records = ({
        "advisor_recommendation_id": "advisor-1",
        "recommendation_type_id": "retirement-1",
        "short_description_problem": "Advisor retirement problem",
        "impact": "High",
        "retirement_date": "2027-01-01",
        "last_updated": "2026-09-20T12:00:00Z",
        "learn_more_link": "https://learn.example/advisor/",
        "source_health_ash_urls": ["https://app.azure.com/h/notice-1/"],
        "raw_record_ref": "advisor-ref",
    },)
    health_records = ({
        "service_health_event_id": "health-1",
        "tracking_id": "notice-1",
        "title": "Service Health retirement notice",
        "retirement_date": "2027-02-01",
        "impact_start_time": "2026-08-01T00:00:00Z",
        "impact_mitigation_time": "2026-10-01T00:00:00Z",
        "source_link": "https://learn.example/health/",
        "raw_record_ref": "health-ref",
    },)

    advisor_acquisition = SimpleNamespace(
        records=advisor_records,
        companion_records=(
            {
                "raw_record_ref": "advisor-ref",
                "advisor_metadata": {
                    "sourceProperties": {
                        "serviceRetirement": {
                            "serviceHealth": {"ashUrls": ["https://app.azure.com/h/notice-1/"]},
                        },
                    },
                },
                "recommendation": {
                    "properties": {
                        "extendedProperties": {
                            "recommendedActionLearnMore": "https://learn.example/action/",
                        },
                    },
                },
            },
        ),
    )
    records = build_aggregate(
        advisor_acquisition,
        health_records,
        context=context(),
        catalog=catalog(),
    )

    assert len(records) == 1
    row = records[0]
    assert json.loads(row["problem_titles_json"]) == [
        "Advisor retirement problem",
        "Service Health retirement notice",
    ]
    assert json.loads(row["advisor_impacts_json"]) == ["High"]
    assert json.loads(row["date_events_json"]) == [
        {"date": "2026-08-01", "kind": "notice_start", "source": "service-health"},
        {"date": "2026-09-20", "kind": "last_updated", "source": "advisor"},
        {"date": "2026-10-01", "kind": "notice_end", "source": "service-health"},
        {"date": "2027-01-01", "kind": "retirement", "source": "advisor"},
        {"date": "2027-02-01", "kind": "retirement", "source": "service-health"},
    ]
    assert json.loads(row["source_links_json"]) == [
        "https://app.azure.com/h/notice-1",
        "https://learn.example/action",
        "https://learn.example/advisor",
        "https://learn.example/health",
    ]
