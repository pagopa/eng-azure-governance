import json
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
