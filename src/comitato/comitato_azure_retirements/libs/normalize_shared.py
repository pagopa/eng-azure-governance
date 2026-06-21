"""Shared normalization helpers for Advisor and Service Health rows."""

from __future__ import annotations

from datetime import datetime
import re

from .dates import parse_possible_date

RETIREMENT_KEYWORD_PATTERN = re.compile(
    r"retire|deprecat|end of support|sunset", re.IGNORECASE
)
DATE_CANDIDATE_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})"
)
TEXT_DATE_FORMATS = (
    "%d %B %Y",
    "%d %b %Y",
    "%B %d, %Y",
    "%b %d, %Y",
)


def parse_retirement_date_candidate(candidate: str) -> tuple[str, bool]:
    parsed_candidate = parse_possible_date(candidate)
    if parsed_candidate:
        return parsed_candidate.isoformat(), False

    normalized = " ".join(candidate.split())
    for date_format in TEXT_DATE_FORMATS:
        try:
            return datetime.strptime(normalized, date_format).date().isoformat(), True
        except ValueError:
            continue

    return "", False


def extract_retirement_deadline_from_text(
    *,
    title: str,
    summary: str,
    description: str,
    recommended_actions: str,
) -> tuple[str, bool]:
    for text in [title, summary, recommended_actions, description]:
        if not text or not RETIREMENT_KEYWORD_PATTERN.search(text):
            continue

        for candidate in DATE_CANDIDATE_PATTERN.findall(text):
            parsed_date, derived_from_text = parse_retirement_date_candidate(candidate)
            if parsed_date:
                return parsed_date, derived_from_text

    return "", False


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
) -> tuple[str, bool]:
    explicit_deadline, derived_from_text = extract_retirement_deadline_from_text(
        title=title,
        summary=summary,
        description=description,
        recommended_actions=recommended_actions,
    )

    if explicit_deadline:
        return explicit_deadline, derived_from_text

    for candidate in [
        date_from_normalized_datetime(impact_mitigation),
        date_from_normalized_datetime(impact_start),
        date_from_normalized_datetime(last_update),
    ]:
        if candidate:
            return candidate, False

    return "", False
