from __future__ import annotations

from datetime import date

from src.comitato.comitato_azure_retirements.libs.dates import days_until, months_until, parse_iso_date


def test_parse_iso_date_exact() -> None:
    value, quality = parse_iso_date("2027-03-18")
    assert value == "2027-03-18"
    assert quality == "exact"


def test_parse_iso_date_unparseable() -> None:
    value, quality = parse_iso_date("not-a-date")
    assert value == ""
    assert quality == "unparseable"


def test_days_and_months_until() -> None:
    as_of = date(2026, 6, 18)
    assert days_until(as_of, "2026-06-28") == 10
    assert months_until(as_of, "2026-07-18") == 0.99
