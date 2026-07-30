from __future__ import annotations

from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2.adapters.platform_catalog_yaml import (
    CatalogLoadError,
    YamlPlatformCatalogSource,
)


def test_yaml_catalog_loads_active_assignments_and_hashes_exact_bytes(tmp_path: Path) -> None:
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
