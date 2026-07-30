from __future__ import annotations

from src.comitato.comitato_azure_retirements_v2.domain.platforms import (
    PlatformAssignment,
    PlatformCatalogSnapshot,
    SubscriptionId,
    project_platforms,
)


SUB_A = "11111111-1111-1111-1111-111111111111"
SUB_B = "22222222-2222-2222-2222-222222222222"


def test_platform_projection_is_canonical_and_global_is_explicit() -> None:
    catalog = PlatformCatalogSnapshot(
        schema_version=1,
        sha256="a" * 64,
        assignments=(
            PlatformAssignment(SubscriptionId(SUB_B), "Zeta", "B-name"),
            PlatformAssignment(SubscriptionId(SUB_A), "Alpha", "A-name"),
        ),
    )

    projected = project_platforms(
        (SubscriptionId(SUB_B), SubscriptionId(SUB_A)), False, catalog
    )
    assert projected.is_valid
    assert projected.value is not None
    assert projected.value.platforms == ("Alpha", "Zeta")
    assert projected.value.platforms_subscriptions == {
        "Alpha": ({"subscription_id": SUB_A, "subscription_name": "A-name"},),
        "Zeta": ({"subscription_id": SUB_B, "subscription_name": "B-name"},),
    }

    global_projection = project_platforms((), True, catalog)
    assert global_projection.is_valid
    assert global_projection.value is not None
    assert global_projection.value.platforms == ("ALL",)
    assert global_projection.value.platforms_subscriptions == {"ALL": ()}


def test_platform_projection_reports_unmapped_uuid() -> None:
    catalog = PlatformCatalogSnapshot(schema_version=1, sha256="a" * 64, assignments=())
    result = project_platforms((SubscriptionId(SUB_A),), False, catalog)
    assert not result.is_valid
    assert result.diagnostics[0].code == "platform_mapping_unmapped_subscription"
