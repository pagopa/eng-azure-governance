from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.comitato.comitato_azure_retirements.libs.platform_catalog import (
    load_active_subscription_platform_map,
)


def _write_catalog(tmp_path: Path, payload: object) -> Path:
    catalog_path = tmp_path / "eng-finops-platforms.yaml"
    catalog_path.write_text(
        yaml.safe_dump(payload, sort_keys=False),
        encoding="utf-8",
    )
    return catalog_path


def test_load_active_subscription_platform_map_uses_schema_v1_active_entries_only(
    tmp_path: Path,
) -> None:
    catalog_path = _write_catalog(
        tmp_path,
        {
            "schema_version": 1,
            "platforms": {
                "IO": {
                    "subscriptions": [
                        {
                            "name": "PROD-IO",
                            "id": "ec285037-c673-4f58-b594-d7c480da4e8b",
                            "state": "active",
                        },
                        {"name": "Unassigned", "id": None, "state": "disabled"},
                        {
                            "name": "OLD-IO",
                            "id": "000df80e-d061-4064-998e-d4e32146d17b",
                            "state": "deleted",
                        },
                    ]
                },
                "PCI": {"subscriptions": []},
            },
        },
    )

    mapping = load_active_subscription_platform_map(catalog_path)

    assert mapping == {"prod-io": "IO"}


def test_canonical_eng_finops_catalog_has_accepted_active_assignments() -> None:
    repository_root = Path(__file__).resolve().parents[3]
    catalog_path = (
        repository_root / "src" / "_source_of_truth" / "eng-finops-platforms.yaml"
    )

    mapping = load_active_subscription_platform_map(catalog_path)

    assert len(mapping) == 54
    assert {
        name: mapping[name]
        for name in (
            "dev-arc",
            "uat-arc",
            "prod-arc",
            "dev-p4pa",
            "uat-p4pa",
            "prod-p4pa",
            "dev-devex",
            "dev-engineering",
            "uat-devex",
            "prod-devex",
            "prod-trial",
            "uat-esercenti",
            "prod-esercenti",
        )
    } == {
        "dev-arc": "Piattaforma Unitaria",
        "uat-arc": "Piattaforma Unitaria",
        "prod-arc": "Piattaforma Unitaria",
        "dev-p4pa": "Piattaforma Unitaria",
        "uat-p4pa": "Piattaforma Unitaria",
        "prod-p4pa": "Piattaforma Unitaria",
        "dev-devex": "DEVEX",
        "dev-engineering": "DEVEX",
        "uat-devex": "DEVEX",
        "prod-devex": "DEVEX",
        "prod-trial": "DEVEX",
        "uat-esercenti": "IO",
        "prod-esercenti": "IO",
    }
    assert "dev-itwallet" not in mapping
    assert "dev-mil" not in mapping
    assert "unassigned" not in mapping


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({}, "schema_version"),
        (
            {"schema_version": 2, "platforms": {}},
            "unsupported schema_version",
        ),
        (
            {
                "schema_version": 1,
                "platforms": {
                    "IO": {
                        "subscriptions": [
                            {
                                "name": "PROD-IO",
                                "id": "ec285037-c673-4f58-b594-d7c480da4e8b",
                                "state": "paused",
                            }
                        ]
                    }
                },
            },
            "state",
        ),
        (
            {
                "schema_version": 1,
                "platforms": {
                    "IO": {
                        "subscriptions": [
                            {"name": "PROD-IO", "id": None, "state": "active"}
                        ]
                    }
                },
            },
            "active subscription id",
        ),
        (
            {
                "schema_version": 1,
                "platforms": {
                    "IO": {
                        "subscriptions": [
                            {
                                "name": "PROD-IO",
                                "id": "not-a-uuid",
                                "state": "active",
                            }
                        ]
                    }
                },
            },
            "UUID",
        ),
    ],
)
def test_catalog_rejects_invalid_schema_v1_values(
    tmp_path: Path,
    payload: object,
    message: str,
) -> None:
    catalog_path = _write_catalog(tmp_path, payload)

    with pytest.raises(ValueError, match=message):
        load_active_subscription_platform_map(catalog_path)


def test_catalog_rejects_normalized_active_name_collision(tmp_path: Path) -> None:
    catalog_path = _write_catalog(
        tmp_path,
        {
            "schema_version": 1,
            "platforms": {
                "IO": {
                    "subscriptions": [
                        {
                            "name": "PROD-IO",
                            "id": "ec285037-c673-4f58-b594-d7c480da4e8b",
                            "state": "active",
                        }
                    ]
                },
                "Other": {
                    "subscriptions": [
                        {
                            "name": " prod-io ",
                            "id": "74da48a3-b0e7-489d-8172-da79801086ed",
                            "state": "active",
                        }
                    ]
                },
            },
        },
    )

    with pytest.raises(ValueError, match="duplicate active subscription name"):
        load_active_subscription_platform_map(catalog_path)


def test_catalog_rejects_duplicate_non_null_id(tmp_path: Path) -> None:
    duplicate_id = "ec285037-c673-4f58-b594-d7c480da4e8b"
    catalog_path = _write_catalog(
        tmp_path,
        {
            "schema_version": 1,
            "platforms": {
                "IO": {
                    "subscriptions": [
                        {"name": "PROD-IO", "id": duplicate_id, "state": "active"}
                    ]
                },
                "Other": {
                    "subscriptions": [
                        {
                            "name": "PROD-OTHER",
                            "id": duplicate_id,
                            "state": "disabled",
                        }
                    ]
                },
            },
        },
    )

    with pytest.raises(ValueError, match="duplicate subscription id"):
        load_active_subscription_platform_map(catalog_path)
