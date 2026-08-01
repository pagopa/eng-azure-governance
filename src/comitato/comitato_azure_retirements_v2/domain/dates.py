"""Structured retirement-date handling used by aggregate and slide stages."""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from enum import Enum
import json


def add_calendar_months(value: date, months: int) -> date:
    """Add calendar months and clamp to the last valid day of the month."""

    if months < 0:
        raise ValueError("months must be non-negative")
    month_index = value.year * 12 + value.month - 1 + months
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    return date(year, month, min(value.day, monthrange(year, month)[1]))


@dataclass(frozen=True, slots=True)
class CommitteeWindow:
    as_of_date: date
    months: int = 12

    def __post_init__(self) -> None:
        if self.months < 0:
            raise ValueError("months must be non-negative")

    @property
    def lower_bound(self) -> date:
        return self.as_of_date

    @property
    def upper_bound(self) -> date:
        return add_calendar_months(self.as_of_date, self.months)


class SlideEligibility(str, Enum):
    ELIGIBLE = "eligible"
    ELAPSED_RETIREMENT_DATE = "elapsed_retirement_date"
    BEYOND_COMMITTEE_WINDOW = "beyond_committee_window"
    MISSING_RETIREMENT_DATE = "missing_retirement_date"
    INVALID_RETIREMENT_DATE = "invalid_retirement_date"
    CONFLICTING_RETIREMENT_DATE = "conflicting_retirement_date"


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


def _strict_iso_date(raw_value: object) -> date | None:
    raw = "" if raw_value is None else str(raw_value).strip()
    if len(raw) != 10 or raw[4] != "-" or raw[7] != "-":
        return None
    try:
        parsed = date.fromisoformat(raw)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == raw else None


def _has_structured_exact_claim(aggregate, retirement_date: str) -> bool:
    try:
        claims = json.loads(aggregate["retirement_dates_json"])
    except (KeyError, TypeError, json.JSONDecodeError):
        return False
    if not isinstance(claims, list):
        return False
    return any(
        isinstance(claim, dict)
        and claim.get("date") == retirement_date
        and claim.get("quality", "exact") == "exact"
        for claim in claims
    )


def classify_retirement_date(aggregate, window: CommitteeWindow) -> SlideEligibility:
    quality = str(aggregate["retirement_date_quality"]).strip()
    if quality == "missing":
        return SlideEligibility.MISSING_RETIREMENT_DATE
    if quality == "conflict":
        return SlideEligibility.CONFLICTING_RETIREMENT_DATE
    if quality != "exact":
        return SlideEligibility.INVALID_RETIREMENT_DATE

    raw_date = str(aggregate["retirement_date"]).strip()
    retirement_date = _strict_iso_date(raw_date)
    if retirement_date is None or not _has_structured_exact_claim(aggregate, raw_date):
        return SlideEligibility.INVALID_RETIREMENT_DATE
    if retirement_date < window.lower_bound:
        return SlideEligibility.ELAPSED_RETIREMENT_DATE
    if retirement_date > window.upper_bound:
        return SlideEligibility.BEYOND_COMMITTEE_WINDOW
    return SlideEligibility.ELIGIBLE


__all__ = [
    "CommitteeWindow",
    "RetirementDateClaim",
    "SlideEligibility",
    "add_calendar_months",
    "classify_retirement_date",
    "parse_retirement_date",
]
