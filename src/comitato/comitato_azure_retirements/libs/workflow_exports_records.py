"""Record builders used by aggregate workflow exports."""

from __future__ import annotations

from dataclasses import dataclass

from .dates import add_calendar_months, parse_possible_date
from .normalize_shared import parse_retirement_date_candidate
from .workflow_exports_utils import (
    DATE_CANDIDATE_PATTERN,
    extract_links,
    first_non_empty,
    sorted_unique,
)


@dataclass(frozen=True)
class PublicationSelection:
    records: list[dict[str, object]]
    excluded_by_reason: dict[str, list[str]]


def _record_identifiers(record: dict[str, object]) -> list[str]:
    identifiers = record.get("source_identifiers", [])
    if isinstance(identifiers, list):
        values = [
            str(identifier).strip()
            for identifier in identifiers
            if str(identifier).strip()
        ]
    else:
        values = []
    if values:
        return sorted(set(values))
    fallback = str(record.get("source_id") or record.get("tracking_id") or "").strip()
    return [fallback] if fallback else []


def select_publication_records(
    records: list[dict[str, object]], *, as_of_date
) -> PublicationSelection:
    upper_bound = add_calendar_months(as_of_date, 12)
    selected: list[dict[str, object]] = []
    excluded: dict[str, list[str]] = {}

    for record in records:
        source_system = str(record.get("source_system") or "")
        if (
            source_system.startswith("advisor")
            and str(record.get("platform_state") or "") != "New"
        ):
            excluded.setdefault("advisor_not_current", []).extend(
                _record_identifiers(record)
            )
            continue

        publication_date = parse_possible_date(
            str(record.get("publication_date") or "")
        )
        if publication_date is None:
            excluded.setdefault("missing_or_invalid_date", []).extend(
                _record_identifiers(record)
            )
            continue
        if publication_date < as_of_date:
            excluded.setdefault("expired", []).extend(_record_identifiers(record))
            continue
        if publication_date > upper_bound:
            excluded.setdefault("beyond_one_year", []).extend(
                _record_identifiers(record)
            )
            continue
        selected.append(record)

    return PublicationSelection(
        records=selected,
        excluded_by_reason={
            reason: sorted(set(identifiers))
            for reason, identifiers in excluded.items()
            if identifiers
        },
    )


def normalize_retirement_date(
    *,
    explicit_date: str,
    source_texts: list[str],
    exact_quality: bool,
) -> tuple[str, str, bool]:
    parsed_explicit = parse_possible_date(explicit_date)
    if parsed_explicit:
        return (
            parsed_explicit.isoformat(),
            "exact" if exact_quality else "derived",
            False,
        )

    for text in source_texts:
        if not text:
            continue
        for candidate in DATE_CANDIDATE_PATTERN.findall(text):
            resolved_candidate, derived_from_text = parse_retirement_date_candidate(
                candidate
            )
            if resolved_candidate:
                return resolved_candidate, "derived", derived_from_text

    return "", "missing", False


def classify_service_health_type(
    *, title: str, summary: str, description: str, event_sub_type: str
) -> str:
    joined_text = " ".join([title, summary, description, event_sub_type]).lower()
    if "deprecat" in joined_text:
        return "service_health_deprecation"
    if event_sub_type.strip().lower() == "retirement":
        return "service_health_retirement"
    if (
        "retire" in joined_text
        or "end of support" in joined_text
        or "sunset" in joined_text
    ):
        return "service_health_retirement"
    return "other_advisory"


def advisor_records(advisor_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in advisor_rows:
        source_identifiers = sorted_unique(
            [row.get("source_id", ""), row.get("advisor_recommendation_id", "")]
        )
        retirement_date = row.get("retirement_date", "")
        explicit_links = extract_links([row.get("learn_more_link", "")])
        retiring_feature = first_non_empty(
            [
                row.get("retiring_feature", ""),
                row.get("short_description_problem", ""),
                row.get("service_name", ""),
            ]
        )
        action_required = first_non_empty(
            [
                row.get("short_description_solution", ""),
                row.get("short_description_problem", ""),
            ]
        )
        technology_or_service = row.get("service_name", "")

        # Skip low-signal advisor metadata records that cannot produce committee-usable rows.
        if row.get("source_system", "") == "advisor_metadata" and not any(
            [retiring_feature, action_required, explicit_links, technology_or_service]
        ):
            continue

        records.append(
            {
                "source": "advisor",
                "advice_type": "advisor_retirement",
                "technology_or_service": technology_or_service,
                "_descrizione_problema_raw": row.get("short_description_problem", ""),
                "retiring_feature": retiring_feature,
                "action_required": action_required,
                "retirement_date": retirement_date,
                "subscription_id": row.get("subscription_id", ""),
                "subscription_name": row.get("subscription_name", ""),
                "source_system": row.get("source_system", "advisor_joined")
                or "advisor_joined",
                "source_identifiers": source_identifiers,
                "source_links": explicit_links,
                "publication_date": row.get("retirement_date", ""),
                "platform_state": row.get("platform_state", ""),
                "summary_text": row.get("short_description_problem", ""),
                "as_of_date": row.get("as_of_date", ""),
                "diagnostic_flags": "",
            }
        )

    return records


def service_health_records(
    service_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in service_rows:
        description_problem = row.get("description_problem", "") or row.get(
            "description", ""
        )
        source_identifiers = sorted_unique(
            [
                row.get("event_id", ""),
                row.get("tracking_id", ""),
                row.get("source_id", ""),
            ]
        )
        retirement_date = row.get("date_for_window", "")
        links = extract_links(
            [
                description_problem,
                row.get("summary", ""),
                row.get("title", ""),
            ]
        )
        records.append(
            {
                "source": "service-health",
                "advice_type": classify_service_health_type(
                    title=row.get("title", ""),
                    summary=row.get("summary", ""),
                    description=description_problem,
                    event_sub_type=row.get("event_sub_type", ""),
                ),
                "technology_or_service": row.get("impacted_service", ""),
                "_descrizione_problema_raw": description_problem,
                "retiring_feature": row.get("title", ""),
                "action_required": first_non_empty(
                    [
                        row.get("short_description_solution", ""),
                        row.get("recommended_actions", ""),
                        row.get("summary", ""),
                    ]
                ),
                "retirement_date": retirement_date,
                "subscription_id": row.get("subscription_id", ""),
                "subscription_name": row.get("subscription_name", ""),
                "source_system": row.get("source_system", "resource_health_events")
                or "resource_health_events",
                "source_identifiers": source_identifiers,
                "source_links": links,
                "publication_date": row.get("impact_mitigation_time", ""),
                "summary_text": row.get("summary", ""),
                "as_of_date": row.get("as_of_date", ""),
                "diagnostic_flags": "",
            }
        )

    return records
