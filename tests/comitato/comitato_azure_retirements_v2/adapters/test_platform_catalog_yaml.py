from __future__ import annotations

from pathlib import Path

import pytest

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
