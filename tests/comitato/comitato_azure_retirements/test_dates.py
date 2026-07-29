from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.dates import (
    add_calendar_months,
    days_to_retirement,
    months_to_retirement,
    normalize_datetime,
    parse_iso_date,
    parse_possible_date,
)


def test_parse_iso_date_exact() -> None:
    assert parse_iso_date("2027-03-18") == date(2027, 3, 18)


def test_parse_possible_date_unparseable() -> None:
    assert parse_possible_date("not-a-date") is None


def test_days_and_months_to_retirement() -> None:
    as_of = date(2026, 6, 18)
    assert days_to_retirement(as_of, date(2026, 6, 28)) == 10
    assert months_to_retirement(as_of, date(2026, 7, 18)) == 1


def test_add_calendar_months_clamps_to_month_end() -> None:
    assert add_calendar_months(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert add_calendar_months(date(2024, 2, 29), 12) == date(2025, 2, 28)


def test_normalize_datetime_converts_to_utc() -> None:
    assert normalize_datetime("2026-06-18T10:30:00+02:00") == "2026-06-18T08:30:00Z"
