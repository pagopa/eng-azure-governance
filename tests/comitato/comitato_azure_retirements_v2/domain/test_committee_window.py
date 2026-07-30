from datetime import date

from src.comitato.comitato_azure_retirements_v2.domain.dates import add_calendar_months


def test_add_calendar_months_clamps_leap_day() -> None:
    assert add_calendar_months(date(2024, 2, 29), 12) == date(2025, 2, 28)
