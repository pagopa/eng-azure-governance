"""Date parsing and transformation helpers."""

from __future__ import annotations

import calendar
from datetime import date, datetime, timezone


def parse_iso_date(raw: str) -> date:
    """Parse a YYYY-MM-DD string into a date."""
    return datetime.strptime(raw, "%Y-%m-%d").date()


def parse_possible_date(raw: str | None) -> date | None:
    if not raw:
        return None
    raw = raw.strip()
    if not raw:
        return None

    candidates = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
    ]
    for fmt in candidates:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def normalize_datetime(raw: str | None) -> str:
    if not raw:
        return ""
    text = raw.strip()
    if not text:
        return ""

    try:
        if text.endswith("Z"):
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return ""


def add_calendar_months(base: date, months: int) -> date:
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def days_to_retirement(as_of_date: date, retirement: date | None) -> int | None:
    if retirement is None:
        return None
    return (retirement - as_of_date).days


def months_to_retirement(as_of_date: date, retirement: date | None) -> int | None:
    if retirement is None:
        return None
    delta = (retirement.year - as_of_date.year) * 12 + (retirement.month - as_of_date.month)
    if retirement.day < as_of_date.day:
        delta -= 1
    return delta
