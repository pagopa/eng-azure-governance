from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.comitato.comitato_azure_retirements_v2.retirements.adapters.filesystem.platform_catalog_yaml import (
    CatalogLoadError,
    YamlPlatformCatalogSource,
)

SUB_A = "11111111-1111-1111-1111-111111111111"
TENANT_ID = "7788edaf-0346-4068-9d79-c868aed15b3d"


def test_yaml_catalog_loads_active_assignments_and_hashes_exact_bytes(
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog.yaml"
    data = (
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n"
        "      - name: A\n        id: 11111111-1111-1111-1111-111111111111\n        state: active\n"
    ).encode()
    path.write_bytes(data)
    snapshot = YamlPlatformCatalogSource(path).load()
    assert snapshot.sha256
    assert snapshot.lookup("11111111-1111-1111-1111-111111111111") == (
        "Alpha",
        "A",
    )


def test_yaml_catalog_accepts_tenant_id_without_changing_subscription_mapping(
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(
        f"schema_version: 1\ntenant_id: {TENANT_ID}\n"
        "platforms:\n  Alpha:\n    subscriptions:\n"
        "      - name: A\n"
        f"        id: {SUB_A}\n"
        "        state: active\n",
        encoding="utf-8",
    )

    snapshot = YamlPlatformCatalogSource(path).load()

    assert snapshot.lookup(SUB_A) == ("Alpha", "A")


@pytest.mark.parametrize("tenant_id", ["not-a-uuid", '""'])
def test_yaml_catalog_rejects_invalid_tenant_id(tmp_path: Path, tenant_id: str) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(
        f"schema_version: 1\ntenant_id: {tenant_id}\nplatforms: {{}}\n",
        encoding="utf-8",
    )

    with pytest.raises(CatalogLoadError, match="tenant"):
        YamlPlatformCatalogSource(path).load()


def test_yaml_catalog_loads_repository_source_of_truth() -> None:
    snapshot = YamlPlatformCatalogSource(
        Path("src/_source_of_truth/eng-finops-platforms.yaml")
    ).load()
    assert snapshot.lookup("A4E96BCD-59DC-4D66-B2F7-5547AD157C12") == (
        "IO",
        "DEV-IO",
    )
    assert snapshot.lookup("4c6905f7-1596-46a3-bf7a-cbb94494b92d") is None


@pytest.mark.parametrize(
    ("subscription_id", "platform", "name"),
    [
        ("a9a529f9-b18c-454b-ba95-c69c5eba134c", "IO", "COPILOT-IO-APP"),
        ("56ae6b0e-2bd4-4080-a13a-9618c9189d43", "IO", "COPILOT-IO-CARABINIERI"),
        ("89b3e3cf-cd5d-41d7-97d2-8ef2c8532799", "IO", "COPILOT-IO-WALLET"),
        ("3a4cff68-ae8c-4c59-8333-06b4c8952e1f", "IO", "COPILOT-IO-CGN"),
        ("728a1e35-cfa5-4d73-a027-8afa624d3462", "Technology", "MDASH-Evaluation"),
        (
            "7e206bc6-280e-416c-97f3-f1dd5011ad39",
            "Technology",
            "COPILOT-TECHNOLOGY-CLOUD-STRATEGY",
        ),
    ],
)
def test_yaml_catalog_maps_copilot_and_evaluation_subscriptions(
    subscription_id: str, platform: str, name: str
) -> None:
    snapshot = YamlPlatformCatalogSource(
        Path("src/_source_of_truth/eng-finops-platforms.yaml")
    ).load()
    assert snapshot.lookup(subscription_id) == (platform, name)


@pytest.mark.parametrize(
    "data",
    [
        "schema_version: 1\nplatforms: {}\nextra: true\n",
        "schema_version: 1\nplatforms:\n  Alpha: {}\n",
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n      - name: A\n        id: null\n        state: active\n",
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n      - name: A\n        id: not-a-uuid\n        state: active\n",
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n      - name: A\n        id: "
        + SUB_A
        + "\n        state: unknown\n",
    ],
)
def test_yaml_catalog_rejects_invalid_entry_values(tmp_path: Path, data: str) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(data, encoding="utf-8")
    with pytest.raises(CatalogLoadError):
        YamlPlatformCatalogSource(path).load()


def test_yaml_catalog_rejects_duplicate_uuid_across_states(tmp_path: Path) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n"
        f"      - name: A\n        id: {SUB_A}\n        state: active\n"
        f"      - name: old\n        id: {SUB_A}\n        state: deleted\n",
        encoding="utf-8",
    )
    with pytest.raises(CatalogLoadError, match="duplicate"):
        YamlPlatformCatalogSource(path).load()


@pytest.mark.parametrize(
    "duplicate_name", ["alpha beta", " alpha  beta ", "alpha\tbeta"]
)
def test_yaml_catalog_rejects_duplicate_active_names_after_normalization(
    tmp_path: Path,
    duplicate_name: str,
) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n"
        f"      - name: Alpha Beta\n        id: {SUB_A}\n        state: active\n"
        "  Beta:\n    subscriptions:\n"
        f'      - name: "{duplicate_name}"\n'
        "        id: 22222222-2222-2222-2222-222222222222\n        state: active\n",
        encoding="utf-8",
    )
    with pytest.raises(CatalogLoadError, match="duplicate"):
        YamlPlatformCatalogSource(path).load()


def test_yaml_catalog_allows_null_id_only_for_non_active_history(
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n"
        "      - name: Unassigned\n        id: null\n        state: disabled\n",
        encoding="utf-8",
    )
    assert YamlPlatformCatalogSource(path).load().active_ids == ()


def test_yaml_catalog_accepts_valid_empty_mapping(tmp_path: Path) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text("schema_version: 1\nplatforms: {}\n", encoding="utf-8")
    assert YamlPlatformCatalogSource(path).load().active_ids == ()


@pytest.mark.parametrize(
    "data",
    [
        "schema_version: 2\nplatforms: {}\n",
        "schema_version: 1\nplatforms:\n  ALL:\n    subscriptions: []\n",
        "schema_version: 1\nplatforms:\n  Alpha: nope\n",
    ],
)
def test_yaml_catalog_rejects_non_v1_shapes(tmp_path: Path, data: str) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(data, encoding="utf-8")
    with pytest.raises(CatalogLoadError):
        YamlPlatformCatalogSource(path).load()


def lifecycle_metadata() -> dict[str, object]:
    return {
        "purchased_on": None,
        "created_at": None,
        "disabled_at": None,
        "deleted_at": None,
        "date_sources": {},
        "history_complete": False,
        "incomplete_reason": "Historical events are not available.",
        "activity_periods": [],
        "platform_assignments": [],
    }


def write_lifecycle_catalog(
    tmp_path: Path,
    lifecycle: object,
    *,
    state: str = "active",
    identifier: str | None = SUB_A,
) -> Path:
    path = tmp_path / "catalog.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "platforms": {
                    "Alpha": {
                        "subscriptions": [
                            {
                                "name": "A",
                                "id": identifier,
                                "state": state,
                                "lifecycle": lifecycle,
                            }
                        ]
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_yaml_catalog_accepts_unknown_lifecycle_without_inventing_dates(
    tmp_path: Path,
) -> None:
    path = write_lifecycle_catalog(tmp_path, lifecycle_metadata())
    assert YamlPlatformCatalogSource(path).load().lookup(SUB_A) == ("Alpha", "A")


def test_yaml_catalog_accepts_reactivation_and_platform_transfer_history(
    tmp_path: Path,
) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle.update(
        {
            "created_at": "2020-01-01T00:00:00Z",
            "disabled_at": "2021-01-01T00:00:00Z",
            "date_sources": {
                "created_at": "Archived creation event",
                "disabled_at": "Archived cancellation event",
            },
            "history_complete": True,
            "incomplete_reason": None,
            "activity_periods": [
                {
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2021-01-01T00:00:00Z",
                    "source": "Archived events",
                },
                {
                    "started_at": "2022-01-01T00:00:00Z",
                    "ended_at": None,
                    "source": "Archived reactivation event",
                },
            ],
            "platform_assignments": [
                {
                    "platform": "Previous",
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2022-01-01T00:00:00Z",
                    "source": "Approved assignment",
                },
                {
                    "platform": "Alpha",
                    "started_at": "2022-01-01T00:00:00Z",
                    "ended_at": None,
                    "source": "Approved transfer",
                },
            ],
        }
    )
    path = write_lifecycle_catalog(tmp_path, lifecycle)
    assert YamlPlatformCatalogSource(path).load().lookup(SUB_A) == ("Alpha", "A")


@pytest.mark.parametrize("state", ["disabled", "deleted"])
def test_yaml_catalog_keeps_inactive_unknown_history_out_of_current_mapping(
    tmp_path: Path, state: str
) -> None:
    path = write_lifecycle_catalog(tmp_path, lifecycle_metadata(), state=state)
    assert YamlPlatformCatalogSource(path).load().lookup(SUB_A) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("created_at", "0001-01-01T00:00:00Z"),
        ("created_at", "2026-02-30T00:00:00Z"),
        ("created_at", "2020-01-01"),
        ("created_at", "2020-01-01T00:00:00"),
        ("created_at", 2020),
        ("created_at", "2020-01-01T00:00:00Z"),
        ("purchased_on", "0001-01-01"),
        ("purchased_on", "2021-02-30"),
        ("purchased_on", "02/07/2021"),
        ("purchased_on", "2021-07-02"),
        ("history_complete", "false"),
        ("history_complete", True),
        ("incomplete_reason", None),
        (
            "activity_periods",
            [{"started_at": None, "ended_at": None, "source": "Unknown"}],
        ),
        (
            "activity_periods",
            [
                {
                    "started_at": "2022-01-01T00:00:00Z",
                    "ended_at": "2021-01-01T00:00:00Z",
                    "source": "Events",
                }
            ],
        ),
        (
            "activity_periods",
            [
                {
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": None,
                    "source": "Events",
                },
                {
                    "started_at": "2021-01-01T00:00:00Z",
                    "ended_at": None,
                    "source": "Events",
                },
            ],
        ),
        (
            "activity_periods",
            [
                {
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2022-01-01T00:00:00Z",
                    "source": "Events",
                },
                {
                    "started_at": "2021-01-01T00:00:00Z",
                    "ended_at": "2023-01-01T00:00:00Z",
                    "source": "Events",
                },
            ],
        ),
        ("activity_periods", {}),
        (
            "activity_periods",
            [{"started_at": "2020-01-01T00:00:00Z", "ended_at": None, "source": ""}],
        ),
        (
            "activity_periods",
            [
                {
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2020-01-01T00:00:00Z",
                    "source": "Events",
                }
            ],
        ),
        (
            "platform_assignments",
            [
                {
                    "platform": "",
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": None,
                    "source": "Events",
                }
            ],
        ),
        ("date_sources", {"created_at": "No corresponding date"}),
        ("extra", True),
    ],
)
def test_yaml_catalog_rejects_invalid_lifecycle(
    tmp_path: Path, field: str, value: object
) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle[field] = value
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(write_lifecycle_catalog(tmp_path, lifecycle)).load()


def test_yaml_catalog_rejects_lifecycle_dates_before_creation(tmp_path: Path) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle.update(
        {
            "created_at": "2022-01-01T00:00:00Z",
            "disabled_at": "2021-01-01T00:00:00Z",
            "date_sources": {
                "created_at": "Creation event",
                "disabled_at": "Disable event",
            },
        }
    )
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(
            write_lifecycle_catalog(tmp_path, lifecycle, state="disabled")
        ).load()


def test_yaml_catalog_accepts_not_applicable_lifecycle_only_for_placeholder(
    tmp_path: Path,
) -> None:
    assert (
        YamlPlatformCatalogSource(
            write_lifecycle_catalog(tmp_path, None, state="disabled", identifier=None)
        )
        .load()
        .active_ids
        == ()
    )
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(write_lifecycle_catalog(tmp_path, None)).load()


def test_canonical_catalog_has_explicit_lifecycle_for_every_record() -> None:
    payload = yaml.safe_load(
        Path("src/_source_of_truth/eng-finops-platforms.yaml").read_text()
    )
    for definition in payload["platforms"].values():
        for item in definition["subscriptions"]:
            assert "lifecycle" in item
            if item["id"] is None:
                assert item["lifecycle"] is None
            else:
                assert set(item["lifecycle"]) == set(lifecycle_metadata())
                if not item["lifecycle"]["history_complete"]:
                    assert item["lifecycle"]["incomplete_reason"]


@pytest.mark.parametrize("state", ["disabled", "deleted"])
def test_yaml_catalog_accepts_complete_closed_lifecycle(
    tmp_path: Path, state: str
) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle.update(
        {
            "created_at": "2020-01-01T00:00:00Z",
            "disabled_at": "2021-01-01T00:00:00Z",
            "date_sources": {"created_at": "Creation", "disabled_at": "Disable"},
            "history_complete": True,
            "incomplete_reason": None,
            "activity_periods": [
                {
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2021-01-01T00:00:00Z",
                    "source": "Events",
                },
            ],
            "platform_assignments": [
                {
                    "platform": "Alpha",
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2021-01-01T00:00:00Z",
                    "source": "Assignment",
                },
            ],
        }
    )
    if state == "deleted":
        lifecycle["deleted_at"] = "2022-01-01T00:00:00Z"
        lifecycle["date_sources"] = {
            "created_at": "Creation",
            "disabled_at": "Disable",
            "deleted_at": "Deletion",
        }
    assert (
        YamlPlatformCatalogSource(
            write_lifecycle_catalog(tmp_path, lifecycle, state=state)
        )
        .load()
        .active_ids
        == ()
    )


def test_yaml_catalog_accepts_deletion_without_previous_disable(tmp_path: Path) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle.update(
        {
            "created_at": "2020-01-01T00:00:00Z",
            "deleted_at": "2021-01-01T00:00:00Z",
            "date_sources": {"created_at": "Creation", "deleted_at": "Deletion"},
            "history_complete": True,
            "incomplete_reason": None,
            "activity_periods": [
                {
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2021-01-01T00:00:00Z",
                    "source": "Events",
                },
            ],
            "platform_assignments": [
                {
                    "platform": "Alpha",
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2021-01-01T00:00:00Z",
                    "source": "Assignment",
                },
            ],
        }
    )
    assert (
        YamlPlatformCatalogSource(
            write_lifecycle_catalog(tmp_path, lifecycle, state="deleted")
        )
        .load()
        .active_ids
        == ()
    )


def test_yaml_catalog_accepts_simultaneous_disable_and_deletion(tmp_path: Path) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle.update(
        {
            "created_at": "2020-01-01T00:00:00Z",
            "disabled_at": "2021-01-01T00:00:00Z",
            "deleted_at": "2021-01-01T00:00:00Z",
            "date_sources": {
                "created_at": "Creation",
                "disabled_at": "Disable",
                "deleted_at": "Deletion",
            },
            "history_complete": True,
            "incomplete_reason": None,
            "activity_periods": [
                {
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2021-01-01T00:00:00Z",
                    "source": "Events",
                },
            ],
            "platform_assignments": [
                {
                    "platform": "Alpha",
                    "started_at": "2020-01-01T00:00:00Z",
                    "ended_at": "2021-01-01T00:00:00Z",
                    "source": "Assignment",
                },
            ],
        }
    )
    assert (
        YamlPlatformCatalogSource(
            write_lifecycle_catalog(tmp_path, lifecycle, state="deleted")
        )
        .load()
        .active_ids
        == ()
    )


def test_yaml_catalog_rejects_ongoing_activity_for_disabled_subscription(
    tmp_path: Path,
) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle["activity_periods"] = [
        {
            "started_at": "2020-01-01T00:00:00Z",
            "ended_at": None,
            "source": "Activation event",
        }
    ]
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(
            write_lifecycle_catalog(tmp_path, lifecycle, state="disabled")
        ).load()


def test_yaml_catalog_rejects_ongoing_assignment_to_another_platform(
    tmp_path: Path,
) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle["platform_assignments"] = [
        {
            "platform": "Other",
            "started_at": "2020-01-01T00:00:00Z",
            "ended_at": None,
            "source": "Assignment record",
        }
    ]
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(write_lifecycle_catalog(tmp_path, lifecycle)).load()


def test_yaml_catalog_accepts_purchase_date_without_inventing_creation_instant(
    tmp_path: Path,
) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle.update(
        {
            "purchased_on": "2021-07-02",
            "date_sources": {"purchased_on": "Azure portal Properties screenshot"},
        }
    )
    assert YamlPlatformCatalogSource(
        write_lifecycle_catalog(tmp_path, lifecycle)
    ).load().lookup(SUB_A) == ("Alpha", "A")
    assert lifecycle["created_at"] is None


def test_canonical_org_purchase_date_matches_user_supplied_portal_evidence() -> None:
    payload = yaml.safe_load(
        Path("src/_source_of_truth/eng-finops-platforms.yaml").read_text()
    )
    org = next(
        item
        for item in payload["platforms"]["Technology"]["subscriptions"]
        if item["name"] == "ORG"
    )
    assert org["lifecycle"]["purchased_on"] == "2021-07-02"
    assert org["lifecycle"]["created_at"] is None
    assert "screenshot" in org["lifecycle"]["date_sources"]["purchased_on"]
