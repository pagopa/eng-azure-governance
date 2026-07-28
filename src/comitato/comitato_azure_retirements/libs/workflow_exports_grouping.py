"""Grouping helpers for aggregate workflow exports."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
import re

from .dates import parse_possible_date
from .tsv import compact_json
from .workflow_exports_utils import (
    as_string_list,
    first_non_empty,
    max_iso_date,
    min_iso_date,
    pick_human_text,
    priority_label,
    sorted_unique,
)

UNKNOWN_PLATFORM = "Unknown Platform"
UNKNOWN_SUBSCRIPTION = "Unknown Subscription"

_SUBSCRIPTION_ID_RE = re.compile(r"/subscriptions/([^/]+)", re.IGNORECASE)


def aggregate_group(
    *,
    advisory_key: str,
    rows: list[dict[str, object]],
    active_platform_map: dict[str, str],
    normalize_key,
    as_of_date: date,
    subscription_name_by_id: dict[str, str] | None = None,
) -> dict[str, str]:
    source_identifiers = sorted_unique(
        item for row in rows for item in as_string_list(row.get("source_identifiers"))
    )
    source_links = sorted_unique(
        item for row in rows for item in as_string_list(row.get("source_links"))
    )
    source_systems = sorted_unique(str(row.get("source_system", "")) for row in rows)
    subscription_names = _subscription_references(
        rows=rows,
        subscription_name_by_id=subscription_name_by_id or {},
    )

    platform_subscriptions: dict[str, set[str]] = defaultdict(set)
    for subscription_name in subscription_names:
        platform_name = active_platform_map.get(normalize_key(subscription_name), UNKNOWN_PLATFORM)
        platform_subscriptions[platform_name].add(subscription_name)

    ordered_platforms = sorted(
        platform_subscriptions.keys(),
        key=lambda value: (value == UNKNOWN_PLATFORM, value.lower()),
    )
    impacted_platforms = ", ".join(ordered_platforms)
    platform_json = {
        "platforms": {
            platform_name: sorted(platform_subscriptions[platform_name], key=str.lower)
            for platform_name in ordered_platforms
        }
    }

    retirement_candidates = sorted_unique(str(row.get("retirement_date", "")) for row in rows)
    parsed_dates = [candidate for candidate in retirement_candidates if parse_possible_date(candidate)]
    chosen_retirement_date = ""
    if parsed_dates:
        chosen_retirement_date = min(parsed_dates)

    first_seen_date = min_iso_date(str(row.get("as_of_date", "")) for row in rows)
    last_seen_date = max_iso_date(str(row.get("as_of_date", "")) for row in rows)

    retiring_feature = pick_human_text(str(row.get("retiring_feature", "")) for row in rows)
    summary_text = pick_human_text(str(row.get("summary_text", "")) for row in rows)
    source = first_non_empty(str(row.get("source", "")) for row in rows)
    raw_problem = pick_human_text(
        str(row.get("_descrizione_problema_raw", "")) for row in rows
    )
    action_required = pick_human_text(str(row.get("action_required", "")) for row in rows)
    if not action_required:
        action_required = summary_text

    technology_or_service = pick_human_text(
        str(row.get("technology_or_service", "")) for row in rows
    )

    advice_type = first_non_empty([str(row.get("advice_type", "")) for row in rows])
    computed_priority_label = priority_label(retirement_date=chosen_retirement_date, as_of_date=as_of_date)

    return {
        "source": source,
        "advisory_key": advisory_key,
        "technology_or_service": technology_or_service,
        "impacted_platforms": impacted_platforms,
        "impacted_subscriptions": ", ".join(subscription_names),
        "impacted_platforms_subscriptions_json": compact_json(platform_json),
        "advice_type": advice_type,
        "_descrizione_problema_raw": raw_problem,
        "retiring_feature": retiring_feature,
        "action_required": action_required,
        "retirement_date": chosen_retirement_date,
        "priority_label": computed_priority_label,
        "source_systems": ", ".join(source_systems),
        "source_identifiers": ", ".join(source_identifiers),
        "source_links": ", ".join(source_links),
        "summary_text": summary_text,
        "first_seen_date": first_seen_date,
        "last_seen_date": last_seen_date,
    }


def _subscription_references(
    *,
    rows: list[dict[str, object]],
    subscription_name_by_id: dict[str, str],
) -> list[str]:
    references: list[str] = []
    for row in rows:
        subscription_name = str(row.get("subscription_name", "")).strip()
        subscription_id = str(row.get("subscription_id", "")).strip()
        if not subscription_id:
            subscription_id = _first_subscription_id(row.get("source_identifiers"))

        if not subscription_name and subscription_id:
            subscription_name = subscription_name_by_id.get(subscription_id, subscription_id)

        if subscription_name:
            references.append(subscription_name)

    if not references:
        references.append(UNKNOWN_SUBSCRIPTION)

    return sorted_unique(references)


def _first_subscription_id(source_identifiers: object) -> str:
    for source_identifier in as_string_list(source_identifiers):
        match = _SUBSCRIPTION_ID_RE.search(source_identifier)
        if match:
            return match.group(1)
    return ""
