"""Structured retirement-date handling used by aggregate and slide stages."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date


def add_calendar_months(value: date, months: int) -> date:
    """Add calendar months and clamp to the last valid day of the month."""

    if months < 0:
        raise ValueError("months must be non-negative")
    month_index = value.year * 12 + value.month - 1 + months
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    return date(year, month, min(value.day, monthrange(year, month)[1]))


@dataclass(frozen=True, slots=True)
class RetirementDateClaim:
    raw_value: str
    value: date | None
    quality: str
    source_path: str = ""
    source_system: str = ""
    raw_record_ref: str = ""


def parse_retirement_date(raw_value: object, *, source_path: str = "", source_system: str = "", raw_record_ref: str = "") -> RetirementDateClaim:
    raw = "" if raw_value is None else str(raw_value).strip()
    if not raw:
        return RetirementDateClaim(raw, None, "missing", source_path, source_system, raw_record_ref)
    try:
        parsed = date.fromisoformat(raw[:10])
    except ValueError:
        return RetirementDateClaim(raw, None, "invalid", source_path, source_system, raw_record_ref)
    return RetirementDateClaim(raw, parsed, "exact", source_path, source_system, raw_record_ref)


__all__ = ["RetirementDateClaim", "add_calendar_months", "parse_retirement_date"]
