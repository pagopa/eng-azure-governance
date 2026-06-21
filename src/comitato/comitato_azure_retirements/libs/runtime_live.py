"""Live-mode collection for Azure retirements runtime."""

from __future__ import annotations

from typing import Any

from .advisor import (
    collect_advisor_metadata,
    collect_advisor_recommendations,
    collect_advisor_resource_graph,
    index_metadata_with_collisions,
    index_resource_graph,
)
from .arm_client import ArmClient, ArmClientSettings
from .auth import get_management_token
from .config import RuntimeConfig
from .debug_log import DebugRunLogger
from .diagnostics import DiagnosticsCollector
from .normalize import normalize_advisor_rows, normalize_service_health_rows
from .runtime_logging import ExecutionReporter
from .runtime_paths import scope_mode
from .runtime_stages import add_live_empty_output_diagnostics, effective_worker_count
from .service_health import (
    build_recommended_actions,
    collect_events_for_subscriptions,
    event_impacted_regions,
    event_impacted_service_regions,
    event_impacted_services,
    filter_health_advisory_events,
)
from .subscriptions import build_subscription_name_map, resolve_scope_subscriptions
from .tsv import compact_json
from .workflow_exports import RAW_ADVISOR_FILENAME, RAW_SERVICE_HEALTH_FILENAME


def live_mode(
    cfg: RuntimeConfig,
    run_id: str,
    output_dir,
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
    del output_dir
    reporter.section(
        "🔐",
        "Authentication",
        "Acquire the ARM token and prepare the resilient HTTP session",
    )
    reporter.step("Requesting Azure ARM bearer token")
    token = get_management_token()
    # Keep pool size at least as large as the worker budget to avoid pool churn.
    pool_size = max(16, cfg.max_workers or 16)
    client = ArmClient(
        token,
        settings=ArmClientSettings(
            pool_connections=pool_size,
            pool_maxsize=pool_size,
        ),
        trace_handler=reporter.observe_request,
    )
    reporter.success("ARM client ready with retry-aware HTTP session")

    reporter.section(
        "🧭",
        "Scope Resolution",
        "Resolve explicit subscriptions and management group descendants",
    )
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

    effective_workers = effective_worker_count(len(subscriptions), cfg.max_workers)
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
                "effective_max_workers": effective_workers,
                "subscriptions_count": len(subscriptions),
            }
        ),
    )
    debug_logger.info(
        "collector_parallelism",
        "Parallel worker configuration resolved",
        requested_max_workers=cfg.max_workers,
        effective_max_workers=effective_workers,
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
            resolved_worker_count=effective_workers,
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
            resolved_worker_count=effective_workers,
            debug_logger=debug_logger,
        )
    service_events = filter_health_advisory_events(service_events)
    reporter.step(
        f"Advisor metadata rows: {len(advisor_metadata)} across {advisor_metadata_pages} page(s)"
    )
    reporter.step(
        "Advisor recommendation rows: "
        f"{len(advisor_recommendations)} across {sum(recommendation_pages.values())} page(s)"
    )
    reporter.step(
        f"Resource Graph rows: {len(advisor_graph_rows)} across {advisor_graph_pages} page(s)"
    )
    reporter.mapping("Advisor pages by subscription", recommendation_pages)

    reporter.section(
        "🏥",
        "Service Health Collection",
        "Fetch Service Health events for the resolved subscriptions",
    )
    reporter.step(
        f"Service Health rows: {len(service_events)} across {sum(service_pages.values())} page(s)"
    )
    reporter.mapping("Service Health pages by subscription", service_pages)

    metadata_by_key, metadata_collisions = index_metadata_with_collisions(advisor_metadata)
    graph_by_key = index_resource_graph(advisor_graph_rows)

    if metadata_collisions:
        diagnostics.add(
            severity="warning",
            check_id="advisor_metadata_key_collisions",
            source_system="advisor_metadata",
            scope="global",
            message="Advisor metadata contains duplicated keys; last value wins during indexing",
            action_required="Review duplicated metadata IDs or service IDs before relying on catalog-only joins",
            observed_count=len(metadata_collisions),
            raw_context_json=compact_json(
                {
                    "duplicate_keys": sorted(metadata_collisions.keys()),
                    "collision_events": sum(metadata_collisions.values()),
                }
            ),
        )
        reporter.warning(
            f"Advisor metadata produced {len(metadata_collisions)} duplicate key(s)"
        )

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
        scope_mode=scope_mode(cfg),
        recommendations=advisor_recommendations,
        metadata_by_key=metadata_by_key,
        resource_graph_by_key=graph_by_key,
        subscription_name_map=subscription_name_map,
        include_raw_json=cfg.write_raw_jsonl,
    )

    service_rows = normalize_service_health_rows(
        run_id=run_id,
        as_of_date=cfg.as_of_date,
        scope_mode=scope_mode(cfg),
        events=service_events,
        subscription_name_map=subscription_name_map,
        event_impacted_services=event_impacted_services,
        event_impacted_regions=event_impacted_regions,
        event_impacted_service_regions=event_impacted_service_regions,
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
        reporter.warning(
            f"Service Health collection failed for {len(service_failures)} subscription(s)"
        )
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
        reporter.warning(
            "Problem determination mini-report generated for warning/error subscriptions"
        )
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
        reporter.warning(
            "Resource Graph returned truncated results; validate output counts carefully"
        )

    counts_by_source = {
        "advisor_metadata": len(advisor_metadata),
        "advisor_recommendations": len(advisor_recommendations),
        "resource_graph_advisorresources": len(advisor_graph_rows),
        "resource_health_events": len(service_events),
    }
    add_live_empty_output_diagnostics(
        diagnostics=diagnostics,
        reporter=reporter,
        advisor_rows=advisor_rows,
        service_rows=service_rows,
        counts_by_source=counts_by_source,
    )
    counts_by_file = {
        RAW_ADVISOR_FILENAME: len(advisor_rows),
        RAW_SERVICE_HEALTH_FILENAME: len(service_rows),
        "azure_retirements_run_diagnostics.tsv": len(diagnostics.rows()),
    }

    advisor_raw = [{"kind": "advisor_metadata", "item": item} for item in advisor_metadata] + [
        {"kind": "advisor_recommendation", "item": item} for item in advisor_recommendations
    ]
    service_raw = [{"kind": "service_health_event", "item": item} for item in service_events]

    return (
        advisor_rows,
        service_rows,
        counts_by_source,
        counts_by_file,
        advisor_raw,
        service_raw,
        subscriptions,
    )
