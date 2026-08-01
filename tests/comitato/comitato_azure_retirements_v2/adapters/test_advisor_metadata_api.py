from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from src.comitato.comitato_azure_retirements_v2.adapters.advisor_metadata_api import (
    AdvisorMetadataApiSource,
    flatten_metadata_items,
)
from src.comitato.comitato_azure_retirements_v2.adapters.arm_http import ArmPageEnvelope
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


class RecordingHttp:
    def __init__(self, pages: tuple[ArmPageEnvelope, ...]) -> None:
        self.pages = pages
        self.calls: list[tuple[str, dict[str, str], str]] = []

    def list_pages(self, url: str, *, params: dict[str, str], run_id: str) -> tuple[ArmPageEnvelope, ...]:
        self.calls.append((url, params, run_id))
        return self.pages


def context() -> RunContext:
    request = RunRequest(ReportSelector.ADVISOR, ("sub-a",), date(2026, 7, 31))
    return RunContext(
        run_id="run-1",
        as_of_date=date(2026, 7, 31),
        created_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
        request=request,
        scope=Scope(("sub-a",), mode="explicit"),
        catalog_identity=CatalogIdentity(1, "0" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "advisor")),
    )


def test_metadata_source_uses_the_retirement_filter_and_ibiza_expansion() -> None:
    url = "https://management.azure.com/providers/Microsoft.Advisor/metadata"
    http = RecordingHttp(
        pages=(
            ArmPageEnvelope(
                f"{url}?page=1",
                (
                    {
                        "id": "metadata-parent",
                        "properties": {
                            "supportedValues": [
                                {
                                    "id": "service-a",
                                    "sourceProperties": {
                                        "serviceRetirement": {"serviceId": "service-a"}
                                    },
                                }
                            ]
                        },
                    },
                ),
                f"{url}?page=2",
            ),
            ArmPageEnvelope(f"{url}?page=2", ({"id": "service-b"},)),
        )
    )

    rows = AdvisorMetadataApiSource(http).acquire(context())

    assert [row["id"] for row in rows] == ["service-a", "service-b"]
    assert http.calls == [
        (
            url,
            {
                "api-version": "2025-01-01",
                "$filter": "recommendationCategory eq 'HighAvailability' and recommendationSubCategory eq 'ServiceUpgradeAndRetirement'",
                "$expand": "ibiza",
            },
            "run-1",
        )
    ]


def test_flatten_metadata_items_accepts_top_level_and_nested_supported_values() -> None:
    rows = flatten_metadata_items(
        (
            {"id": "parent", "supportedValues": [{"id": "child"}]},
            {"id": "nested-parent", "properties": {"supportedValues": [{"id": "nested-child"}]}},
            {"id": "plain"},
        )
    )

    assert [row["id"] for row in rows] == ["child", "nested-child", "plain"]


def test_flatten_metadata_items_rejects_non_mapping_supported_values() -> None:
    with pytest.raises(ValueError, match="supportedValues"):
        flatten_metadata_items(({"supportedValues": [{"id": "valid"}, "invalid"]},))
