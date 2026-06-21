"""Shared normalization helpers for Advisor and Service Health rows."""

from __future__ import annotations

import re

from dateutil import parser as date_parser

from .dates import parse_possible_date

RETIREMENT_KEYWORD_PATTERN = re.compile(
    r"retire|deprecat|end of support|sunset", re.IGNORECASE
)
DATE_CANDIDATE_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})"
)


def extract_retirement_deadline_from_text(
    *,
    title: str,
    summary: str,
    description: str,
    recommended_actions: str,
) -> str:
    for text in [title, summary, recommended_actions, description]:
        if not text or not RETIREMENT_KEYWORD_PATTERN.search(text):
            continue

        for candidate in DATE_CANDIDATE_PATTERN.findall(text):
            parsed_candidate = parse_possible_date(candidate)
            if parsed_candidate:
                return parsed_candidate.isoformat()
            try:
                parsed_any = date_parser.parse(candidate, fuzzy=True)
            except (TypeError, ValueError, date_parser.ParserError):
                continue
            return parsed_any.date().isoformat()

    return ""


def date_from_normalized_datetime(raw: str) -> str:
    if not raw:
        return ""
    return raw[:10]


def service_health_date_for_window(
    *,
    title: str,
    summary: str,
    description: str,
    recommended_actions: str,
    impact_mitigation: str,
    impact_start: str,
    last_update: str,
) -> str:
    explicit_deadline = extract_retirement_deadline_from_text(
        title=title,
        summary=summary,
        description=description,
        recommended_actions=recommended_actions,
    )

    for candidate in [
        explicit_deadline,
        date_from_normalized_datetime(impact_mitigation),
        date_from_normalized_datetime(impact_start),
        date_from_normalized_datetime(last_update),
    ]:
        if candidate:
            return candidate

    return ""
