"""Runtime stage helpers for schema, fixture, and stage-input reuse flows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .advisor import (
    flatten_advisor_metadata_items,
    index_metadata_with_collisions,
    index_resource_graph,
)
from .concurrency import effective_worker_count
from .config import RuntimeConfig
from .diagnostics import DiagnosticsCollector
from .normalize import normalize_advisor_rows, normalize_service_health_rows
from .runtime_logging import ExecutionReporter
from .schemas import ADVISOR_HEADERS, SERVICE_HEALTH_HEADERS
from .service_health import (
    build_recommended_actions,
    event_impacted_service_regions,
    filter_health_advisory_events,
)
from .service_health_resources import index_impacted_resources
from .subscriptions import build_subscription_name_map
from .tsv import compact_json, read_tsv
from .workflow_exports import (
    AGGREGATE_FILENAME,
    LEGACY_RAW_ADVISOR_FILENAME,
    LEGACY_RAW_SERVICE_HEALTH_FILENAME,
    RAW_ADVISOR_FILENAME,
    RAW_SERVICE_HEALTH_FILENAME,
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


def add_service_health_expired_diagnostic(
    *, diagnostics: DiagnosticsCollector, expired_event_ids: list[str]
) -> None:
    if not expired_event_ids:
        return
    diagnostics.add(
        severity="info",
        check_id="service_health_expired_events_filtered",
        source_system="resource_health_events",
        scope="global",
        message="Service Health events with elapsed End time were excluded before normalization",
        action_required="None",
        observed_count=len(expired_event_ids),
        raw_context_json=compact_json({"tracking_ids": sorted(set(expired_event_ids))}),
    )


def add_publication_exclusion_diagnostics(
    *,
    diagnostics: DiagnosticsCollector,
    excluded_by_reason: dict[str, list[str]],
) -> None:
    for reason in (
        "advisor_not_current",
        "expired",
        "beyond_one_year",
        "missing_or_invalid_date",
    ):
        identifiers = sorted(set(excluded_by_reason.get(reason, [])))
        if not identifiers:
            continue
        context: dict[str, Any] = {"identifiers": identifiers[:100]}
        if len(identifiers) > 100:
            context["identifiers_truncated"] = True
        diagnostics.add(
            severity="info",
            check_id=f"publication_{reason}",
            source_system="publication_window",
            scope="global",
            message=f"Publication rows excluded: {reason}",
            action_required="Review excluded identifiers if the source payload is expected to be current",
            observed_count=len(identifiers),
            raw_context_json=compact_json(context),
        )


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
    service_source_count = counts_by_source.get(
        "resource_health_events_collected",
        counts_by_source["resource_health_events"],
    )
    service_retained_count = counts_by_source.get(
        "resource_health_events_retained",
        counts_by_source.get("resource_health_events", 0),
    )
    service_expired_count = counts_by_source.get("resource_health_events_expired", 0)
    service_intentionally_empty = (
        service_source_count > 0
        and service_retained_count == 0
        and service_expired_count == service_source_count
    )

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
        severity = (
            "warning"
            if service_source_count == 0 or service_intentionally_empty
            else "error"
        )
        diagnostics.add(
            severity=severity,
            check_id="service_rows_empty",
            source_system="resource_health_events",
            scope="global",
            message="Service Health aggregate contains no rows",
            action_required=(
                "No Service Health source rows were returned for the resolved scope"
                if service_source_count == 0
                else "All collected Service Health events were intentionally excluded because their End time elapsed"
                if service_intentionally_empty
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
    counts_by_source: dict[str, int] | None = None,
) -> None:
    source_counts = counts_by_source or {}
    service_collected_count = source_counts.get(
        "resource_health_events_collected",
        source_counts.get("resource_health_events", 0),
    )
    service_retained_count = source_counts.get(
        "resource_health_events_retained",
        source_counts.get("resource_health_events", len(service_rows)),
    )
    service_expired_count = source_counts.get("resource_health_events_expired", 0)
    service_intentionally_empty = (
        not service_rows
        and service_collected_count > 0
        and service_retained_count == 0
        and service_expired_count == service_collected_count
    )
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

    if not service_rows and not service_intentionally_empty:
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


def add_service_health_contract_diagnostics(
    *, diagnostics: DiagnosticsCollector, rows: list[dict[str, str]]
) -> None:
    checks: list[tuple[str, list[int], str]] = []
    blank_tracking = [
        index + 1
        for index, row in enumerate(rows)
        if not row.get("tracking_id", "").strip()
    ]
    noncanonical_description = [
        index + 1
        for index, row in enumerate(rows)
        if not row.get("description_problem", "").isascii()
        or "<" in row.get("description_problem", "")
        or ">" in row.get("description_problem", "")
    ]
    blank_priority = [
        index + 1
        for index, row in enumerate(rows)
        if not row.get("priority", "").strip()
    ]
    blank_subscription = [
        index + 1
        for index, row in enumerate(rows)
        if not row.get("subscription_name", "").strip()
    ]
    blank_resource_contract = [
        index + 1
        for index, row in enumerate(rows)
        if any(
            not row.get(key, "").strip()
            for key in (
                "resource_granularity",
                "resource_id",
                "resource_group",
                "resource_type",
            )
        )
    ]
    blank_resource_resolution_contract = [
        index + 1
        for index, row in enumerate(rows)
        if any(
            not row.get(key, "").strip()
            for key in (
                "resource_resolution_source",
                "resource_resolution_status",
                "recommendation_type_id",
                "advisor_platform_state",
                "current_query_match",
            )
        )
    ]
    checks.extend(
        [
            (
                "service_health_blank_tracking_id",
                blank_tracking,
                "Service Health tracking_id is blank",
            ),
            (
                "service_health_noncanonical_description_problem",
                noncanonical_description,
                "Service Health description_problem is not canonical ASCII text",
            ),
            (
                "service_health_blank_priority",
                blank_priority,
                "Service Health priority is blank",
            ),
            (
                "service_health_blank_subscription_name",
                blank_subscription,
                "Service Health subscription_name is blank",
            ),
            (
                "service_health_blank_resource_contract",
                blank_resource_contract,
                "Service Health resource contract contains a blank field",
            ),
            (
                "service_health_blank_resource_resolution_contract",
                blank_resource_resolution_contract,
                "Service Health resource-resolution contract contains a blank field",
            ),
        ]
    )
    for check_id, row_numbers, message in checks:
        if not row_numbers:
            continue
        diagnostics.add(
            severity="error",
            check_id=check_id,
            source_system="resource_health_events",
            scope="global",
            message=message,
            action_required="Fix Service Health normalization before publication",
            observed_count=len(row_numbers),
            raw_context_json=compact_json({"row_numbers": row_numbers}),
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

    advisor_metadata = flatten_advisor_metadata_items(
        load_fixture(cfg.fixture_dir / "advisor_metadata.json")
    )
    advisor_recommendations = load_fixture(
        cfg.fixture_dir / "advisor_recommendations.json"
    )
    advisor_graph_rows = load_fixture(cfg.fixture_dir / "advisor_resource_graph.json")
    collected_service_health_events = load_fixture(
        cfg.fixture_dir / "service_health_events.json"
    )
    service_health_filter = filter_health_advisory_events(
        collected_service_health_events, as_of_date=cfg.as_of_date
    )
    service_health_events = service_health_filter.events
    add_service_health_expired_diagnostic(
        diagnostics=diagnostics,
        expired_event_ids=service_health_filter.expired_event_ids,
    )
    subscription_rows = load_fixture(cfg.fixture_dir / "subscriptions.json")
    impacted_resource_rows = load_fixture(
        cfg.fixture_dir / "service_health_impacted_resources.json"
    )
    retained_tracking_ids = {
        str(event.get("name") or event.get("id") or "")
        for event in service_health_events
    }
    impacted_resources_by_event = index_impacted_resources(
        impacted_resource_rows,
        tracking_ids=retained_tracking_ids,
    )

    metadata_by_key, metadata_collisions = index_metadata_with_collisions(
        advisor_metadata
    )
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
        subscription_name_map=subscription_name_map,
        include_raw_json=cfg.write_raw_jsonl,
    )

    service_rows = normalize_service_health_rows(
        run_id=run_id,
        as_of_date=cfg.as_of_date,
        scope_mode="fixture",
        events=service_health_events,
        subscription_name_map=subscription_name_map,
        event_impacted_service_regions=event_impacted_service_regions,
        build_recommended_actions=build_recommended_actions,
        impacted_resources_by_event=impacted_resources_by_event,
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
        "resource_health_events_collected": len(collected_service_health_events),
        "resource_health_events_retained": len(service_health_events),
        "resource_health_events_expired": len(service_health_filter.expired_event_ids),
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
        + [
            {"kind": "advisor_recommendation", "item": item}
            for item in advisor_recommendations
        ],
        [
            {"kind": "service_health_event", "item": item}
            for item in service_health_events
        ],
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


def canonicalize_service_health_input_row(row: dict[str, str]) -> dict[str, str]:
    canonical = dict(row)
    if not canonical.get("description_problem", "").strip():
        canonical["description_problem"] = canonical.get("description", "")
    canonical.pop("description", None)
    return canonical


def require_non_empty_stage_input(
    rows: list[dict[str, str]], *, stage_name: str, path: Path
) -> None:
    if rows:
        return
    raise RuntimeError(
        f"{stage_name} workflow requires non-empty input file '{path.name}' in '{path.parent}'. "
        "Run workflow raw in live or fixture mode before aggregate/slide."
    )


def load_raw_stage_inputs(
    output_dir: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
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
    service_rows = [
        canonicalize_service_health_input_row(row)
        for row in read_tsv(service_health_path)
    ]
    require_non_empty_stage_input(
        advisor_rows, stage_name="aggregate", path=advisor_path
    )
    require_non_empty_stage_input(
        service_rows, stage_name="aggregate", path=service_health_path
    )
    return advisor_rows, service_rows


def load_aggregate_stage_input(output_dir: Path) -> list[dict[str, str]]:
    aggregate_path = output_dir / AGGREGATE_FILENAME
    require_stage_input(aggregate_path, stage_name="slide")
    return read_tsv(aggregate_path)


def load_slide_stage_inputs(output_dir: Path) -> list[dict[str, str]]:
    return load_aggregate_stage_input(output_dir)


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
