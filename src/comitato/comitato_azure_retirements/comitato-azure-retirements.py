#!/usr/bin/env python3
"""Export Azure retirements into separated Advisor and Service Health aggregate TSV files."""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from typing import Any

from libs.advisor import (
    ADVISOR_API_VERSION,
    collect_advisor_metadata,
    collect_advisor_recommendations,
    collect_advisor_resource_graph,
    index_metadata,
    index_resource_graph,
)
from libs.arm_client import ArmClient
from libs.auth import get_management_token
from libs.config import RuntimeConfig, parse_args
from libs.debug_log import DebugRunLogger
from libs.diagnostics import DiagnosticsCollector, build_manifest, utc_now
from libs.normalize import normalize_advisor_rows, normalize_service_health_rows
from libs.runtime_logging import ExecutionReporter
from libs.schemas import AGGREGATE_HEADERS, ADVISOR_HEADERS, DIAGNOSTICS_HEADERS, SERVICE_HEALTH_HEADERS, SLIDE_HEADERS
from libs.service_health import (
    RESOURCE_HEALTH_API_VERSION,
    build_recommended_actions,
    collect_events_for_subscriptions,
    event_impacted_regions,
    event_impacted_services,
    filter_health_advisory_events,
)
from libs.subscriptions import build_subscription_name_map, resolve_scope_subscriptions
from libs.tsv import compact_json, read_tsv, unique_tsv_rows, write_json, write_jsonl, write_tsv
from libs.workflow_exports import (
    AGGREGATE_FILENAME,
    LEGACY_RAW_ADVISOR_FILENAME,
    LEGACY_RAW_SERVICE_HEALTH_FILENAME,
    RAW_ADVISOR_FILENAME,
    RAW_SERVICE_HEALTH_FILENAME,
    SLIDE_FILENAME,
    build_aggregate_rows,
    build_slide_rows,
    load_active_subscription_platform_map,
)


ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME = RAW_ADVISOR_FILENAME
SERVICE_HEALTH_ADVISORIES_RAW_FILENAME = RAW_SERVICE_HEALTH_FILENAME
PLATFORMS_SOURCE_PATH = Path(__file__).resolve().parents[2] / "_source_of_truth" / "platforms.yaml"


def _build_output_dir(root: Path, as_of_date) -> Path:
    return root / as_of_date.strftime("%Y") / as_of_date.strftime("%m")


def _build_runtime_dir(as_of_date) -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "tmp" / "comitato" / "comitato_azure_retirements" / "run" / as_of_date.strftime("%Y") / as_of_date.strftime("%m")


def _build_debug_log_path(runtime_dir: Path, run_id: str) -> Path:
    return runtime_dir / f"{run_id}_debug.log"


def _scope_mode(cfg: RuntimeConfig) -> str:
    if cfg.mode == "fixture":
        return "fixture"
    if cfg.mode == "schema-only":
        return "schema_only"
    if cfg.subscriptions:
        return "subscriptions"
    return "management_groups"


def _diagnostic_summary(rows: list[dict[str, str]]) -> dict[str, int]:
    summary = {"info": 0, "warning": 0, "error": 0}
    for row in rows:
        severity = row.get("severity", "")
        if severity in summary:
            summary[severity] += 1
    return summary


def _empty_rows(headers: list[str]) -> list[dict[str, str]]:
    return [] if headers else []


def _effective_worker_count(subscriptions_count: int, requested_workers: int | None) -> int:
    if subscriptions_count <= 1:
        return 1
    if requested_workers is None:
        return min(16, subscriptions_count)
    return max(1, min(requested_workers, subscriptions_count))


def _schema_only(
    cfg: RuntimeConfig,
    run_id: str,
    output_dir: Path,
    diagnostics: DiagnosticsCollector,
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int], dict[str, int]]:
    diagnostics.add(
        severity="info",
        check_id="schema_only_mode",
        source_system="global",
        scope="global",
        message="Schema-only mode generated headers without live Azure data rows",
        action_required="Run fixture or live mode for populated aggregates",
    )
    advisor_rows = _empty_rows(ADVISOR_HEADERS)
    service_rows = _empty_rows(SERVICE_HEALTH_HEADERS)

    counts_by_source = {
        "advisor_metadata": 0,
        "advisor_recommendations": 0,
        "resource_graph_advisorresources": 0,
        "resource_health_events": 0,
    }
    counts_by_file = {
        ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME: len(advisor_rows),
        SERVICE_HEALTH_ADVISORIES_RAW_FILENAME: len(service_rows),
        "azure_retirements_run_diagnostics.tsv": len(diagnostics.rows()),
    }

    return advisor_rows, service_rows, counts_by_source, counts_by_file


def _add_live_empty_output_diagnostics(
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


def _enforce_mandatory_raw_rows(
    *,
    diagnostics: DiagnosticsCollector,
    reporter: ExecutionReporter,
    advisor_rows: list[dict[str, str]],
    service_rows: list[dict[str, str]],
) -> None:
    missing_files: list[str] = []
    if not advisor_rows:
        missing_files.append(ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME)
        diagnostics.add(
            severity="error",
            check_id="mandatory_advisor_raw_empty",
            source_system="advisor_joined",
            scope="global",
            message="Advisor raw output is empty but mandatory",
            action_required="Collect live or fixture raw data before running aggregate/slide workflows",
        )

    if not service_rows:
        missing_files.append(SERVICE_HEALTH_ADVISORIES_RAW_FILENAME)
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

    reporter.error(
        "Mandatory raw outputs are empty: "
        + ", ".join(missing_files)
    )
    raise RuntimeError(
        "Mandatory raw workflow outputs are empty; rerun in live/fixture mode with valid scope and permissions"
    )


def _load_fixture(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8")
    payload = json.loads(content)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("value"), list):
        return payload["value"]
    return []


def _fixture_mode(
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
    assert cfg.fixture_dir is not None

    advisor_metadata = _load_fixture(cfg.fixture_dir / "advisor_metadata.json")
    advisor_recommendations = _load_fixture(cfg.fixture_dir / "advisor_recommendations.json")
    advisor_graph_rows = _load_fixture(cfg.fixture_dir / "advisor_resource_graph.json")
    service_health_events = filter_health_advisory_events(
        _load_fixture(cfg.fixture_dir / "service_health_events.json")
    )
    subscription_rows = _load_fixture(cfg.fixture_dir / "subscriptions.json")

    metadata_by_key = index_metadata(advisor_metadata)
    graph_by_key = index_resource_graph(advisor_graph_rows)
    subscription_name_map = build_subscription_name_map(subscription_rows)

    advisor_rows = normalize_advisor_rows(
        run_id=run_id,
        as_of_date=cfg.as_of_date,
        scope_mode="fixture",
        recommendations=advisor_recommendations,
        metadata_by_key=metadata_by_key,
        resource_graph_by_key=graph_by_key,
    )

    service_rows = normalize_service_health_rows(
        run_id=run_id,
        as_of_date=cfg.as_of_date,
        scope_mode="fixture",
        events=service_health_events,
        subscription_name_map=subscription_name_map,
        event_impacted_services=event_impacted_services,
        event_impacted_regions=event_impacted_regions,
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
        ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME: len(advisor_rows),
        SERVICE_HEALTH_ADVISORIES_RAW_FILENAME: len(service_rows),
        "azure_retirements_run_diagnostics.tsv": len(diagnostics.rows()),
    }

    return (
        advisor_rows,
        service_rows,
        counts_by_source,
        counts_by_file,
        [
            {"kind": "advisor_metadata", "item": item} for item in advisor_metadata
        ]
        + [{"kind": "advisor_recommendation", "item": item} for item in advisor_recommendations],
        [{"kind": "service_health_event", "item": item} for item in service_health_events],
    )


def _live_mode(
    cfg: RuntimeConfig,
    run_id: str,
    output_dir: Path,
    diagnostics: DiagnosticsCollector,
    reporter: ExecutionReporter,
    debug_logger: DebugRunLogger,
) -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    dict[str, int],
    dict[str, int],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[str],
]:
    reporter.section("🔐", "Authentication", "Acquire the ARM token and prepare the resilient HTTP session")
    reporter.step("Requesting Azure ARM bearer token")
    token = get_management_token()
    client = ArmClient(token, trace_handler=reporter.observe_request)
    reporter.success("ARM client ready with retry-aware HTTP session")

    reporter.section("🧭", "Scope Resolution", "Resolve explicit subscriptions and management group descendants")
    subscriptions, mg_resolution = resolve_scope_subscriptions(
        client,
        explicit_subscriptions=cfg.subscriptions,
        management_groups=cfg.management_groups,
    )
    if not subscriptions:
        raise RuntimeError("No subscriptions resolved from provided scope")
    reporter.step(f"Resolved {len(subscriptions)} subscription(s) for live collection")
    if mg_resolution:
        reporter.mapping(
            "Management group descendants",
            {group: len(items) for group, items in mg_resolution.items()},
            always=True,
        )

    effective_worker_count = _effective_worker_count(len(subscriptions), cfg.max_workers)
    diagnostics.add(
        severity="info",
        check_id="collector_parallelism",
        source_system="global",
        scope="global",
        message="Collector parallelism configured",
        action_required="Tune AZURE_RETIREMENTS_MAX_WORKERS if throttling increases",
        raw_context_json=compact_json(
            {
                "requested_max_workers": cfg.max_workers,
                "effective_max_workers": effective_worker_count,
                "subscriptions_count": len(subscriptions),
            }
        ),
    )
    debug_logger.info(
        "collector_parallelism",
        "Parallel worker configuration resolved",
        requested_max_workers=cfg.max_workers,
        effective_max_workers=effective_worker_count,
        subscriptions_count=len(subscriptions),
    )

    reporter.section(
        "📦",
        "Advisor Collection",
        "Fetch Advisor metadata, recommendations, and Resource Graph enrichment",
    )
    problem_rows: list[dict[str, str]] = []
    advisor_metadata, advisor_metadata_pages = collect_advisor_metadata(client)
    with reporter.subscription_progress("Advisor recommendations", len(subscriptions)) as advisor_progress:
        advisor_recommendations, recommendation_pages, recommendation_failures = collect_advisor_recommendations(
            client,
            subscriptions,
            allow_degraded=cfg.allow_degraded,
            on_subscription_update=advisor_progress,
            max_workers=effective_worker_count,
            debug_logger=debug_logger,
        )
    advisor_graph_rows, advisor_graph_truncated, advisor_graph_pages = collect_advisor_resource_graph(
        client,
        subscriptions=subscriptions,
        management_groups=cfg.management_groups,
    )
    with reporter.subscription_progress("Service Health", len(subscriptions)) as service_progress:
        service_events, service_pages, service_failures = collect_events_for_subscriptions(
            client,
            subscriptions=subscriptions,
            query_start_time=cfg.health_query_start.isoformat(),
            allow_degraded=cfg.allow_degraded,
            on_subscription_update=service_progress,
            max_workers=effective_worker_count,
            debug_logger=debug_logger,
        )
    service_events = filter_health_advisory_events(service_events)
    reporter.step(f"Advisor metadata rows: {len(advisor_metadata)} across {advisor_metadata_pages} page(s)")
    reporter.step(
        "Advisor recommendation rows: "
        f"{len(advisor_recommendations)} across {sum(recommendation_pages.values())} page(s)"
    )
    reporter.step(f"Resource Graph rows: {len(advisor_graph_rows)} across {advisor_graph_pages} page(s)")
    reporter.mapping("Advisor pages by subscription", recommendation_pages)

    reporter.section("🏥", "Service Health Collection", "Fetch Service Health events for the resolved subscriptions")
    reporter.step(
        f"Service Health rows: {len(service_events)} across {sum(service_pages.values())} page(s)"
    )
    reporter.mapping("Service Health pages by subscription", service_pages)

    metadata_by_key = index_metadata(advisor_metadata)
    graph_by_key = index_resource_graph(advisor_graph_rows)

    subscription_name_rows = [
        {
            "subscriptionId": row.get("subscriptionId", ""),
            "subscriptionName": row.get("subscriptionName", ""),
        }
        for row in advisor_graph_rows
    ]
    subscription_name_map = build_subscription_name_map(subscription_name_rows)

    advisor_rows = normalize_advisor_rows(
        run_id=run_id,
        as_of_date=cfg.as_of_date,
        scope_mode=_scope_mode(cfg),
        recommendations=advisor_recommendations,
        metadata_by_key=metadata_by_key,
        resource_graph_by_key=graph_by_key,
    )

    service_rows = normalize_service_health_rows(
        run_id=run_id,
        as_of_date=cfg.as_of_date,
        scope_mode=_scope_mode(cfg),
        events=service_events,
        subscription_name_map=subscription_name_map,
        event_impacted_services=event_impacted_services,
        event_impacted_regions=event_impacted_regions,
        build_recommended_actions=build_recommended_actions,
    )

    diagnostics.add(
        severity="info",
        check_id="advisor_metadata_pages",
        source_system="advisor_metadata",
        scope="global",
        message="Advisor metadata pages fetched",
        action_required="None",
        observed_count=advisor_metadata_pages,
    )

    diagnostics.add(
        severity="info",
        check_id="advisor_recommendation_pages",
        source_system="advisor_recommendations",
        scope="global",
        message="Advisor recommendation pages fetched",
        action_required="None",
        raw_context_json=compact_json(recommendation_pages),
    )

    diagnostics.add(
        severity="info",
        check_id="service_health_pages",
        source_system="resource_health_events",
        scope="global",
        message="Service Health pages fetched",
        action_required="None",
        raw_context_json=compact_json(service_pages),
    )

    if recommendation_failures:
        severity = "warning" if cfg.allow_degraded else "error"
        diagnostics.add(
            severity=severity,
            check_id="advisor_subscription_failures",
            source_system="advisor_recommendations",
            scope="global",
            message="Advisor recommendation collection failed for one or more subscriptions",
            action_required=(
                "Proceed in degraded mode and validate missing subscriptions manually"
                if cfg.allow_degraded
                else "Rerun with --allow-degraded or remediate the failing subscriptions"
            ),
            observed_count=len(recommendation_failures),
            raw_context_json=compact_json(recommendation_failures),
        )
        reporter.warning(
            f"Advisor recommendation collection failed for {len(recommendation_failures)} subscription(s)"
        )
        for failure in recommendation_failures:
            problem_rows.append(
                {
                    "collector": "advisor_recommendations",
                    "subscription": failure.get("subscription_id", ""),
                    "severity": severity,
                    "detail": failure.get("error", ""),
                }
            )

    if service_failures:
        severity = "warning" if cfg.allow_degraded else "error"
        diagnostics.add(
            severity=severity,
            check_id="service_health_subscription_failures",
            source_system="resource_health_events",
            scope="global",
            message="Service Health collection failed for one or more subscriptions",
            action_required=(
                "Proceed in degraded mode and validate missing subscriptions manually"
                if cfg.allow_degraded
                else "Rerun with --allow-degraded or remediate the failing subscriptions"
            ),
            observed_count=len(service_failures),
            raw_context_json=compact_json(service_failures),
        )
        reporter.warning(f"Service Health collection failed for {len(service_failures)} subscription(s)")
        for failure in service_failures:
            problem_rows.append(
                {
                    "collector": "resource_health_events",
                    "subscription": failure.get("subscription_id", ""),
                    "severity": severity,
                    "detail": failure.get("error", ""),
                }
            )

    if problem_rows:
        reporter.warning("Problem determination mini-report generated for warning/error subscriptions")
        reporter.problem_determination_report(
            "🧪 Problem Determination (subscription outcomes)",
            problem_rows,
        )

    if advisor_graph_truncated:
        severity = "warning" if cfg.allow_degraded else "error"
        diagnostics.add(
            severity=severity,
            check_id="resource_graph_truncated",
            source_system="resource_graph_advisorresources",
            scope="global",
            message="Resource Graph reported resultTruncated",
            action_required=(
                "Review pagination evidence and rerun with a narrower scope"
                if not cfg.allow_degraded
                else "Proceed in degraded mode and validate counts manually"
            ),
        )
        reporter.warning("Resource Graph returned truncated results; validate output counts carefully")

    counts_by_source = {
        "advisor_metadata": len(advisor_metadata),
        "advisor_recommendations": len(advisor_recommendations),
        "resource_graph_advisorresources": len(advisor_graph_rows),
        "resource_health_events": len(service_events),
    }
    _add_live_empty_output_diagnostics(
        diagnostics=diagnostics,
        reporter=reporter,
        advisor_rows=advisor_rows,
        service_rows=service_rows,
        counts_by_source=counts_by_source,
    )
    counts_by_file = {
        ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME: len(advisor_rows),
        SERVICE_HEALTH_ADVISORIES_RAW_FILENAME: len(service_rows),
        "azure_retirements_run_diagnostics.tsv": len(diagnostics.rows()),
    }

    advisor_raw = [
        {"kind": "advisor_metadata", "item": item} for item in advisor_metadata
    ] + [{"kind": "advisor_recommendation", "item": item} for item in advisor_recommendations]
    service_raw = [{"kind": "service_health_event", "item": item} for item in service_events]

    return advisor_rows, service_rows, counts_by_source, counts_by_file, advisor_raw, service_raw, subscriptions


def _require_stage_input(path: Path, *, stage_name: str) -> None:
    if path.exists():
        return
    raise RuntimeError(
        f"{stage_name} workflow requires input file '{path.name}' in '{path.parent}'"
    )


def _resolve_optional_legacy_input(primary_path: Path, *, legacy_filename: str) -> Path:
    if primary_path.exists():
        return primary_path
    legacy_path = primary_path.parent / legacy_filename
    if legacy_path.exists():
        return legacy_path
    return primary_path


def _require_non_empty_stage_input(rows: list[dict[str, str]], *, stage_name: str, path: Path) -> None:
    if rows:
        return
    raise RuntimeError(
        f"{stage_name} workflow requires non-empty input file '{path.name}' in '{path.parent}'. "
        "Run workflow raw in live or fixture mode before aggregate/slide."
    )


def _load_raw_stage_inputs(output_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    advisor_path = _resolve_optional_legacy_input(
        output_dir / ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME,
        legacy_filename=LEGACY_RAW_ADVISOR_FILENAME,
    )
    service_health_path = _resolve_optional_legacy_input(
        output_dir / SERVICE_HEALTH_ADVISORIES_RAW_FILENAME,
        legacy_filename=LEGACY_RAW_SERVICE_HEALTH_FILENAME,
    )
    _require_stage_input(advisor_path, stage_name="aggregate")
    _require_stage_input(service_health_path, stage_name="aggregate")
    advisor_rows = read_tsv(advisor_path)
    service_rows = read_tsv(service_health_path)
    _require_non_empty_stage_input(advisor_rows, stage_name="aggregate", path=advisor_path)
    _require_non_empty_stage_input(service_rows, stage_name="aggregate", path=service_health_path)
    return advisor_rows, service_rows


def _load_aggregate_stage_input(output_dir: Path) -> list[dict[str, str]]:
    aggregate_path = output_dir / AGGREGATE_FILENAME
    _require_stage_input(aggregate_path, stage_name="slide")
    return read_tsv(aggregate_path)


def main() -> int:
    cfg = parse_args()

    run_id = f"azure-retirements-{uuid.uuid4()}"
    started_at = utc_now()
    output_dir = _build_output_dir(cfg.output_root, cfg.as_of_date)
    runtime_dir = _build_runtime_dir(cfg.as_of_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    scope_mode = _scope_mode(cfg)
    debug_logger = DebugRunLogger(file_path=_build_debug_log_path(runtime_dir, run_id), run_id=run_id)
    reporter = ExecutionReporter(verbose=cfg.verbose, debug_logger=debug_logger)

    diagnostics = DiagnosticsCollector(run_id)
    diagnostics.add(
        severity="info",
        check_id="debug_log_enabled",
        source_system="global",
        scope="global",
        message="Persistent debug log enabled for this run",
        action_required="Use debug log for timeline-based problem determination",
        raw_context_json=compact_json({"debug_log_path": str(debug_logger.file_path)}),
    )
    reporter.banner(
        run_id=run_id,
        mode=cfg.mode,
        scope_mode=scope_mode,
        output_dir=output_dir,
        subscriptions=cfg.subscriptions,
        management_groups=cfg.management_groups,
        write_raw_jsonl=cfg.write_raw_jsonl,
    )
    debug_logger.info(
        "run_started",
        "Azure retirements run started",
        mode=cfg.mode,
        scope_mode=scope_mode,
        subscriptions=cfg.subscriptions,
        management_groups=cfg.management_groups,
        output_dir=str(output_dir),
        runtime_dir=str(runtime_dir),
        command_line=" ".join(sys.argv),
    )

    try:
        advisor_rows: list[dict[str, str]] = []
        service_rows: list[dict[str, str]] = []
        aggregate_rows: list[dict[str, str]] = []
        slide_rows: list[dict[str, str]] = []
        counts_by_source: dict[str, int] = {
            "advisor_metadata": 0,
            "advisor_recommendations": 0,
            "resource_graph_advisorresources": 0,
            "resource_health_events": 0,
        }
        counts_by_file: dict[str, int] = {}
        advisor_raw_items: list[dict[str, Any]] = []
        service_raw_items: list[dict[str, Any]] = []
        resolved_subscriptions: list[str] = cfg.subscriptions
        selected_workflows = cfg.workflows
        aggregate_stage_ran = False

        reporter.step(f"Selected workflows: {', '.join(selected_workflows)}")
        debug_logger.info(
            "workflow_selection",
            "Resolved workflow selection",
            workflows=selected_workflows,
        )

        if "raw" in selected_workflows:
            if cfg.mode == "schema-only":
                reporter.section("🧪", "Schema-only Mode", "Write empty aggregates with headers and runtime diagnostics")
                reporter.step("Skipping Azure API calls and generating schema artifacts only")
                advisor_rows, service_rows, counts_by_source, _ = _schema_only(
                    cfg=cfg,
                    run_id=run_id,
                    output_dir=output_dir,
                    diagnostics=diagnostics,
                )
                reporter.success("Schema-only artifacts generated")
            elif cfg.mode == "fixture":
                reporter.section(
                    "🧰",
                    "Fixture Mode",
                    "Load local fixture payloads and normalize them into runtime outputs",
                )
                reporter.detail("Fixture directory", str(cfg.fixture_dir), always=True)
                (
                    advisor_rows,
                    service_rows,
                    counts_by_source,
                    _,
                    advisor_raw_items,
                    service_raw_items,
                ) = _fixture_mode(cfg=cfg, run_id=run_id, output_dir=output_dir, diagnostics=diagnostics)
                resolved_subscriptions = cfg.subscriptions
                reporter.success("Fixture inputs normalized successfully")
            else:
                (
                    advisor_rows,
                    service_rows,
                    counts_by_source,
                    _,
                    advisor_raw_items,
                    service_raw_items,
                    resolved_subscriptions,
                ) = _live_mode(
                    cfg=cfg,
                    run_id=run_id,
                    output_dir=output_dir,
                    diagnostics=diagnostics,
                    reporter=reporter,
                    debug_logger=debug_logger,
                )

            advisor_rows = unique_tsv_rows(ADVISOR_HEADERS, advisor_rows)
            service_rows = unique_tsv_rows(SERVICE_HEALTH_HEADERS, service_rows)
            _enforce_mandatory_raw_rows(
                diagnostics=diagnostics,
                reporter=reporter,
                advisor_rows=advisor_rows,
                service_rows=service_rows,
            )

            reporter.section("📝", "Raw Stage", "Persist source Advisor and Service Health TSV artifacts")
            advisor_report_path = output_dir / ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME
            service_health_report_path = output_dir / SERVICE_HEALTH_ADVISORIES_RAW_FILENAME

            write_tsv(advisor_report_path, ADVISOR_HEADERS, advisor_rows)
            reporter.step(f"Wrote Advisor retirements report: {advisor_report_path} ({len(advisor_rows)} row(s))")
            debug_logger.info(
                "advisor_report_written",
                "Advisor retirements report written",
                report_path=str(advisor_report_path),
                rows=len(advisor_rows),
            )

            write_tsv(service_health_report_path, SERVICE_HEALTH_HEADERS, service_rows)
            reporter.step(
                f"Wrote Service Health advisories report: {service_health_report_path} ({len(service_rows)} row(s))"
            )
            debug_logger.info(
                "service_health_report_written",
                "Service Health advisories report written",
                report_path=str(service_health_report_path),
                rows=len(service_rows),
            )

            counts_by_file[ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME] = len(advisor_rows)
            counts_by_file[SERVICE_HEALTH_ADVISORIES_RAW_FILENAME] = len(service_rows)

            if cfg.write_raw_jsonl:
                write_jsonl(output_dir / "azure_advisor_retirements_raw.jsonl", advisor_raw_items)
                write_jsonl(output_dir / "azure_service_health_advisories_raw.jsonl", service_raw_items)
                reporter.step("Wrote raw JSONL traces")
        else:
            reporter.section("📦", "Raw Stage Reuse", "Load previously generated raw TSV artifacts")
            advisor_rows, service_rows = _load_raw_stage_inputs(output_dir)
            counts_by_file[ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME] = len(advisor_rows)
            counts_by_file[SERVICE_HEALTH_ADVISORIES_RAW_FILENAME] = len(service_rows)
            reporter.step(
                "Loaded raw stage inputs: "
                f"{ADVISOR_SERVICE_RETIREMENTS_RAW_FILENAME} ({len(advisor_rows)} row(s)), "
                f"{SERVICE_HEALTH_ADVISORIES_RAW_FILENAME} ({len(service_rows)} row(s))"
            )
            diagnostics.add(
                severity="info",
                check_id="raw_stage_reused",
                source_system="global",
                scope="global",
                message="Raw workflow skipped and existing raw artifacts were reused",
                action_required="None",
            )

        if "aggregate" in selected_workflows:
            reporter.section("🧮", "Aggregate Stage", "Build normalized grouped advisory contract")
            platform_map = load_active_subscription_platform_map(PLATFORMS_SOURCE_PATH)
            aggregate_rows = unique_tsv_rows(
                AGGREGATE_HEADERS,
                build_aggregate_rows(
                    advisor_rows=advisor_rows,
                    service_rows=service_rows,
                    active_platform_map=platform_map,
                    as_of_date=cfg.as_of_date,
                ),
            )
            aggregate_report_path = output_dir / AGGREGATE_FILENAME
            write_tsv(aggregate_report_path, AGGREGATE_HEADERS, aggregate_rows)
            counts_by_file[AGGREGATE_FILENAME] = len(aggregate_rows)
            reporter.step(f"Wrote aggregate report: {aggregate_report_path} ({len(aggregate_rows)} row(s))")
            debug_logger.info(
                "aggregate_report_written",
                "Aggregate report written",
                report_path=str(aggregate_report_path),
                rows=len(aggregate_rows),
            )
            aggregate_stage_ran = True

        if "slide" in selected_workflows:
            reporter.section("🗂️", "Slide Stage", "Project aggregate output to committee subset")
            if not aggregate_stage_ran:
                aggregate_rows = _load_aggregate_stage_input(output_dir)
            slide_rows = unique_tsv_rows(SLIDE_HEADERS, build_slide_rows(aggregate_rows))
            slide_report_path = output_dir / SLIDE_FILENAME
            write_tsv(slide_report_path, SLIDE_HEADERS, slide_rows)
            counts_by_file[SLIDE_FILENAME] = len(slide_rows)
            reporter.step(f"Wrote slide report: {slide_report_path} ({len(slide_rows)} row(s))")
            debug_logger.info(
                "slide_report_written",
                "Slide report written",
                report_path=str(slide_report_path),
                rows=len(slide_rows),
            )

        diagnostics_rows = unique_tsv_rows(DIAGNOSTICS_HEADERS, diagnostics.rows())
        diagnostic_summary = _diagnostic_summary(diagnostics_rows)
        counts_by_file["azure_retirements_run_diagnostics.tsv"] = len(diagnostics_rows)

        diagnostics_path = runtime_dir / "azure_retirements_run_diagnostics.tsv"
        manifest_path = runtime_dir / "azure_retirements_run_manifest.json"

        write_tsv(diagnostics_path, DIAGNOSTICS_HEADERS, diagnostics_rows)
        reporter.step(f"Wrote run diagnostics: {diagnostics_path} ({len(diagnostics_rows)} row(s))")
        debug_logger.info(
            "diagnostics_written",
            "Diagnostics TSV written",
            diagnostics_path=str(diagnostics_path),
            diagnostics_rows=len(diagnostics_rows),
        )

        finished_at = utc_now()
        manifest = build_manifest(
            run_id=run_id,
            started_at_utc=started_at,
            finished_at_utc=finished_at,
            as_of_date=cfg.as_of_date.isoformat(),
            output_dir=str(output_dir),
            scope_mode=_scope_mode(cfg),
            subscriptions=resolved_subscriptions,
            management_groups=cfg.management_groups,
            query_start_time=cfg.health_query_start.isoformat(),
            api_versions={
                "advisor_recommendations": ADVISOR_API_VERSION,
                "advisor_metadata": ADVISOR_API_VERSION,
                "resource_graph_resources": "2024-04-01",
                "resource_health_events": RESOURCE_HEALTH_API_VERSION,
            },
            counts_by_file=counts_by_file,
            counts_by_source=counts_by_source,
            diagnostic_summary=diagnostic_summary,
            degraded_mode=any(row["severity"] == "error" for row in diagnostics_rows),
            command_line=" ".join(sys.argv),
            debug_log_path=str(debug_logger.file_path),
        )
        write_json(manifest_path, manifest)
        reporter.step(f"Wrote run manifest: {manifest_path}")
        debug_logger.info(
            "run_manifest_written",
            "Runtime manifest written",
            manifest_path=str(manifest_path),
        )
        reporter.step(f"Runtime debug log: {debug_logger.file_path}")
        reporter.summary(
            output_dir=output_dir,
            counts_by_file=counts_by_file,
            counts_by_source=counts_by_source,
            diagnostic_summary=diagnostic_summary,
        )
        if any(row["severity"] == "error" for row in diagnostics_rows):
            reporter.error("Run completed with error diagnostics; treating execution as failed")
            debug_logger.error(
                "run_completed_with_errors",
                "Run completed with diagnostics severity error",
                diagnostic_summary=diagnostic_summary,
            )
            return 1
        debug_logger.info(
            "run_completed_success",
            "Run completed successfully",
            diagnostic_summary=diagnostic_summary,
            counts_by_file=counts_by_file,
            counts_by_source=counts_by_source,
        )
        return 0
    except Exception as exc:  # pragma: no cover - terminal guard
        diagnostics.add(
            severity="error",
            check_id="runtime_failure",
            source_system="global",
            scope="global",
            message=f"Run failed: {exc}",
            action_required="Inspect traceback and rerun after remediation",
        )
        write_tsv(runtime_dir / "azure_retirements_run_diagnostics.tsv", DIAGNOSTICS_HEADERS, diagnostics.rows())
        reporter.error(f"Export failed: {exc}")
        debug_logger.error("run_failed", "Unhandled runtime failure", error=str(exc))
        return 1
    finally:
        debug_logger.close()


if __name__ == "__main__":
    raise SystemExit(main())
