from __future__ import annotations

from datetime import date
from hashlib import sha256
from pathlib import Path

import pytest
import yaml

from src.comitato.comitato_azure_retirements_v2.retirements.adapters.filesystem.platform_catalog_yaml import (
    CatalogLoadError,
    YamlPlatformCatalogSource,
)

SUB_A = "11111111-1111-1111-1111-111111111111"
TENANT_ID = "7788edaf-0346-4068-9d79-c868aed15b3d"
CATALOG_PATH = Path("src/_source_of_truth/eng-finops-platforms.yaml")


def test_yaml_catalog_loads_active_assignments_and_hashes_exact_bytes(
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog.yaml"
    data = (
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n"
        f"      - name: A\n        id: {SUB_A}\n        state: active\n"
    ).encode()
    path.write_bytes(data)
    snapshot = YamlPlatformCatalogSource(path).load()
    assert snapshot.sha256 == sha256(data).hexdigest()
    assert snapshot.lookup(SUB_A) == ("Alpha", "A")


def test_yaml_catalog_accepts_tenant_id_without_changing_subscription_mapping(
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(
        f"schema_version: 1\ntenant_id: {TENANT_ID}\n"
        "platforms:\n  Alpha:\n    subscriptions:\n"
        f"      - name: A\n        id: {SUB_A}\n        state: active\n",
        encoding="utf-8",
    )
    assert YamlPlatformCatalogSource(path).load().lookup(SUB_A) == ("Alpha", "A")


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
    snapshot = YamlPlatformCatalogSource(CATALOG_PATH).load()
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
    assert YamlPlatformCatalogSource(CATALOG_PATH).load().lookup(subscription_id) == (
        platform,
        name,
    )


@pytest.mark.parametrize(
    "data",
    [
        "schema_version: 1\nplatforms: {}\nextra: true\n",
        "schema_version: 1\nplatforms:\n  Alpha: {}\n",
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n      - name: A\n        id: null\n        state: active\n",
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n      - name: A\n        id: not-a-uuid\n        state: active\n",
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n"
        f"      - name: A\n        id: {SUB_A}\n        state: unknown\n",
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
        f"      - name: old\n        id: {SUB_A}\n        state: dismiss\n",
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


def test_yaml_catalog_allows_null_id_only_for_dismissed_history(
    tmp_path: Path,
) -> None:
    path = tmp_path / "catalog.yaml"
    path.write_text(
        "schema_version: 1\nplatforms:\n  Alpha:\n    subscriptions:\n"
        "      - name: Unassigned\n        id: null\n        state: dismiss\n",
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
    return {"created_at": None, "disabled_at": None, "deleted_at": None}


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


@pytest.mark.parametrize("state", ["active", "dismiss"])
def test_yaml_catalog_accepts_unknown_lifecycle_without_inventing_dates(
    tmp_path: Path, state: str
) -> None:
    snapshot = YamlPlatformCatalogSource(
        write_lifecycle_catalog(tmp_path, lifecycle_metadata(), state=state)
    ).load()
    assert snapshot.lookup(SUB_A) == (("Alpha", "A") if state == "active" else None)


def test_yaml_catalog_accepts_calendar_creation_date(tmp_path: Path) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle["created_at"] = "2024-02-29"
    assert YamlPlatformCatalogSource(
        write_lifecycle_catalog(tmp_path, lifecycle)
    ).load().lookup(SUB_A) == ("Alpha", "A")


@pytest.mark.parametrize("state", ["disabled", "deleted", "action", "disable"])
def test_yaml_catalog_rejects_obsolete_or_misspelled_states(
    tmp_path: Path, state: str
) -> None:
    with pytest.raises(CatalogLoadError, match="subscription values"):
        YamlPlatformCatalogSource(
            write_lifecycle_catalog(tmp_path, lifecycle_metadata(), state=state)
        ).load()


@pytest.mark.parametrize("field", ["created_at", "disabled_at", "deleted_at"])
@pytest.mark.parametrize(
    "value",
    [
        "0001-01-01",
        "2026-02-30",
        "30-03-2026",
        "2026-3-01",
        "20260330",
        "2026-03-30T00:00:00Z",
        2026,
        False,
        date(2026, 3, 30),
    ],
)
def test_yaml_catalog_rejects_invalid_lifecycle_dates(
    tmp_path: Path, field: str, value: object
) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle[field] = value
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(
            write_lifecycle_catalog(tmp_path, lifecycle, state="dismiss")
        ).load()


@pytest.mark.parametrize(
    "field",
    [
        "purchased_on",
        "date_sources",
        "history_complete",
        "incomplete_reason",
        "activity_periods",
        "platform_assignments",
        "extra",
    ],
)
def test_yaml_catalog_rejects_obsolete_lifecycle_fields(
    tmp_path: Path, field: str
) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle[field] = None
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(write_lifecycle_catalog(tmp_path, lifecycle)).load()


@pytest.mark.parametrize("field", ["created_at", "disabled_at", "deleted_at"])
def test_yaml_catalog_requires_all_three_lifecycle_fields(
    tmp_path: Path, field: str
) -> None:
    lifecycle = lifecycle_metadata()
    del lifecycle[field]
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(write_lifecycle_catalog(tmp_path, lifecycle)).load()


@pytest.mark.parametrize("lifecycle", [[], "unknown", 1])
def test_yaml_catalog_rejects_non_mapping_lifecycle(
    tmp_path: Path, lifecycle: object
) -> None:
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(write_lifecycle_catalog(tmp_path, lifecycle)).load()


@pytest.mark.parametrize(
    ("created", "disabled", "deleted"),
    [
        ("2024-01-01", "2026-03-30", "2026-06-30"),
        ("2024-01-01", "2026-06-30", "2026-06-30"),
        ("2024-01-01", None, "2026-06-30"),
        ("2024-01-01", "2026-03-30", None),
        (None, "2026-03-30", "2026-06-30"),
    ],
)
def test_yaml_catalog_excludes_dismissed_lifecycle_from_active_mapping(
    tmp_path: Path, created: str | None, disabled: str | None, deleted: str | None
) -> None:
    lifecycle = {
        "created_at": created,
        "disabled_at": disabled,
        "deleted_at": deleted,
    }
    assert YamlPlatformCatalogSource(
        write_lifecycle_catalog(tmp_path, lifecycle, state="dismiss")
    ).load().active_ids == ()


@pytest.mark.parametrize(
    ("created", "disabled", "deleted"),
    [
        ("2026-04-01", "2026-03-30", None),
        ("2026-07-01", None, "2026-06-30"),
        (None, "2026-07-01", "2026-06-30"),
    ],
)
def test_yaml_catalog_rejects_out_of_order_known_dates(
    tmp_path: Path, created: str | None, disabled: str | None, deleted: str | None
) -> None:
    lifecycle = {
        "created_at": created,
        "disabled_at": disabled,
        "deleted_at": deleted,
    }
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(
            write_lifecycle_catalog(tmp_path, lifecycle, state="dismiss")
        ).load()


@pytest.mark.parametrize("field", ["disabled_at", "deleted_at"])
def test_yaml_catalog_rejects_closed_dates_for_active_subscription(
    tmp_path: Path, field: str
) -> None:
    lifecycle = lifecycle_metadata()
    lifecycle[field] = "2026-03-30"
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(write_lifecycle_catalog(tmp_path, lifecycle)).load()


@pytest.mark.parametrize(
    "lifecycle",
    [
        None,
        {"created_at": None, "disabled_at": "2026-03-30", "deleted_at": "2026-06-30"},
    ],
)
def test_yaml_catalog_accepts_placeholder_lifecycle(
    tmp_path: Path, lifecycle: object
) -> None:
    assert YamlPlatformCatalogSource(
        write_lifecycle_catalog(tmp_path, lifecycle, state="dismiss", identifier=None)
    ).load().active_ids == ()


def test_yaml_catalog_rejects_null_lifecycle_for_real_subscription(
    tmp_path: Path,
) -> None:
    with pytest.raises(CatalogLoadError, match="lifecycle"):
        YamlPlatformCatalogSource(write_lifecycle_catalog(tmp_path, None)).load()


def test_canonical_catalog_has_only_current_states_and_explicit_lifecycle() -> None:
    payload = yaml.safe_load(CATALOG_PATH.read_text())
    for definition in payload["platforms"].values():
        for item in definition["subscriptions"]:
            assert item["state"] in {"active", "dismiss"}
            assert set(item["lifecycle"]) == set(lifecycle_metadata())
    YamlPlatformCatalogSource(CATALOG_PATH).load()
