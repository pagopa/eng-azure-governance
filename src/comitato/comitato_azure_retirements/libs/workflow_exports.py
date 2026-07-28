"""Workflow helpers for raw, aggregate, and slide exports."""

from __future__ import annotations

from datetime import date
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml
from .workflow_exports_grouping import (
    UNKNOWN_PLATFORM as GROUP_UNKNOWN_PLATFORM,
    aggregate_group,
)
from .workflow_exports_records import (
    advisor_records,
    select_publication_records,
    service_health_records,
)
from .workflow_exports_utils import (
    as_string_list,
    build_advisory_key,
    canonical_title,
    normalize_key,
    priority_rank,
    traceable_links_from_identifiers,
)
from .service_health_text import html_to_ascii_text

RAW_ADVISOR_FILENAME = "01_azure_advisor_retirements_raw.tsv"
RAW_SERVICE_HEALTH_FILENAME = "01_azure_service_health_advisories_raw.tsv"
LEGACY_RAW_ADVISOR_FILENAME = "azure_advisor_retirements_aggregate.tsv"
LEGACY_RAW_SERVICE_HEALTH_FILENAME = "azure_service_health_advisories_aggregate.tsv"
AGGREGATE_FILENAME = "02_azure_retirements_aggregate.tsv"
SERVICE_HEALTH_SUPPLEMENTAL_FILENAME = "02_azure_service_health_supplemental.tsv"
SLIDE_FILENAME = "03_azure_retirements_slide.tsv"
UNKNOWN_PLATFORM = GROUP_UNKNOWN_PLATFORM


@dataclass(frozen=True)
class AggregateBuildResult:
    advisor_rows: list[dict[str, str]]
    service_health_rows: list[dict[str, str]]
    excluded_by_reason: dict[str, list[str]]


def _group_records_by_advisory_key(frame: pd.DataFrame) -> list[tuple[str, list[dict[str, object]]]]:
    # Pandas is intentionally isolated here to keep a future stdlib migration one-spot.
    grouped: list[tuple[str, list[dict[str, object]]]] = []
    for advisory_key, group in frame.groupby("advisory_key", sort=True):
        grouped.append((str(advisory_key), group.to_dict("records")))
    return grouped


def load_active_subscription_platform_map(platforms_path: Path) -> dict[str, str]:
    """Load an active-only reverse map of subscription name to platform name."""
    payload = yaml.safe_load(platforms_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}

    reverse_map: dict[str, str] = {}
    for platform_name, platform_payload in payload.items():
        if not isinstance(platform_name, str) or not isinstance(platform_payload, dict):
            continue

        active_subscriptions = platform_payload.get("active")
        if not isinstance(active_subscriptions, list):
            continue

        for subscription_name in active_subscriptions:
            if not isinstance(subscription_name, str):
                continue
            normalized_subscription = normalize_key(subscription_name)
            if normalized_subscription:
                reverse_map[normalized_subscription] = platform_name

    return reverse_map


def _group_records(
    records: list[dict[str, object]],
    *,
    active_platform_map: dict[str, str],
    as_of_date: date,
) -> list[dict[str, str]]:
    if not records:
        return []

    frame = pd.DataFrame.from_records(records).fillna("")
    frame["canonical_title"] = frame["retiring_feature"].map(canonical_title)
    frame["canonical_date"] = frame["retirement_date"].map(
        lambda value: value if value else "na"
    )
    frame["advisory_key"] = frame.apply(
        lambda row: _build_advisory_key(
            advice_type=str(row["advice_type"]),
            canonical_title_value=str(row["canonical_title"]),
            canonical_date=str(row["canonical_date"]),
            source_identifiers=row["source_identifiers"],
        ),
        axis=1,
    )
    subscription_name_by_id = _subscription_name_by_id(frame.to_dict("records"))

    grouped_rows: list[dict[str, str]] = []
    for advisory_key, grouped_records in _group_records_by_advisory_key(frame):
        grouped_rows.append(
            aggregate_group(
                advisory_key=str(advisory_key),
                rows=grouped_records,
                active_platform_map=active_platform_map,
                normalize_key=normalize_key,
                as_of_date=as_of_date,
                subscription_name_by_id=subscription_name_by_id,
            )
        )

    grouped_rows.sort(key=lambda row: row["advisory_key"])
    return grouped_rows


def build_aggregate_rows(
    *,
    advisor_rows: list[dict[str, str]],
    service_rows: list[dict[str, str]],
    active_platform_map: dict[str, str],
    as_of_date: date,
) -> AggregateBuildResult:
    """Build source-separated grouped aggregate rows for the publication window."""
    advisor_selection = select_publication_records(
        advisor_records(advisor_rows), as_of_date=as_of_date
    )
    service_health_selection = select_publication_records(
        service_health_records(service_rows), as_of_date=as_of_date
    )

    excluded_by_reason: dict[str, list[str]] = {}
    for selection in (advisor_selection, service_health_selection):
        for reason, identifiers in selection.excluded_by_reason.items():
            excluded_by_reason.setdefault(reason, []).extend(identifiers)

    return AggregateBuildResult(
        advisor_rows=_group_records(
            advisor_selection.records,
            active_platform_map=active_platform_map,
            as_of_date=as_of_date,
        ),
        service_health_rows=_group_records(
            service_health_selection.records,
            active_platform_map=active_platform_map,
            as_of_date=as_of_date,
        ),
        excluded_by_reason={
            reason: sorted(set(identifiers))
            for reason, identifiers in excluded_by_reason.items()
        },
    )


def build_slide_rows(aggregate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Project aggregate rows into the committee slide subset schema."""
    projected_rows: list[dict[str, str]] = []
    for row in aggregate_rows:
        source_links = row.get("source_links", "").strip()
        if not source_links:
            source_links = ", ".join(
                traceable_links_from_identifiers(
                    as_string_list(row.get("source_identifiers", ""))
                )
            )

        action_required = html_to_ascii_text(
            str(row.get("action_required", "") or row.get("summary_text", ""))
        )
        complete_description = " ".join(
            value
            for value in (
                html_to_ascii_text(str(row.get("details_text", ""))),
                action_required,
            )
            if value
        )
        source_systems = row.get("source_systems", "").lower()
        source = (
            "Fonte: service-health"
            if "resource_health" in source_systems
            or str(row.get("advice_type", "")).startswith("service_health")
            else "Fonte: advisor"
        )

        projected_rows.append(
            {
                "technology_or_service": row.get("technology_or_service", ""),
                "retiring_feature": row.get("retiring_feature", ""),
                "platforms": row.get("impacted_platforms", ""),
                "platforms_subscriptions_json": row.get(
                    "impacted_platforms_subscriptions_json", ""
                ),
                "comitato_priorità": row.get("priority_label", ""),
                "advice_type": row.get("advice_type", ""),
                "action_required": action_required,
                "comitato_descrizione_completa": complete_description,
                "comitato_retirement_date": row.get("retirement_date", ""),
                "comitato_piattaforme": row.get("impacted_platforms", ""),
                "source_links": source_links,
                "source": source,
            }
        )

    projected_rows.sort(
        key=lambda row: (
            priority_rank(row.get("priority_label", "")),
            row.get("retirement_date", "9999-12-31") or "9999-12-31",
            row.get("technology_or_service", "").lower(),
            row.get("retiring_feature", "").lower(),
        )
    )
    return projected_rows




def _build_advisory_key(
    *,
    advice_type: str,
    canonical_title_value: str,
    canonical_date: str,
    source_identifiers: object,
) -> str:
    return build_advisory_key(
        advice_type=advice_type,
        canonical_title_value=canonical_title_value,
        canonical_date=canonical_date,
        source_identifiers=source_identifiers,
    )


def _subscription_name_by_id(records: list[dict[str, object]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for record in records:
        subscription_id = str(record.get("subscription_id", "")).strip()
        subscription_name = str(record.get("subscription_name", "")).strip()
        if subscription_id and subscription_name and subscription_id not in mapping:
            mapping[subscription_id] = subscription_name
    return mapping
