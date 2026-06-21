from __future__ import annotations

from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements.libs.diagnostics import DiagnosticsCollector
from src.comitato.comitato_azure_retirements.libs.runtime_stages import (
    add_aggregate_contract_diagnostics,
    add_slide_source_link_diagnostics,
    diagnostic_summary,
    load_raw_stage_inputs,
    manifest_degraded_mode,
    require_non_empty_stage_input,
    require_stage_input,
    resolve_optional_legacy_input,
)
from src.comitato.comitato_azure_retirements.libs.schemas import (
    ADVISOR_HEADERS,
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
