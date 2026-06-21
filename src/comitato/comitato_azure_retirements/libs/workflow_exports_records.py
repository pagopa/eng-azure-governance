"""Record builders used by aggregate workflow exports."""

from __future__ import annotations

from dateutil import parser as date_parser

from .dates import parse_possible_date
from .workflow_exports_utils import (
    DATE_CANDIDATE_PATTERN,
    extract_links,
    first_non_empty,
    infer_technology_from_text,
    sorted_unique,
    traceable_links_from_identifiers,
)


def normalize_retirement_date(
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
        for candidate in DATE_CANDIDATE_PATTERN.findall(text):
            parsed_candidate = parse_possible_date(candidate)
            if parsed_candidate:
                return parsed_candidate.isoformat(), "derived"
            try:
                parsed_any = date_parser.parse(candidate, fuzzy=True)
            except (TypeError, ValueError, date_parser.ParserError):
                continue
            return parsed_any.date().isoformat(), "derived"

    return "", "missing"


def classify_service_health_type(*, title: str, summary: str, description: str, event_sub_type: str) -> str:
    joined_text = " ".join([title, summary, description, event_sub_type]).lower()
    if "deprecat" in joined_text:
        return "service_health_deprecation"
    if event_sub_type.strip().lower() == "retirement":
        return "service_health_retirement"
    if "retire" in joined_text or "end of support" in joined_text or "sunset" in joined_text:
        return "service_health_retirement"
    return "other_advisory"


def advisor_records(advisor_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in advisor_rows:
        source_identifiers = sorted_unique(
            [row.get("source_id", ""), row.get("advisor_recommendation_id", "")]
        )
        retirement_date, retirement_quality = normalize_retirement_date(
            explicit_date=row.get("retirement_date", ""),
            source_texts=[
                row.get("short_description_problem", ""),
                row.get("short_description_solution", ""),
                row.get("description", ""),
            ],
            exact_quality=True,
        )
        explicit_links = extract_links(
            [
                row.get("action_link", ""),
                row.get("learn_more_link", ""),
                row.get("description", ""),
                row.get("short_description_solution", ""),
                row.get("short_description_problem", ""),
            ]
        )
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
                row.get("description", ""),
            ]
        )
        technology_or_service = first_non_empty(
            [
                row.get("service_name", ""),
                infer_technology_from_text(
                    candidates=[
                        row.get("retiring_feature", ""),
                        row.get("short_description_problem", ""),
                        row.get("description", ""),
                    ]
                ),
            ]
        )

        # Skip low-signal advisor metadata records that cannot produce committee-usable rows.
        if row.get("source_system", "") == "advisor_metadata" and not any(
            [retiring_feature, action_required, explicit_links, technology_or_service]
        ):
            continue

        links = explicit_links or traceable_links_from_identifiers(source_identifiers)

        records.append(
            {
                "advice_type": "advisor_retirement",
                "technology_or_service": technology_or_service,
                "retiring_feature": retiring_feature,
                "action_required": action_required,
                "retirement_date": retirement_date,
                "retirement_date_quality": retirement_quality,
                "subscription_name": row.get("subscription_name", ""),
                "source_system": row.get("source_system", "advisor_joined") or "advisor_joined",
                "source_identifiers": source_identifiers,
                "source_links": links,
                "summary_text": first_non_empty(
                    [row.get("short_description_problem", ""), row.get("retiring_feature", "")]
                ),
                "details_text": row.get("description", ""),
                "as_of_date": row.get("as_of_date", ""),
            }
        )

    return records


def service_health_records(service_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for row in service_rows:
        source_identifiers = sorted_unique(
            [row.get("event_id", ""), row.get("tracking_id", ""), row.get("source_id", "")]
        )
        retirement_date, retirement_quality = normalize_retirement_date(
            explicit_date=row.get("date_for_window", ""),
            source_texts=[
                row.get("title", ""),
                row.get("summary", ""),
                row.get("recommended_actions", ""),
                row.get("description", ""),
            ],
            exact_quality=False,
        )
        links = extract_links(
            [
                row.get("description", ""),
                row.get("recommended_actions", ""),
                row.get("summary", ""),
                row.get("title", ""),
            ]
        )
        if not links:
            links = traceable_links_from_identifiers(source_identifiers)
        technology_or_service = first_non_empty(
            [
                row.get("impacted_service", ""),
                infer_technology_from_text(
                    candidates=[
                        row.get("title", ""),
                        row.get("summary", ""),
                        row.get("description", ""),
                        row.get("event_sub_type", ""),
                    ]
                ),
            ]
        )
        records.append(
            {
                "advice_type": classify_service_health_type(
                    title=row.get("title", ""),
                    summary=row.get("summary", ""),
                    description=row.get("description", ""),
                    event_sub_type=row.get("event_sub_type", ""),
                ),
                "technology_or_service": technology_or_service,
                "retiring_feature": first_non_empty(
                    [row.get("title", ""), row.get("summary", ""), row.get("impacted_service", "")]
                ),
                "action_required": first_non_empty(
                    [
                        row.get("recommended_actions", ""),
                        row.get("summary", ""),
                        row.get("description", ""),
                    ]
                ),
                "retirement_date": retirement_date,
                "retirement_date_quality": retirement_quality,
                "subscription_name": row.get("subscription_name", ""),
                "source_system": row.get("source_system", "resource_health_events") or "resource_health_events",
                "source_identifiers": source_identifiers,
                "source_links": links,
                "summary_text": first_non_empty([row.get("summary", ""), row.get("title", "")]),
                "details_text": row.get("description", ""),
                "as_of_date": row.get("as_of_date", ""),
            }
        )

    return records
