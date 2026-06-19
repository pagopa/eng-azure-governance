"""Workflow helpers for raw, aggregate, and slide exports."""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

import pandas as pd
import yaml
from dateutil import parser as date_parser

from .dates import parse_possible_date
from .tsv import compact_json


RAW_ADVISOR_FILENAME = "azure_advisor_retirements_aggregate.tsv"
RAW_SERVICE_HEALTH_FILENAME = "azure_service_health_advisories_aggregate.tsv"
AGGREGATE_FILENAME = "02_azure_retirements_aggregate.tsv"
SLIDE_FILENAME = "03_azure_retirements_slide.tsv"
UNKNOWN_PLATFORM = "Unknown Platform"

_WHITESPACE = re.compile(r"\s+")
_URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
_DATE_CANDIDATE_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})"
)


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
            normalized_subscription = _normalize_key(subscription_name)
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
    records = _advisor_records(advisor_rows) + _service_health_records(service_rows)
    if not records:
        return []

    frame = pd.DataFrame.from_records(records).fillna("")
    frame["canonical_title"] = frame["retiring_feature"].map(_canonical_title)
    frame["canonical_date"] = frame["retirement_date"].map(lambda value: value if value else "na")
    frame["advisory_key"] = frame.apply(
        lambda row: _build_advisory_key(
            advice_type=str(row["advice_type"]),
            canonical_title=str(row["canonical_title"]),
            canonical_date=str(row["canonical_date"]),
            source_identifiers=row["source_identifiers"],
        ),
        axis=1,
    )

    grouped_rows: list[dict[str, str]] = []
    for advisory_key, group in frame.groupby("advisory_key", sort=True):
        grouped_rows.append(
            _aggregate_group(
                advisory_key=str(advisory_key),
                rows=group.to_dict("records"),
                active_platform_map=active_platform_map,
                as_of_date=as_of_date,
            )
        )

    grouped_rows.sort(key=lambda row: row["advisory_key"])
    return grouped_rows


def build_slide_rows(aggregate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Project aggregate rows into the committee slide subset schema."""
    projected_rows: list[dict[str, str]] = []
    for row in aggregate_rows:
        projected_rows.append(
            {
                "priority_label": row.get("priority_label", ""),
                "retiring_feature": row.get("retiring_feature", ""),
                "action_required": row.get("action_required", "") or row.get("summary_text", ""),
                "retirement_date": row.get("retirement_date", ""),
                "platforms": row.get("impacted_platforms", ""),
                "platforms_subscriptions_json": row.get("impacted_platforms_subscriptions_json", ""),
                "advice_type": row.get("advice_type", ""),
                "source_links": row.get("source_links", ""),
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
            row.get("retiring_feature", "").lower(),
        )
    )
    return projected_rows


def _advisor_records(advisor_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in advisor_rows:
        retirement_date, retirement_quality = _normalize_retirement_date(
            explicit_date=row.get("retirement_date", ""),
            source_texts=[row.get("short_description_problem", "")],
            exact_quality=True,
        )
        links = _extract_links([row.get("action_link", ""), row.get("learn_more_link", "")])
        source_identifiers = _sorted_unique(
            [row.get("source_id", ""), row.get("advisor_recommendation_id", "")]
        )
        records.append(
            {
                "advice_type": "advisor_retirement",
                "retiring_feature": _first_non_empty([row.get("retiring_feature", ""), row.get("service_name", "")]),
                "action_required": _first_non_empty(
                    [
                        row.get("short_description_solution", ""),
                        row.get("short_description_problem", ""),
                        row.get("description", ""),
                    ]
                ),
                "retirement_date": retirement_date,
                "retirement_date_quality": retirement_quality,
                "subscription_name": row.get("subscription_name", ""),
                "source_system": row.get("source_system", "advisor_joined") or "advisor_joined",
                "source_identifiers": source_identifiers,
                "source_links": links,
                "summary_text": _first_non_empty([row.get("short_description_problem", ""), row.get("retiring_feature", "")]),
                "details_text": row.get("description", ""),
                "as_of_date": row.get("as_of_date", ""),
            }
        )

    return records


def _service_health_records(service_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in service_rows:
        retirement_date, retirement_quality = _normalize_retirement_date(
            explicit_date=row.get("date_for_window", ""),
            source_texts=[
                row.get("title", ""),
                row.get("summary", ""),
                row.get("recommended_actions", ""),
                row.get("description", ""),
            ],
            exact_quality=False,
        )
        links = _extract_links([row.get("description", ""), row.get("recommended_actions", "")])
        source_identifiers = _sorted_unique(
            [row.get("event_id", ""), row.get("tracking_id", ""), row.get("source_id", "")]
        )
        records.append(
            {
                "advice_type": _classify_service_health_type(
                    title=row.get("title", ""),
                    summary=row.get("summary", ""),
                    description=row.get("description", ""),
                    event_sub_type=row.get("event_sub_type", ""),
                ),
                "retiring_feature": _first_non_empty([row.get("title", ""), row.get("summary", "")]),
                "action_required": _first_non_empty([row.get("recommended_actions", ""), row.get("summary", "")]),
                "retirement_date": retirement_date,
                "retirement_date_quality": retirement_quality,
                "subscription_name": row.get("subscription_name", ""),
                "source_system": row.get("source_system", "resource_health_events") or "resource_health_events",
                "source_identifiers": source_identifiers,
                "source_links": links,
                "summary_text": _first_non_empty([row.get("summary", ""), row.get("title", "")]),
                "details_text": row.get("description", ""),
                "as_of_date": row.get("as_of_date", ""),
            }
        )

    return records


def _aggregate_group(
    *,
    advisory_key: str,
    rows: list[dict[str, object]],
    active_platform_map: dict[str, str],
    as_of_date: date,
) -> dict[str, str]:
    source_identifiers = _sorted_unique(item for row in rows for item in _as_string_list(row.get("source_identifiers")))
    source_links = _sorted_unique(item for row in rows for item in _as_string_list(row.get("source_links")))
    source_systems = _sorted_unique(str(row.get("source_system", "")) for row in rows)
    subscription_names = _sorted_unique(str(row.get("subscription_name", "")) for row in rows)

    platform_subscriptions: dict[str, set[str]] = defaultdict(set)
    for subscription_name in subscription_names:
        if not subscription_name:
            continue
        platform_name = active_platform_map.get(_normalize_key(subscription_name), UNKNOWN_PLATFORM)
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

    retirement_candidates = _sorted_unique(str(row.get("retirement_date", "")) for row in rows)
    parsed_dates = [candidate for candidate in retirement_candidates if parse_possible_date(candidate)]
    chosen_retirement_date = ""
    retirement_quality = "missing"
    if parsed_dates:
        chosen_retirement_date = min(parsed_dates)
        any_derived = any(
            str(row.get("retirement_date", "")) == chosen_retirement_date
            and str(row.get("retirement_date_quality", "")) == "derived"
            for row in rows
        )
        retirement_quality = "derived" if any_derived else "exact"

    first_seen_date = _min_iso_date(str(row.get("as_of_date", "")) for row in rows)
    last_seen_date = _max_iso_date(str(row.get("as_of_date", "")) for row in rows)

    retiring_feature = _pick_human_text(str(row.get("retiring_feature", "")) for row in rows)
    summary_text = _pick_human_text(str(row.get("summary_text", "")) for row in rows)
    details_text = _pick_human_text(str(row.get("details_text", "")) for row in rows)
    action_required = _pick_human_text(str(row.get("action_required", "")) for row in rows)
    if not action_required:
        action_required = summary_text

    advice_type = _first_non_empty([str(row.get("advice_type", "")) for row in rows])
    priority_label = _priority_label(retirement_date=chosen_retirement_date, as_of_date=as_of_date)

    return {
        "advice_type": advice_type,
        "advisory_key": advisory_key,
        "retiring_feature": retiring_feature,
        "action_required": action_required,
        "retirement_date": chosen_retirement_date,
        "retirement_date_quality": retirement_quality,
        "priority_label": priority_label,
        "impacted_platforms": impacted_platforms,
        "impacted_platforms_subscriptions_json": compact_json(platform_json),
        "impacted_subscriptions": ", ".join(subscription_names),
        "source_systems": ", ".join(source_systems),
        "source_identifiers": ", ".join(source_identifiers),
        "source_links": ", ".join(source_links),
        "summary_text": summary_text,
        "details_text": details_text,
        "first_seen_date": first_seen_date,
        "last_seen_date": last_seen_date,
    }


def _normalize_retirement_date(
    *,
    explicit_date: str,
    source_texts: list[str],
    exact_quality: bool,
) -> tuple[str, str]:
    parsed_explicit = parse_possible_date(explicit_date)
    if parsed_explicit:
        return parsed_explicit.isoformat(), "exact" if exact_quality else "derived"

    for text in source_texts:
        if not text:
            continue
        for candidate in _DATE_CANDIDATE_PATTERN.findall(text):
            parsed_candidate = parse_possible_date(candidate)
            if parsed_candidate:
                return parsed_candidate.isoformat(), "derived"
            try:
                parsed_any = date_parser.parse(candidate, fuzzy=True)
            except (TypeError, ValueError, date_parser.ParserError):
                continue
            return parsed_any.date().isoformat(), "derived"

    return "", "missing"


def _classify_service_health_type(*, title: str, summary: str, description: str, event_sub_type: str) -> str:
    joined_text = " ".join([title, summary, description, event_sub_type]).lower()
    if "deprecat" in joined_text:
        return "service_health_deprecation"
    if event_sub_type.strip().lower() == "retirement":
        return "service_health_retirement"
    if "retire" in joined_text or "end of support" in joined_text or "sunset" in joined_text:
        return "service_health_retirement"
    return "other_advisory"


def _extract_links(texts: list[str]) -> list[str]:
    links: list[str] = []
    for text in texts:
        if not text:
            continue
        for link in _URL_PATTERN.findall(text):
            clean_link = link.rstrip(".,);\"]")
            if clean_link:
                links.append(clean_link)
    return _sorted_unique(links)


def _build_advisory_key(
    *,
    advice_type: str,
    canonical_title: str,
    canonical_date: str,
    source_identifiers: object,
) -> str:
    base_key = f"{advice_type}|{canonical_title}|{canonical_date}"
    if canonical_title:
        return base_key

    identifiers = _as_string_list(source_identifiers)
    digest = hashlib.sha1("|".join(identifiers).encode("utf-8")).hexdigest()[:12]
    return f"{base_key}|{digest}"


def _canonical_title(value: object) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    return _WHITESPACE.sub(" ", text)


def _normalize_key(value: str) -> str:
    return _WHITESPACE.sub(" ", value.strip().lower())


def _sorted_unique(values) -> list[str]:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    return sorted(set(cleaned), key=str.lower)


def _as_string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _first_non_empty(values: list[str]) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""


def _pick_human_text(values) -> str:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    if not cleaned:
        return ""
    cleaned.sort(key=lambda value: (len(value), value.lower()), reverse=True)
    return cleaned[0]


def _min_iso_date(values) -> str:
    valid_dates = sorted(value for value in values if parse_possible_date(value))
    return valid_dates[0] if valid_dates else ""


def _max_iso_date(values) -> str:
    valid_dates = sorted(value for value in values if parse_possible_date(value))
    return valid_dates[-1] if valid_dates else ""


def _priority_label(*, retirement_date: str, as_of_date: date) -> str:
    parsed_date = parse_possible_date(retirement_date)
    if parsed_date is None:
        return "Debito"

    days_to_retirement = (parsed_date - as_of_date).days
    if days_to_retirement <= 90:
        return "Critico"
    if days_to_retirement <= 180:
        return "Prioritario"
    if days_to_retirement <= 365:
        return "Da pianificare"
    return "Debito"
