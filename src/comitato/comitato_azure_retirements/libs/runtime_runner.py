"""Main runtime execution loop for Azure retirements exports."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Callable

from .advisor import ADVISOR_API_VERSION
from .config import RuntimeConfig
from .debug_log import DebugRunLogger
from .diagnostics import DiagnosticsCollector, build_manifest, utc_now
from .runtime_logging import ExecutionReporter
from .schemas import ADVISOR_HEADERS, AGGREGATE_HEADERS, DIAGNOSTICS_HEADERS, SERVICE_HEALTH_HEADERS, SLIDE_HEADERS
from .service_health import RESOURCE_HEALTH_API_VERSION
from .tsv import compact_json, unique_tsv_rows
from .workflow_exports import (
    AGGREGATE_FILENAME,
    RAW_ADVISOR_FILENAME,
    RAW_SERVICE_HEALTH_FILENAME,
    SLIDE_FILENAME,
    build_aggregate_rows,
    build_slide_rows,
    load_active_subscription_platform_map,
)

SchemaOnlyFn = Callable[
    [RuntimeConfig, str, Path, DiagnosticsCollector],
    tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int], dict[str, int]],
]
FixtureFn = Callable[
    [RuntimeConfig, str, Path, DiagnosticsCollector],
    tuple[
        list[dict[str, str]],
        list[dict[str, str]],
        dict[str, int],
        dict[str, int],
        list[dict[str, Any]],
        list[dict[str, Any]],
    ],
]
LiveFn = Callable[
    [RuntimeConfig, str, Path, DiagnosticsCollector, ExecutionReporter, DebugRunLogger],
    tuple[
        list[dict[str, str]],
        list[dict[str, str]],
        dict[str, int],
        dict[str, int],
        list[dict[str, Any]],
        list[dict[str, Any]],
        list[str],
    ],
]


def run_export(
    *,
    cfg: RuntimeConfig,
    argv: list[str],
    platforms_source_path: Path,
    build_output_dir_fn: Callable[[Path, Any], Path],
    build_runtime_dir_fn: Callable[[Any], Path],
    build_debug_log_path_fn: Callable[[Path, str], Path],
    scope_mode_fn: Callable[[RuntimeConfig], str],
    diagnostic_summary_fn: Callable[[list[dict[str, str]]], dict[str, int]],
    manifest_degraded_mode_fn: Callable[[list[dict[str, str]]], bool],
    schema_only_fn: SchemaOnlyFn,
    fixture_mode_fn: FixtureFn,
    live_mode_fn: LiveFn,
    enforce_mandatory_raw_rows_fn: Callable[..., None],
    load_raw_stage_inputs_fn: Callable[[Path], tuple[list[dict[str, str]], list[dict[str, str]]]],
    load_aggregate_stage_input_fn: Callable[[Path], list[dict[str, str]]],
    add_aggregate_contract_diagnostics_fn: Callable[..., None],
    add_slide_source_link_diagnostics_fn: Callable[..., None],
    write_tsv_fn: Callable[[Path, list[str], list[dict[str, str]]], None],
    write_json_fn: Callable[[Path, dict[str, Any]], None],
    write_jsonl_fn: Callable[[Path, list[dict[str, Any]]], None],
) -> int:
    run_id = f"azure-retirements-{uuid.uuid4()}"
    started_at = utc_now()
    output_dir = build_output_dir_fn(cfg.output_root, cfg.as_of_date)
    runtime_dir = build_runtime_dir_fn(cfg.as_of_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    resolved_scope_mode = scope_mode_fn(cfg)
    debug_logger = DebugRunLogger(file_path=build_debug_log_path_fn(runtime_dir, run_id), run_id=run_id)
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
        debug_logger.info("workflow_selection", "Resolved workflow selection", workflows=selected_workflows)

        if "raw" in selected_workflows:
            if cfg.mode == "schema-only":
                reporter.section(
                    "🧪",
                    "Schema-only Mode",
                    "Write empty aggregates with headers and runtime diagnostics",
                )
                reporter.step("Skipping Azure API calls and generating schema artifacts only")
                advisor_rows, service_rows, counts_by_source, _ = schema_only_fn(
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
                ) = fixture_mode_fn(
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
                ) = live_mode_fn(
                    cfg=cfg,
                    run_id=run_id,
                    output_dir=output_dir,
                    diagnostics=diagnostics,
                    reporter=reporter,
                    debug_logger=debug_logger,
                )

            advisor_rows = unique_tsv_rows(ADVISOR_HEADERS, advisor_rows)
            service_rows = unique_tsv_rows(SERVICE_HEALTH_HEADERS, service_rows)
            if cfg.mode != "schema-only":
                enforce_mandatory_raw_rows_fn(
                    diagnostics=diagnostics,
                    reporter=reporter,
                    advisor_rows=advisor_rows,
                    service_rows=service_rows,
                )

            reporter.section(
                "📝",
                "Raw Stage",
                "Persist source Advisor and Service Health TSV artifacts",
            )
            advisor_report_path = output_dir / RAW_ADVISOR_FILENAME
            service_health_report_path = output_dir / RAW_SERVICE_HEALTH_FILENAME

            write_tsv_fn(advisor_report_path, ADVISOR_HEADERS, advisor_rows)
            reporter.step(f"Wrote Advisor retirements report: {advisor_report_path} ({len(advisor_rows)} row(s))")
            debug_logger.info(
                "advisor_report_written",
                "Advisor retirements report written",
                report_path=str(advisor_report_path),
                rows=len(advisor_rows),
            )

            write_tsv_fn(service_health_report_path, SERVICE_HEALTH_HEADERS, service_rows)
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
                write_jsonl_fn(output_dir / "azure_advisor_retirements_raw.jsonl", advisor_raw_items)
                write_jsonl_fn(output_dir / "azure_service_health_advisories_raw.jsonl", service_raw_items)
                reporter.step("Wrote raw JSONL traces")
        elif "aggregate" in selected_workflows:
            reporter.section("📦", "Raw Stage Reuse", "Load previously generated raw TSV artifacts")
            advisor_rows, service_rows = load_raw_stage_inputs_fn(output_dir)
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
                message="Raw workflow skipped because only slide workflow was selected",
                action_required="None",
            )

        if "aggregate" in selected_workflows:
            reporter.section("🧮", "Aggregate Stage", "Build normalized grouped advisory contract")
            platform_map = load_active_subscription_platform_map(platforms_source_path)
            aggregate_rows = unique_tsv_rows(
                AGGREGATE_HEADERS,
                build_aggregate_rows(
                    advisor_rows=advisor_rows,
                    service_rows=service_rows,
                    active_platform_map=platform_map,
                    as_of_date=cfg.as_of_date,
                ),
            )
            add_aggregate_contract_diagnostics_fn(diagnostics=diagnostics, aggregate_rows=aggregate_rows)
            aggregate_report_path = output_dir / AGGREGATE_FILENAME
            write_tsv_fn(aggregate_report_path, AGGREGATE_HEADERS, aggregate_rows)
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
                aggregate_rows = load_aggregate_stage_input_fn(output_dir)
            slide_rows = unique_tsv_rows(SLIDE_HEADERS, build_slide_rows(aggregate_rows))
            add_slide_source_link_diagnostics_fn(diagnostics=diagnostics, slide_rows=slide_rows)
            slide_report_path = output_dir / SLIDE_FILENAME
            write_tsv_fn(slide_report_path, SLIDE_HEADERS, slide_rows)
            counts_by_file[SLIDE_FILENAME] = len(slide_rows)
            reporter.step(f"Wrote slide report: {slide_report_path} ({len(slide_rows)} row(s))")
            debug_logger.info(
                "slide_report_written",
                "Slide report written",
                report_path=str(slide_report_path),
                rows=len(slide_rows),
            )

        diagnostics_rows = unique_tsv_rows(DIAGNOSTICS_HEADERS, diagnostics.rows())
        resolved_diagnostic_summary = diagnostic_summary_fn(diagnostics_rows)
        counts_by_file["azure_retirements_run_diagnostics.tsv"] = len(diagnostics_rows)

        diagnostics_path = runtime_dir / "azure_retirements_run_diagnostics.tsv"
        manifest_path = runtime_dir / "azure_retirements_run_manifest.json"

        write_tsv_fn(diagnostics_path, DIAGNOSTICS_HEADERS, diagnostics_rows)
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
            scope_mode=scope_mode_fn(cfg),
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
            degraded_mode=manifest_degraded_mode_fn(diagnostics_rows),
            command_line=" ".join(argv),
            debug_log_path=str(debug_logger.file_path),
        )
        write_json_fn(manifest_path, manifest)
        reporter.step(f"Wrote run manifest: {manifest_path}")
        debug_logger.info("run_manifest_written", "Runtime manifest written", manifest_path=str(manifest_path))
        reporter.step(f"Runtime debug log: {debug_logger.file_path}")
        reporter.summary(
            output_dir=output_dir,
            counts_by_file=counts_by_file,
            counts_by_source=counts_by_source,
            diagnostic_summary=resolved_diagnostic_summary,
        )
        if any(row["severity"] == "error" for row in diagnostics_rows):
            reporter.error("Run completed with error diagnostics; treating execution as failed")
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
    except Exception as exc:  # pragma: no cover - terminal guard
        diagnostics.add(
            severity="error",
            check_id="runtime_failure",
            source_system="global",
            scope="global",
            message=f"Run failed: {exc}",
            action_required="Inspect traceback and rerun after remediation",
        )
        write_tsv_fn(
            runtime_dir / "azure_retirements_run_diagnostics.tsv",
            DIAGNOSTICS_HEADERS,
            diagnostics.rows(),
        )
        reporter.error(f"Export failed: {exc}")
        debug_logger.error("run_failed", "Unhandled runtime failure", error=str(exc))
        return 1
    finally:
        debug_logger.close()
