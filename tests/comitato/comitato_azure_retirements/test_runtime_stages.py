from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements.libs.diagnostics import DiagnosticsCollector
from src.comitato.comitato_azure_retirements.libs.config import RuntimeConfig
from src.comitato.comitato_azure_retirements.libs import runtime_stages
from src.comitato.comitato_azure_retirements.libs.runtime_stages import (
    add_aggregate_contract_diagnostics,
    add_publication_exclusion_diagnostics,
    add_service_health_contract_diagnostics,
    add_slide_source_link_diagnostics,
    diagnostic_summary,
    enforce_mandatory_raw_rows,
    fixture_mode,
    load_slide_stage_inputs,
    load_raw_stage_inputs,
    manifest_degraded_mode,
    require_non_empty_stage_input,
    require_stage_input,
    resolve_optional_legacy_input,
)
from src.comitato.comitato_azure_retirements.libs.schemas import (
    ADVISOR_HEADERS,
    AGGREGATE_HEADERS,
    SERVICE_HEALTH_HEADERS,
)
from src.comitato.comitato_azure_retirements.libs.tsv import write_tsv
from src.comitato.comitato_azure_retirements.libs.workflow_exports import (
    LEGACY_RAW_ADVISOR_FILENAME,
    LEGACY_RAW_SERVICE_HEALTH_FILENAME,
)


def test_diagnostic_summary_and_manifest_degraded_mode() -> None:
    rows = [
        {"severity": "info", "check_id": "some_info"},
        {"severity": "warning", "check_id": "resource_graph_truncated"},
        {"severity": "error", "check_id": "some_error"},
    ]

    assert diagnostic_summary(rows) == {"info": 1, "warning": 1, "error": 1}
    assert manifest_degraded_mode(rows) is True
    assert manifest_degraded_mode([{"check_id": "different_check"}]) is False


def test_fixture_mode_flattens_advisor_metadata_wrapper(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    metadata = {
        "id": "service-1",
        "properties": {"sourceProperties": {"serviceRetirement": {"serviceId": "service-1"}}},
    }
    captured: dict[str, object] = {}
    config = RuntimeConfig(
        mode="fixture",
        workflows=["raw"],
        subscriptions=[],
        management_groups=[],
        output_root=tmp_path,
        as_of_date=date(2026, 7, 28),
        health_query_start=date(2025, 1, 1),
        fixture_dir=tmp_path,
        write_raw_jsonl=False,
        allow_degraded=False,
        verbose=False,
        max_workers=1,
    )

    def load_fixture(path: Path) -> list[dict[str, object]]:
        if path.name == "advisor_metadata.json":
            return [{"properties": {"supportedValues": [metadata]}}]
        return []

    def index_metadata(rows: list[dict[str, object]]) -> tuple[dict[str, object], dict[str, int]]:
        captured["metadata"] = rows
        return {}, {}

    monkeypatch.setattr(runtime_stages, "load_fixture", load_fixture)
    monkeypatch.setattr(runtime_stages, "index_metadata_with_collisions", index_metadata)
    monkeypatch.setattr(runtime_stages, "normalize_advisor_rows", lambda **_: [])
    monkeypatch.setattr(runtime_stages, "normalize_service_health_rows", lambda **_: [])

    fixture_mode(
        cfg=config,
        run_id="run-1",
        output_dir=tmp_path,
        diagnostics=DiagnosticsCollector("run-1"),
    )

    assert captured["metadata"] == [metadata]


def test_fixture_mode_filters_expired_service_health_before_raw_trace(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    events = [
        {
            "name": "9HB8-C00",
            "properties": {
                "eventType": "HealthAdvisory",
                "level": "Warning",
                "status": "Active",
                "impactMitigationTime": "2026-03-31T13:51:10Z",
            },
        },
        {
            "name": "keep-event",
            "properties": {
                "eventType": "HealthAdvisory",
                "level": "Warning",
                "status": "Active",
                "impactMitigationTime": "2026-07-29T00:00:00Z",
            },
        },
    ]
    config = RuntimeConfig(
        mode="fixture",
        workflows=["raw"],
        subscriptions=[],
        management_groups=[],
        output_root=tmp_path,
        as_of_date=date(2026, 7, 28),
        health_query_start=date(2025, 1, 1),
        fixture_dir=tmp_path,
        write_raw_jsonl=False,
        allow_degraded=False,
        verbose=False,
        max_workers=1,
    )

    def load_fixture(path: Path) -> list[dict[str, object]]:
        if path.name == "service_health_events.json":
            return events
        return []

    monkeypatch.setattr(runtime_stages, "load_fixture", load_fixture)
    monkeypatch.setattr(runtime_stages, "normalize_advisor_rows", lambda **_: [])
    monkeypatch.setattr(runtime_stages, "normalize_service_health_rows", lambda **_: [])

    _, _, counts, _, _, service_raw = fixture_mode(
        cfg=config,
        run_id="run-1",
        output_dir=tmp_path,
        diagnostics=DiagnosticsCollector("run-1"),
    )

    assert counts["resource_health_events_collected"] == 2
    assert counts["resource_health_events_retained"] == 1
    assert counts["resource_health_events_expired"] == 1
    assert [item["item"]["name"] for item in service_raw] == ["keep-event"]


class _ErrorReporter:
    def error(self, *_args: object, **_kwargs: object) -> None:
        return None


def test_enforce_mandatory_raw_rows_allows_intentionally_all_expired_service_health() -> None:
    enforce_mandatory_raw_rows(
        diagnostics=DiagnosticsCollector("run-1"),
        reporter=_ErrorReporter(),
        advisor_rows=[{"source_id": "advisor-1"}],
        service_rows=[],
        counts_by_source={
            "resource_health_events_collected": 2,
            "resource_health_events_retained": 0,
            "resource_health_events_expired": 2,
        },
    )


def test_enforce_mandatory_raw_rows_rejects_retained_but_unormalized_service_health() -> None:
    with pytest.raises(RuntimeError, match="Mandatory raw workflow outputs are empty"):
        enforce_mandatory_raw_rows(
            diagnostics=DiagnosticsCollector("run-1"),
            reporter=_ErrorReporter(),
            advisor_rows=[{"source_id": "advisor-1"}],
            service_rows=[],
            counts_by_source={
                "resource_health_events_collected": 1,
                "resource_health_events_retained": 1,
                "resource_health_events_expired": 0,
            },
        )


def test_require_stage_input_and_non_empty_guard_raise_clear_errors(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.tsv"

    with pytest.raises(RuntimeError, match="aggregate workflow requires input file"):
        require_stage_input(missing_path, stage_name="aggregate")

    with pytest.raises(RuntimeError, match="requires non-empty input file"):
        require_non_empty_stage_input([], stage_name="aggregate", path=missing_path)


def test_resolve_optional_legacy_input_prefers_primary_then_legacy(tmp_path: Path) -> None:
    primary_path = tmp_path / "primary.tsv"
    legacy_path = tmp_path / "legacy.tsv"

    assert (
        resolve_optional_legacy_input(primary_path, legacy_filename=legacy_path.name)
        == primary_path
    )

    legacy_path.write_text("legacy", encoding="utf-8")
    assert (
        resolve_optional_legacy_input(primary_path, legacy_filename=legacy_path.name)
        == legacy_path
    )

    primary_path.write_text("primary", encoding="utf-8")
    assert (
        resolve_optional_legacy_input(primary_path, legacy_filename=legacy_path.name)
        == primary_path
    )


def test_load_raw_stage_inputs_reads_non_empty_legacy_files(tmp_path: Path) -> None:
    write_tsv(
        tmp_path / LEGACY_RAW_ADVISOR_FILENAME,
        ADVISOR_HEADERS,
        [{"source_id": "advisor-1", "source_system": "advisor_joined"}],
    )
    write_tsv(
        tmp_path / LEGACY_RAW_SERVICE_HEALTH_FILENAME,
        SERVICE_HEALTH_HEADERS,
        [{"source_id": "event-1", "source_system": "resource_health_events"}],
    )

    advisor_rows, service_rows = load_raw_stage_inputs(tmp_path)

    assert len(advisor_rows) == 1
    assert len(service_rows) == 1
    assert advisor_rows[0]["source_id"] == "advisor-1"
    assert service_rows[0]["source_id"] == "event-1"


def test_load_raw_stage_inputs_maps_legacy_service_description(tmp_path: Path) -> None:
    write_tsv(
        tmp_path / runtime_stages.RAW_ADVISOR_FILENAME,
        ADVISOR_HEADERS,
        [{"source_id": "a"}],
    )
    write_tsv(
        tmp_path / runtime_stages.RAW_SERVICE_HEALTH_FILENAME,
        ["tracking_id", "description"],
        [{"tracking_id": "TRK-1", "description": "Legacy text"}],
    )

    _, service_rows = load_raw_stage_inputs(tmp_path)

    assert service_rows[0]["description_problem"] == "Legacy text"
    assert "description" not in service_rows[0]


def test_load_slide_stage_inputs_reads_advisor_and_service_health_aggregates(
    tmp_path: Path,
) -> None:
    write_tsv(
        tmp_path / runtime_stages.AGGREGATE_FILENAME,
        AGGREGATE_HEADERS,
        [{"technology_or_service": "Advisor service"}],
    )
    write_tsv(
        tmp_path / runtime_stages.SERVICE_HEALTH_SUPPLEMENTAL_FILENAME,
        AGGREGATE_HEADERS,
        [{"technology_or_service": "Health service"}],
    )

    rows = load_slide_stage_inputs(tmp_path)

    assert [row["technology_or_service"] for row in rows] == [
        "Advisor service",
        "Health service",
    ]


def test_contract_diagnostics_flag_gap_and_missing_source_links() -> None:
    diagnostics = DiagnosticsCollector("run-1")

    add_aggregate_contract_diagnostics(
        diagnostics=diagnostics,
        aggregate_rows=[
            {
                "retiring_feature": "",
                "impacted_platforms": "",
                "impacted_subscriptions": "",
                "source_links": "",
                "retirement_date_quality": "derived",
            }
        ],
    )
    add_slide_source_link_diagnostics(
        diagnostics=diagnostics,
        slide_rows=[{"source_links": ""}],
    )

    check_ids = {row["check_id"] for row in diagnostics.rows()}
    assert "aggregate_gap_rows_missing_core_fields" in check_ids
    assert "aggregate_rows_with_derived_retirement_date" in check_ids
    assert "slide_missing_source_links" in check_ids


def test_service_health_contract_diagnostics_flags_every_required_gap() -> None:
    diagnostics = DiagnosticsCollector("run-1")

    add_service_health_contract_diagnostics(
        diagnostics=diagnostics,
        rows=[
            {
                "tracking_id": "",
                "description_problem": "<p>bad</p>",
                "priority": "",
                "subscription_name": "",
                "resource_granularity": "",
                "resource_id": "",
                "resource_group": "",
                "resource_type": "",
            }
        ],
    )

    check_ids = {row["check_id"] for row in diagnostics.rows()}
    assert check_ids == {
        "service_health_blank_tracking_id",
        "service_health_noncanonical_description_problem",
        "service_health_blank_priority",
        "service_health_blank_subscription_name",
        "service_health_blank_resource_contract",
    }


def test_publication_exclusion_diagnostics_are_bounded_and_source_specific() -> None:
    diagnostics = DiagnosticsCollector("run-1")
    add_publication_exclusion_diagnostics(
        diagnostics=diagnostics,
        excluded_by_reason={
            "advisor_not_current": [f"id-{index:03d}" for index in range(105, 0, -1)],
            "expired": ["expired-2", "expired-1", "expired-1"],
            "beyond_one_year": ["future-1"],
            "missing_or_invalid_date": ["invalid-1"],
        },
    )

    rows = diagnostics.rows()
    assert [row["check_id"] for row in rows] == [
        "publication_advisor_not_current",
        "publication_expired",
        "publication_beyond_one_year",
        "publication_missing_or_invalid_date",
    ]
    assert rows[0]["observed_count"] == "105"
    assert json.loads(rows[0]["raw_context_json"]) == {
        "identifiers": [f"id-{index:03d}" for index in range(1, 101)],
        "identifiers_truncated": True,
    }
    assert json.loads(rows[1]["raw_context_json"]) == {
        "identifiers": ["expired-1", "expired-2"]
    }
