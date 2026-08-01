from __future__ import annotations

from src.comitato.comitato_azure_retirements_v2.domain.platforms import (
    PlatformAssignment,
    PlatformCatalogSnapshot,
    PlatformProjection,
    SubscriptionId,
    project_platforms,
)
import pytest


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


def test_subscription_id_serializes_canonical_lowercase_uuid() -> None:
    assert SubscriptionId("11111111-1111-1111-1111-111111111111".upper()).value == SUB_A


@pytest.mark.parametrize("value", ["", "not-a-uuid", None, True])
def test_subscription_id_rejects_non_uuid_identity(value: object) -> None:
    with pytest.raises((TypeError, ValueError, AttributeError)):
        SubscriptionId(value)  # type: ignore[arg-type]


def test_platform_assignment_rejects_reserved_all_and_blank_values() -> None:
    with pytest.raises(ValueError, match="ALL"):
        PlatformAssignment(SubscriptionId(SUB_A), "ALL", "A")
    with pytest.raises(ValueError):
        PlatformAssignment(SubscriptionId(SUB_A), " ", "A")
    with pytest.raises(ValueError):
        PlatformAssignment(SubscriptionId(SUB_A), "Alpha", " ")


def test_catalog_rejects_duplicate_assignment_for_one_uuid() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        PlatformCatalogSnapshot(
            schema_version=1,
            sha256="a" * 64,
            assignments=(
                PlatformAssignment(SubscriptionId(SUB_A), "Alpha", "A"),
                PlatformAssignment(SubscriptionId(SUB_A), "Beta", "B"),
            ),
        )


def test_projection_sorts_platforms_and_subscription_breakdown() -> None:
    catalog = PlatformCatalogSnapshot(
        schema_version=1,
        sha256="a" * 64,
        assignments=(
            PlatformAssignment(SubscriptionId(SUB_B), "Alpha", "B"),
            PlatformAssignment(SubscriptionId(SUB_A), "Alpha", "A"),
            PlatformAssignment(SubscriptionId("33333333-3333-3333-3333-333333333333"), "Zeta", "C"),
        ),
    )
    result = project_platforms(
        (SubscriptionId(SUB_B), SubscriptionId(SUB_A)), False, catalog
    )
    assert result.value is not None
    assert result.value.platforms == ("Alpha",)
    assert result.value.platforms_subscriptions["Alpha"] == (
        {"subscription_id": SUB_A, "subscription_name": "A"},
        {"subscription_id": SUB_B, "subscription_name": "B"},
    )


def test_global_projection_is_exact_and_cannot_hide_subscription_ids() -> None:
    catalog = PlatformCatalogSnapshot(schema_version=1, sha256="a" * 64, assignments=())
    assert project_platforms((), True, catalog).value == PlatformProjection(
        ("ALL",), {"ALL": ()}
    )
    result = project_platforms((SubscriptionId(SUB_A),), True, catalog)
    assert not result.is_valid
    assert result.diagnostics[0].code == "global_subscription_conflict"
