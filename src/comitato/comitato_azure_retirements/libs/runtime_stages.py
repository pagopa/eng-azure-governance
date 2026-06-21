"""Runtime stage helpers for schema, fixture, and stage-input reuse flows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .advisor import index_metadata_with_collisions, index_resource_graph
from .concurrency import effective_worker_count
from .config import RuntimeConfig
from .diagnostics import DiagnosticsCollector
from .normalize import normalize_advisor_rows, normalize_service_health_rows
from .runtime_logging import ExecutionReporter
from .schemas import ADVISOR_HEADERS, SERVICE_HEALTH_HEADERS
from .service_health import (
    build_recommended_actions,
    event_impacted_regions,
    event_impacted_service_regions,
    event_impacted_services,
    filter_health_advisory_events,
)
from .subscriptions import build_subscription_name_map
from .tsv import compact_json, read_tsv
from .workflow_exports import (
    LEGACY_RAW_ADVISOR_FILENAME,
    LEGACY_RAW_SERVICE_HEALTH_FILENAME,
    RAW_ADVISOR_FILENAME,
    RAW_SERVICE_HEALTH_FILENAME,
    AGGREGATE_FILENAME,
)

MANIFEST_DEGRADED_CHECK_IDS = {
    "advisor_subscription_failures",
    "service_health_subscription_failures",
    "resource_graph_truncated",
}


def diagnostic_summary(rows: list[dict[str, str]]) -> dict[str, int]:
    summary = {"info": 0, "warning": 0, "error": 0}
    for row in rows:
        severity = row.get("severity", "")
        if severity in summary:
            summary[severity] += 1
    return summary


def manifest_degraded_mode(rows: list[dict[str, str]]) -> bool:
    return any(row.get("check_id", "") in MANIFEST_DEGRADED_CHECK_IDS for row in rows)


def empty_rows(headers: list[str]) -> list[dict[str, str]]:
    del headers
    return []


def schema_only(
    cfg: RuntimeConfig,
    run_id: str,
    output_dir: Path,
    diagnostics: DiagnosticsCollector,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int], dict[str, int]]:
    del cfg, run_id, output_dir
    diagnostics.add(
        severity="info",
        check_id="schema_only_mode",
        source_system="global",
        scope="global",
        message="Schema-only mode generated headers without live Azure data rows",
        action_required="Run fixture or live mode for populated aggregates",
    )
    advisor_rows = empty_rows(ADVISOR_HEADERS)
    service_rows = empty_rows(SERVICE_HEALTH_HEADERS)

    counts_by_source = {
        "advisor_metadata": 0,
        "advisor_recommendations": 0,
        "resource_graph_advisorresources": 0,
        "resource_health_events": 0,
    }
    counts_by_file = {
        RAW_ADVISOR_FILENAME: len(advisor_rows),
        RAW_SERVICE_HEALTH_FILENAME: len(service_rows),
        "azure_retirements_run_diagnostics.tsv": len(diagnostics.rows()),
    }

    return advisor_rows, service_rows, counts_by_source, counts_by_file


def add_live_empty_output_diagnostics(
    *,
    diagnostics: DiagnosticsCollector,
    reporter: ExecutionReporter,
    advisor_rows: list[dict[str, str]],
    service_rows: list[dict[str, str]],
    counts_by_source: dict[str, int],
) -> None:
    advisor_source_count = (
        counts_by_source["advisor_metadata"]
        + counts_by_source["advisor_recommendations"]
        + counts_by_source["resource_graph_advisorresources"]
    )
    service_source_count = counts_by_source["resource_health_events"]

    if not advisor_rows:
        severity = "warning" if advisor_source_count == 0 else "error"
        diagnostics.add(
            severity=severity,
            check_id="advisor_rows_empty",
            source_system="advisor_joined",
            scope="global",
            message="Advisor aggregate contains no rows",
            action_required=(
                "No Advisor source rows were returned for the resolved scope"
                if advisor_source_count == 0
                else "Fix Advisor normalization or joins before using this export"
            ),
            observed_count=len(advisor_rows),
            expected_count=advisor_source_count,
        )
        reporter.warning("Advisor aggregate produced zero rows")

    if not service_rows:
        severity = "warning" if service_source_count == 0 else "error"
        diagnostics.add(
            severity=severity,
            check_id="service_rows_empty",
            source_system="resource_health_events",
            scope="global",
            message="Service Health aggregate contains no rows",
            action_required=(
                "No Service Health source rows were returned for the resolved scope"
                if service_source_count == 0
                else "Fix Service Health normalization before using this export"
            ),
            observed_count=len(service_rows),
            expected_count=service_source_count,
        )
        reporter.warning("Service Health aggregate produced zero rows")


def enforce_mandatory_raw_rows(
    *,
    diagnostics: DiagnosticsCollector,
    reporter: ExecutionReporter,
    advisor_rows: list[dict[str, str]],
    service_rows: list[dict[str, str]],
) -> None:
    missing_files: list[str] = []
    if not advisor_rows:
        missing_files.append(RAW_ADVISOR_FILENAME)
        diagnostics.add(
            severity="error",
            check_id="mandatory_advisor_raw_empty",
            source_system="advisor_joined",
            scope="global",
            message="Advisor raw output is empty but mandatory",
            action_required="Collect live or fixture raw data before running aggregate/slide workflows",
        )

    if not service_rows:
        missing_files.append(RAW_SERVICE_HEALTH_FILENAME)
        diagnostics.add(
            severity="error",
            check_id="mandatory_service_health_raw_empty",
            source_system="resource_health_events",
            scope="global",
            message="Service Health raw output is empty but mandatory",
            action_required="Collect live or fixture raw data before running aggregate/slide workflows",
        )

    if not missing_files:
        return

    reporter.error("Mandatory raw outputs are empty: " + ", ".join(missing_files))
    raise RuntimeError(
        "Mandatory raw workflow outputs are empty; rerun in live/fixture mode with valid scope and permissions"
    )


def load_fixture(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("value"), list):
        return payload["value"]
    return []


def fixture_mode(
    cfg: RuntimeConfig,
    run_id: str,
    output_dir: Path,
    diagnostics: DiagnosticsCollector,
) -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    dict[str, int],
    dict[str, int],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    del output_dir
    assert cfg.fixture_dir is not None

    advisor_metadata = load_fixture(cfg.fixture_dir / "advisor_metadata.json")
    advisor_recommendations = load_fixture(cfg.fixture_dir / "advisor_recommendations.json")
    advisor_graph_rows = load_fixture(cfg.fixture_dir / "advisor_resource_graph.json")
    service_health_events = filter_health_advisory_events(
        load_fixture(cfg.fixture_dir / "service_health_events.json")
    )
    subscription_rows = load_fixture(cfg.fixture_dir / "subscriptions.json")

    metadata_by_key, metadata_collisions = index_metadata_with_collisions(advisor_metadata)
    graph_by_key = index_resource_graph(advisor_graph_rows)
    subscription_name_map = build_subscription_name_map(subscription_rows)

    if metadata_collisions:
        diagnostics.add(
            severity="warning",
            check_id="advisor_metadata_key_collisions",
            source_system="advisor_metadata",
            scope="fixture",
            message="Advisor metadata contains duplicated keys; last value wins during indexing",
            action_required="Inspect fixture payload for duplicate metadata IDs or service IDs",
            observed_count=len(metadata_collisions),
            raw_context_json=compact_json(
                {
                    "duplicate_keys": sorted(metadata_collisions.keys()),
                    "collision_events": sum(metadata_collisions.values()),
                }
            ),
        )

    advisor_rows = normalize_advisor_rows(
        run_id=run_id,
        as_of_date=cfg.as_of_date,
        scope_mode="fixture",
        recommendations=advisor_recommendations,
        metadata_by_key=metadata_by_key,
        resource_graph_by_key=graph_by_key,
        include_raw_json=cfg.write_raw_jsonl,
    )

    service_rows = normalize_service_health_rows(
        run_id=run_id,
        as_of_date=cfg.as_of_date,
        scope_mode="fixture",
        events=service_health_events,
        subscription_name_map=subscription_name_map,
        event_impacted_services=event_impacted_services,
        event_impacted_regions=event_impacted_regions,
        event_impacted_service_regions=event_impacted_service_regions,
        build_recommended_actions=build_recommended_actions,
    )

    diagnostics.add(
        severity="info",
        check_id="fixture_mode",
        source_system="global",
        scope="fixture",
        message="Fixture mode completed",
        action_required="Use live mode for production evidence",
        observed_count=len(advisor_rows) + len(service_rows),
    )

    counts_by_source = {
        "advisor_metadata": len(advisor_metadata),
        "advisor_recommendations": len(advisor_recommendations),
        "resource_graph_advisorresources": len(advisor_graph_rows),
        "resource_health_events": len(service_health_events),
    }
    counts_by_file = {
        RAW_ADVISOR_FILENAME: len(advisor_rows),
        RAW_SERVICE_HEALTH_FILENAME: len(service_rows),
        "azure_retirements_run_diagnostics.tsv": len(diagnostics.rows()),
    }

    return (
        advisor_rows,
        service_rows,
        counts_by_source,
        counts_by_file,
        [{"kind": "advisor_metadata", "item": item} for item in advisor_metadata]
        + [{"kind": "advisor_recommendation", "item": item} for item in advisor_recommendations],
        [{"kind": "service_health_event", "item": item} for item in service_health_events],
    )


def require_stage_input(path: Path, *, stage_name: str) -> None:
    if path.exists():
        return
    raise RuntimeError(
        f"{stage_name} workflow requires input file '{path.name}' in '{path.parent}'"
    )


def resolve_optional_legacy_input(primary_path: Path, *, legacy_filename: str) -> Path:
    if primary_path.exists():
        return primary_path
    legacy_path = primary_path.parent / legacy_filename
    if legacy_path.exists():
        return legacy_path
    return primary_path


def require_non_empty_stage_input(rows: list[dict[str, str]], *, stage_name: str, path: Path) -> None:
    if rows:
        return
    raise RuntimeError(
        f"{stage_name} workflow requires non-empty input file '{path.name}' in '{path.parent}'. "
        "Run workflow raw in live or fixture mode before aggregate/slide."
    )


def load_raw_stage_inputs(output_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    advisor_path = resolve_optional_legacy_input(
        output_dir / RAW_ADVISOR_FILENAME,
        legacy_filename=LEGACY_RAW_ADVISOR_FILENAME,
    )
    service_health_path = resolve_optional_legacy_input(
        output_dir / RAW_SERVICE_HEALTH_FILENAME,
        legacy_filename=LEGACY_RAW_SERVICE_HEALTH_FILENAME,
    )
    require_stage_input(advisor_path, stage_name="aggregate")
    require_stage_input(service_health_path, stage_name="aggregate")
    advisor_rows = read_tsv(advisor_path)
    service_rows = read_tsv(service_health_path)
    require_non_empty_stage_input(advisor_rows, stage_name="aggregate", path=advisor_path)
    require_non_empty_stage_input(service_rows, stage_name="aggregate", path=service_health_path)
    return advisor_rows, service_rows


def load_aggregate_stage_input(output_dir: Path) -> list[dict[str, str]]:
    aggregate_path = output_dir / AGGREGATE_FILENAME
    require_stage_input(aggregate_path, stage_name="slide")
    return read_tsv(aggregate_path)


def add_aggregate_contract_diagnostics(
    *, diagnostics: DiagnosticsCollector, aggregate_rows: list[dict[str, str]]
) -> None:
    gap_row_indexes = [
        index + 1
        for index, row in enumerate(aggregate_rows)
        if not row.get("retiring_feature", "").strip()
        and not row.get("impacted_platforms", "").strip()
        and not row.get("impacted_subscriptions", "").strip()
        and not row.get("source_links", "").strip()
    ]
    if gap_row_indexes:
        diagnostics.add(
            severity="error",
            check_id="aggregate_gap_rows_missing_core_fields",
            source_system="aggregate",
            scope="global",
            message="Aggregate rows contain blank feature/platform/subscription/link core fields",
            action_required="Fix normalization/grouping inputs before using aggregate output",
            observed_count=len(gap_row_indexes),
            raw_context_json=compact_json({"row_numbers": gap_row_indexes}),
        )

    derived_date_row_indexes = [
        index + 1
        for index, row in enumerate(aggregate_rows)
        if row.get("retirement_date_quality", "") == "derived"
    ]
    if derived_date_row_indexes:
        diagnostics.add(
            severity="warning",
            check_id="aggregate_rows_with_derived_retirement_date",
            source_system="aggregate",
            scope="global",
            message="Aggregate rows include retirement dates inferred from text",
            action_required="Review derived retirement dates before committee distribution",
            observed_count=len(derived_date_row_indexes),
            raw_context_json=compact_json({"row_numbers": derived_date_row_indexes}),
        )


def add_slide_source_link_diagnostics(
    *, diagnostics: DiagnosticsCollector, slide_rows: list[dict[str, str]]
) -> None:
    missing_source_link_indexes = [
        index + 1
        for index, row in enumerate(slide_rows)
        if not row.get("source_links", "").strip()
    ]
    if not missing_source_link_indexes:
        return

    diagnostics.add(
        severity="error",
        check_id="slide_missing_source_links",
        source_system="slide",
        scope="global",
        message="Slide rows are missing source_links",
        action_required="Populate source links from traceable raw fields or remediate data collection before publishing",
        observed_count=len(missing_source_link_indexes),
        raw_context_json=compact_json({"row_numbers": missing_source_link_indexes}),
    )
