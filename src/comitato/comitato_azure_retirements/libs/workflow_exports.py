"""Workflow helpers for raw, aggregate, and slide exports."""

from __future__ import annotations

from datetime import date
import html
from pathlib import Path
import re

import pandas as pd
import yaml
from .workflow_exports_grouping import (
    UNKNOWN_PLATFORM as GROUP_UNKNOWN_PLATFORM,
    aggregate_group,
)
from .workflow_exports_records import advisor_records, service_health_records
from .workflow_exports_utils import (
    as_string_list,
    build_advisory_key,
    canonical_title,
    normalize_key,
    traceable_links_from_identifiers,
)

RAW_ADVISOR_FILENAME = "01_azure_advisor_retirements_raw.tsv"
RAW_SERVICE_HEALTH_FILENAME = "01_azure_service_health_advisories_raw.tsv"
LEGACY_RAW_ADVISOR_FILENAME = "azure_advisor_retirements_aggregate.tsv"
LEGACY_RAW_SERVICE_HEALTH_FILENAME = "azure_service_health_advisories_aggregate.tsv"
AGGREGATE_FILENAME = "02_azure_retirements_aggregate.tsv"
SLIDE_FILENAME = "03_azure_retirements_slide.tsv"
UNKNOWN_PLATFORM = GROUP_UNKNOWN_PLATFORM


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


def build_aggregate_rows(
    *,
    advisor_rows: list[dict[str, str]],
    service_rows: list[dict[str, str]],
    active_platform_map: dict[str, str],
    as_of_date: date,
) -> list[dict[str, str]]:
    """Build grouped aggregate rows from advisor and service health raw rows."""
    records = advisor_records(advisor_rows) + service_health_records(service_rows)
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

    grouped_rows: list[dict[str, str]] = []
    for advisory_key, group in frame.groupby("advisory_key", sort=True):
        grouped_rows.append(
            aggregate_group(
                advisory_key=str(advisory_key),
                rows=group.to_dict("records"),
                active_platform_map=active_platform_map,
                normalize_key=normalize_key,
                as_of_date=as_of_date,
            )
        )

    grouped_rows.sort(key=lambda row: row["advisory_key"])
    return grouped_rows


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

        action_required = _strip_xml_tags(
            str(row.get("action_required", "") or row.get("summary_text", ""))
        )

        projected_rows.append(
            {
                "technology_or_service": row.get("technology_or_service", ""),
                "retiring_feature": row.get("retiring_feature", ""),
                "platforms": row.get("impacted_platforms", ""),
                "platforms_subscriptions_json": row.get(
                    "impacted_platforms_subscriptions_json", ""
                ),
                "priority_label": row.get("priority_label", ""),
                "advice_type": row.get("advice_type", ""),
                "action_required": action_required,
                "retirement_date": row.get("retirement_date", ""),
                "source_links": source_links,
            }
        )

    priority_rank = {
        "Critico": 0,
        "Prioritario": 1,
        "Da pianificare": 2,
        "Debito": 3,
    }
    projected_rows.sort(
        key=lambda row: (
            priority_rank.get(row.get("priority_label", ""), 99),
            row.get("retirement_date", "9999-12-31") or "9999-12-31",
            row.get("technology_or_service", "").lower(),
            row.get("retiring_feature", "").lower(),
        )
    )
    return projected_rows


_XML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _strip_xml_tags(value: str) -> str:
    if not value:
        return ""
    decoded_value = html.unescape(value).replace("\xa0", " ")
    without_tags = _XML_TAG_RE.sub(" ", decoded_value)
    return _WHITESPACE_RE.sub(" ", without_tags).strip()


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
