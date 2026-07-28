"""Main runtime execution loop for Azure retirements exports."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .advisor import ADVISOR_API_VERSION
from .config import RuntimeConfig
from .debug_log import DebugRunLogger
from .diagnostics import DiagnosticsCollector, build_manifest, utc_now
from .runtime_live import live_mode
from .runtime_logging import ExecutionReporter
from .runtime_paths import (
    build_debug_log_path,
    build_output_dir,
    build_runtime_dir,
    scope_mode,
)
from .runtime_router import RuntimeRoute, StageAction, build_runtime_route
from .runtime_stages import (
    add_aggregate_contract_diagnostics,
    add_publication_exclusion_diagnostics,
    add_service_health_contract_diagnostics,
    add_slide_source_link_diagnostics,
    diagnostic_summary,
    enforce_mandatory_raw_rows,
    fixture_mode,
    load_aggregate_stage_input,
    load_raw_stage_inputs,
    load_slide_stage_inputs,
    manifest_degraded_mode,
    schema_only,
)
from .schemas import (
    ADVISOR_HEADERS,
    AGGREGATE_HEADERS,
    DIAGNOSTICS_HEADERS,
    SERVICE_HEALTH_HEADERS,
    SLIDE_HEADERS,
)
from .service_health import RESOURCE_HEALTH_API_VERSION
from .tsv import compact_json, unique_tsv_rows, write_json, write_jsonl, write_tsv
from .workflow_exports import (
    AGGREGATE_FILENAME,
    RAW_ADVISOR_FILENAME,
    RAW_SERVICE_HEALTH_FILENAME,
    SLIDE_FILENAME,
    build_aggregate_rows,
    build_slide_rows,
    load_active_subscription_platform_map,
)


def _platforms_source_path(script_path: Path) -> Path:
    return script_path.resolve().parents[2] / "_source_of_truth" / "platforms.yaml"


def _default_counts_by_source() -> dict[str, int]:
    return {
        "advisor_metadata": 0,
        "advisor_recommendations": 0,
        "resource_graph_advisorresources": 0,
        "resource_health_events": 0,
        "resource_health_events_collected": 0,
        "resource_health_events_retained": 0,
        "resource_health_events_expired": 0,
    }


def _run_raw_stage(
    *,
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
    counts_by_source = _default_counts_by_source()
    counts_by_file: dict[str, int] = {}
    advisor_raw_items: list[dict[str, Any]] = []
    service_raw_items: list[dict[str, Any]] = []
    resolved_subscriptions: list[str] = cfg.subscriptions

    if cfg.mode == "schema-only":
        reporter.section(
            "🧪",
            "Schema-only Mode",
            "Write empty aggregates with headers and runtime diagnostics",
        )
        reporter.step("Skipping Azure API calls and generating schema artifacts only")
        advisor_rows, service_rows, counts_by_source, _ = schema_only(
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
        ) = fixture_mode(
            cfg=cfg,
            run_id=run_id,
            output_dir=output_dir,
            diagnostics=diagnostics,
        )
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
        ) = live_mode(
            cfg=cfg,
            run_id=run_id,
            output_dir=output_dir,
            diagnostics=diagnostics,
            reporter=reporter,
            debug_logger=debug_logger,
        )

    advisor_rows = unique_tsv_rows(ADVISOR_HEADERS, advisor_rows)
    service_rows = unique_tsv_rows(SERVICE_HEALTH_HEADERS, service_rows)
    add_service_health_contract_diagnostics(
        diagnostics=diagnostics,
        rows=service_rows,
    )
    if cfg.mode in {"live", "fixture"} and not cfg.allow_degraded:
        contract_errors = [
            row
            for row in diagnostics.rows()
            if row["severity"] == "error"
            and row["check_id"].startswith("service_health_")
            and row["check_id"] in {
                "service_health_blank_tracking_id",
                "service_health_noncanonical_description_problem",
                "service_health_blank_priority",
                "service_health_blank_subscription_name",
                "service_health_blank_resource_contract",
            }
        ]
        if contract_errors:
            raise RuntimeError("Service Health raw contract validation failed before publication")
    if cfg.mode != "schema-only":
        enforce_mandatory_raw_rows(
            diagnostics=diagnostics,
            reporter=reporter,
            advisor_rows=advisor_rows,
            service_rows=service_rows,
            counts_by_source=counts_by_source,
        )

    reporter.section(
        "📝",
        "Raw Stage",
        "Persist source Advisor and Service Health TSV artifacts",
    )
    advisor_report_path = output_dir / RAW_ADVISOR_FILENAME
    service_health_report_path = output_dir / RAW_SERVICE_HEALTH_FILENAME

    write_tsv(advisor_report_path, ADVISOR_HEADERS, advisor_rows)
    reporter.step(
        f"Wrote Advisor retirements report: {advisor_report_path} ({len(advisor_rows)} row(s))"
    )
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

    counts_by_file[RAW_ADVISOR_FILENAME] = len(advisor_rows)
    counts_by_file[RAW_SERVICE_HEALTH_FILENAME] = len(service_rows)

    if cfg.write_raw_jsonl:
        write_jsonl(
            output_dir / "azure_advisor_retirements_raw.jsonl", advisor_raw_items
        )
        write_jsonl(
            output_dir / "azure_service_health_advisories_raw.jsonl", service_raw_items
        )
        reporter.step("Wrote raw JSONL traces")

    return (
        advisor_rows,
        service_rows,
        counts_by_source,
        counts_by_file,
        advisor_raw_items,
        service_raw_items,
        resolved_subscriptions,
    )


def _run_aggregate_stage(
    *,
    cfg: RuntimeConfig,
    output_dir: Path,
    platforms_source_path: Path,
    diagnostics: DiagnosticsCollector,
    reporter: ExecutionReporter,
    debug_logger: DebugRunLogger,
    advisor_rows: list[dict[str, str]],
    service_rows: list[dict[str, str]],
    counts_by_file: dict[str, int],
) -> list[dict[str, str]]:
    reporter.section(
        "🧮", "Aggregate Stage", "Build normalized grouped advisory contract"
    )
    platform_map = load_active_subscription_platform_map(platforms_source_path)
    aggregate_result = build_aggregate_rows(
        advisor_rows=advisor_rows,
        service_rows=service_rows,
        active_platform_map=platform_map,
        as_of_date=cfg.as_of_date,
    )
    aggregate_rows = unique_tsv_rows(
        AGGREGATE_HEADERS,
        aggregate_result.advisor_rows + aggregate_result.service_health_rows,
    )
    add_publication_exclusion_diagnostics(
        diagnostics=diagnostics,
        excluded_by_reason=aggregate_result.excluded_by_reason,
    )
    add_aggregate_contract_diagnostics(
        diagnostics=diagnostics,
        aggregate_rows=aggregate_rows,
    )
    aggregate_report_path = output_dir / AGGREGATE_FILENAME
    write_tsv(aggregate_report_path, AGGREGATE_HEADERS, aggregate_rows)
    counts_by_file[AGGREGATE_FILENAME] = len(aggregate_rows)
    reporter.step(
        f"Wrote aggregate report: {aggregate_report_path} ({len(aggregate_rows)} row(s))"
    )
    debug_logger.info(
        "aggregate_report_written",
        "Aggregate report written",
        report_path=str(aggregate_report_path),
        rows=len(aggregate_rows),
    )
    return aggregate_rows


def _run_slide_stage(
    *,
    output_dir: Path,
    diagnostics: DiagnosticsCollector,
    reporter: ExecutionReporter,
    debug_logger: DebugRunLogger,
    aggregate_rows: list[dict[str, str]],
    counts_by_file: dict[str, int],
) -> list[dict[str, str]]:
    reporter.section("🗂️", "Slide Stage", "Project aggregate output to committee subset")
    slide_rows = unique_tsv_rows(SLIDE_HEADERS, build_slide_rows(aggregate_rows))
    add_slide_source_link_diagnostics(diagnostics=diagnostics, slide_rows=slide_rows)
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
    return slide_rows


def _finalize_run(
    *,
    cfg: RuntimeConfig,
    run_id: str,
    started_at: str,
    argv: list[str],
    output_dir: Path,
    runtime_dir: Path,
    diagnostics: DiagnosticsCollector,
    reporter: ExecutionReporter,
    debug_logger: DebugRunLogger,
    counts_by_file: dict[str, int],
    counts_by_source: dict[str, int],
    resolved_subscriptions: list[str],
    resolved_scope_mode: str,
) -> int:
    diagnostics_rows = unique_tsv_rows(DIAGNOSTICS_HEADERS, diagnostics.rows())
    resolved_diagnostic_summary = diagnostic_summary(diagnostics_rows)
    counts_by_file["azure_retirements_run_diagnostics.tsv"] = len(diagnostics_rows)

    diagnostics_path = runtime_dir / "azure_retirements_run_diagnostics.tsv"
    manifest_path = runtime_dir / "azure_retirements_run_manifest.json"

    write_tsv(diagnostics_path, DIAGNOSTICS_HEADERS, diagnostics_rows)
    reporter.step(
        f"Wrote run diagnostics: {diagnostics_path} ({len(diagnostics_rows)} row(s))"
    )
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
        scope_mode=resolved_scope_mode,
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
        diagnostic_summary=resolved_diagnostic_summary,
        degraded_mode=manifest_degraded_mode(diagnostics_rows),
        command_line=" ".join(argv),
        debug_log_path=(str(debug_logger.file_path) if debug_logger.enabled else ""),
    )
    write_json(manifest_path, manifest)
    reporter.step(f"Wrote run manifest: {manifest_path}")
    debug_logger.info(
        "run_manifest_written",
        "Runtime manifest written",
        manifest_path=str(manifest_path),
    )
    if debug_logger.enabled:
        reporter.step(f"Runtime debug log: {debug_logger.file_path}")
    reporter.summary(
        output_dir=output_dir,
        counts_by_file=counts_by_file,
        counts_by_source=counts_by_source,
        diagnostic_summary=resolved_diagnostic_summary,
    )
    if any(row["severity"] == "error" for row in diagnostics_rows):
        reporter.error(
            "Run completed with error diagnostics; treating execution as failed"
        )
        debug_logger.error(
            "run_completed_with_errors",
            "Run completed with diagnostics severity error",
            diagnostic_summary=resolved_diagnostic_summary,
        )
        return 1
    debug_logger.info(
        "run_completed_success",
        "Run completed successfully",
        diagnostic_summary=resolved_diagnostic_summary,
        counts_by_file=counts_by_file,
        counts_by_source=counts_by_source,
    )
    return 0


def run_export(
    *,
    cfg: RuntimeConfig,
    argv: list[str],
    script_path: Path,
    route: RuntimeRoute | None = None,
) -> int:
    run_id = f"azure-retirements-{uuid.uuid4()}"
    started_at_datetime = datetime.now(timezone.utc).replace(microsecond=0)
    started_at = started_at_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    output_dir = build_output_dir(cfg.output_root, cfg.as_of_date)
    runtime_dir = build_runtime_dir(script_path, cfg.as_of_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    resolved_scope_mode = scope_mode(cfg)
    log_directory = cfg.logging.log_directory or runtime_dir
    debug_logger = DebugRunLogger(
        file_path=build_debug_log_path(
            log_directory,
            run_id,
            started_at=started_at_datetime,
        ),
        run_id=run_id,
        enabled=cfg.logging.enabled,
        level=cfg.logging.level,
        include_traceback=cfg.logging.include_traceback,
    )
    reporter = ExecutionReporter(
        verbose=cfg.verbose,
        debug_logger=debug_logger,
        console_level=cfg.logging.console_level,
    )
    platforms_source_path = _platforms_source_path(script_path)

    diagnostics = DiagnosticsCollector(run_id)
    diagnostics.add(
        severity="info",
        check_id=(
            "debug_log_enabled" if debug_logger.enabled else "debug_log_disabled"
        ),
        source_system="global",
        scope="global",
        message=(
            "Persistent debug log enabled for this run"
            if debug_logger.enabled
            else "Persistent debug log disabled by azure_rel.conf"
        ),
        action_required=(
            "Use debug log for timeline-based problem determination"
            if debug_logger.enabled
            else "Set logging.enabled=true in azure_rel.conf when persistent diagnostics are required"
        ),
        raw_context_json=compact_json(
            {
                "debug_log_path": (
                    str(debug_logger.file_path) if debug_logger.enabled else ""
                )
            }
        ),
    )
    reporter.banner(
        run_id=run_id,
        mode=cfg.mode,
        scope_mode=resolved_scope_mode,
        output_dir=output_dir,
        subscriptions=cfg.subscriptions,
        management_groups=cfg.management_groups,
        write_raw_jsonl=cfg.write_raw_jsonl,
    )
    debug_logger.info(
        "run_started",
        "Azure retirements run started",
        mode=cfg.mode,
        scope_mode=resolved_scope_mode,
        subscriptions=cfg.subscriptions,
        management_groups=cfg.management_groups,
        output_dir=str(output_dir),
        runtime_dir=str(runtime_dir),
        command_line=" ".join(argv),
    )

    current_stage = "startup"
    try:
        advisor_rows: list[dict[str, str]] = []
        service_rows: list[dict[str, str]] = []
        aggregate_rows: list[dict[str, str]] = []
        service_health_aggregate_rows: list[dict[str, str]] = []
        slide_input_rows: list[dict[str, str]] = []
        counts_by_source = _default_counts_by_source()
        counts_by_file: dict[str, int] = {}
        resolved_subscriptions: list[str] = cfg.subscriptions
        resolved_route = route or build_runtime_route(cfg.workflows)
        selected_workflows = list(resolved_route.selected_workflows)

        reporter.step(f"Selected workflows: {', '.join(selected_workflows)}")
        reporter.detail("Workflow route", resolved_route.describe(), always=True)
        debug_logger.info(
            "workflow_selection",
            "Resolved workflow selection",
            workflows=selected_workflows,
            workflow_route=resolved_route.describe(),
            workflow_route_name=resolved_route.name,
        )

        current_stage = "raw"
        if resolved_route.raw_action == StageAction.EXECUTE:
            (
                advisor_rows,
                service_rows,
                counts_by_source,
                raw_counts_by_file,
                _,
                _,
                resolved_subscriptions,
            ) = _run_raw_stage(
                cfg=cfg,
                run_id=run_id,
                output_dir=output_dir,
                diagnostics=diagnostics,
                reporter=reporter,
                debug_logger=debug_logger,
            )
            counts_by_file.update(raw_counts_by_file)
        elif resolved_route.raw_action == StageAction.REUSE:
            reporter.section(
                "📦", "Raw Stage Reuse", "Load previously generated raw TSV artifacts"
            )
            advisor_rows, service_rows = load_raw_stage_inputs(output_dir)
            counts_by_file[RAW_ADVISOR_FILENAME] = len(advisor_rows)
            counts_by_file[RAW_SERVICE_HEALTH_FILENAME] = len(service_rows)
            reporter.step(
                "Loaded raw stage inputs: "
                f"{RAW_ADVISOR_FILENAME} ({len(advisor_rows)} row(s)), "
                f"{RAW_SERVICE_HEALTH_FILENAME} ({len(service_rows)} row(s))"
            )
            diagnostics.add(
                severity="info",
                check_id="raw_stage_reused",
                source_system="global",
                scope="global",
                message="Raw workflow skipped and existing raw artifacts were reused",
                action_required="None",
            )
        else:
            diagnostics.add(
                severity="info",
                check_id="raw_stage_skipped",
                source_system="global",
                scope="global",
                message="Raw workflow skipped by workflow route",
                action_required="None",
            )

        current_stage = "aggregate"
        if resolved_route.aggregate_action == StageAction.EXECUTE:
            aggregate_rows = _run_aggregate_stage(
                cfg=cfg,
                output_dir=output_dir,
                platforms_source_path=platforms_source_path,
                diagnostics=diagnostics,
                reporter=reporter,
                debug_logger=debug_logger,
                advisor_rows=advisor_rows,
                service_rows=service_rows,
                counts_by_file=counts_by_file,
            )
            slide_input_rows = aggregate_rows
        elif resolved_route.aggregate_action == StageAction.REUSE:
            reporter.section(
                "📦",
                "Aggregate Stage Reuse",
                "Load previously generated aggregate TSV artifact",
            )
            aggregate_rows = load_aggregate_stage_input(output_dir)
            slide_input_rows = load_slide_stage_inputs(output_dir)
            counts_by_file[AGGREGATE_FILENAME] = len(aggregate_rows)
            reporter.step(
                "Loaded aggregate stage input: "
                f"{AGGREGATE_FILENAME} ({len(aggregate_rows)} row(s))"
            )
            diagnostics.add(
                severity="info",
                check_id="aggregate_stage_reused",
                source_system="global",
                scope="global",
                message="Aggregate workflow skipped and existing aggregate artifact was reused",
                action_required="None",
            )

        current_stage = "slide"
        if resolved_route.slide_action == StageAction.EXECUTE:
            _ = _run_slide_stage(
                output_dir=output_dir,
                diagnostics=diagnostics,
                reporter=reporter,
                debug_logger=debug_logger,
                aggregate_rows=slide_input_rows,
                counts_by_file=counts_by_file,
            )

        current_stage = "finalize"
        return _finalize_run(
            cfg=cfg,
            run_id=run_id,
            started_at=started_at,
            argv=argv,
            output_dir=output_dir,
            runtime_dir=runtime_dir,
            diagnostics=diagnostics,
            reporter=reporter,
            debug_logger=debug_logger,
            counts_by_file=counts_by_file,
            counts_by_source=counts_by_source,
            resolved_subscriptions=resolved_subscriptions,
            resolved_scope_mode=resolved_scope_mode,
        )
    except Exception as exc:  # pragma: no cover - terminal guard
        diagnostics.add(
            severity="error",
            check_id="runtime_failure",
            source_system="global",
            scope="global",
            message=f"Run failed: {exc}",
            action_required="Inspect traceback and rerun after remediation",
        )
        write_tsv(
            runtime_dir / "azure_retirements_run_diagnostics.tsv",
            DIAGNOSTICS_HEADERS,
            diagnostics.rows(),
        )
        log_hint = (
            f"; full traceback: {debug_logger.file_path}"
            if debug_logger.enabled and cfg.logging.include_traceback
            else ""
        )
        reporter.error(f"Export failed during {current_stage}: {exc}{log_hint}")
        debug_logger.exception(
            "run_failed",
            "Unhandled runtime failure",
            exc,
            stage=current_stage,
        )
        return 1
    finally:
        debug_logger.close()
