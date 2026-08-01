import json
from datetime import date

import pytest

from src.comitato.comitato_azure_retirements_v2.contracts.aggregate_v1 import AggregateRecord
from src.comitato.comitato_azure_retirements_v2.domain.dates import (
    CommitteeWindow,
    SlideEligibility,
    add_calendar_months,
    classify_retirement_date,
)


def test_add_calendar_months_clamps_leap_day() -> None:
    assert add_calendar_months(date(2024, 2, 29), 12) == date(2025, 2, 28)


def aggregate(*, retirement_date: str = "", quality: str = "missing", claims: object = ()) -> AggregateRecord:
    return AggregateRecord.from_mapping(
        {
            "aggregate_id": "aggregate-1",
            "retirement_date": retirement_date,
            "retirement_date_quality": quality,
            "retirement_dates_json": json.dumps(claims),
            "retiring_feature": "Retire on 2027-01-01, but prose is not evidence",
        }
    )


@pytest.mark.parametrize(
    ("retirement_date", "expected"),
    [
        ("2026-07-30", SlideEligibility.ELIGIBLE),
        ("2027-07-30", SlideEligibility.ELIGIBLE),
        ("2026-07-29", SlideEligibility.ELAPSED_RETIREMENT_DATE),
        ("2027-07-31", SlideEligibility.BEYOND_COMMITTEE_WINDOW),
    ],
)
def test_classify_retirement_date_uses_inclusive_calendar_window(
    retirement_date: str, expected: SlideEligibility
) -> None:
    window = CommitteeWindow(date(2026, 7, 30))
    record = aggregate(
        retirement_date=retirement_date,
        quality="exact",
        claims=[{"date": retirement_date, "quality": "exact"}],
    )

    assert classify_retirement_date(record, window) is expected


def test_committee_window_clamps_upper_bound_for_leap_day() -> None:
    window = CommitteeWindow(date(2024, 2, 29))

    assert window.upper_bound == date(2025, 2, 28)
    assert classify_retirement_date(
        aggregate(
            retirement_date="2025-02-28",
            quality="exact",
            claims=[{"date": "2025-02-28", "quality": "exact"}],
        ),
        window,
    ) is SlideEligibility.ELIGIBLE


@pytest.mark.parametrize(
    ("quality", "retirement_date", "claims", "expected"),
    [
        ("missing", "", [], SlideEligibility.MISSING_RETIREMENT_DATE),
        ("invalid", "not-a-date", [], SlideEligibility.INVALID_RETIREMENT_DATE),
        (
            "conflict",
            "",
            [{"date": "2027-01-01"}, {"date": "2027-02-01"}],
            SlideEligibility.CONFLICTING_RETIREMENT_DATE,
        ),
    ],
)
def test_classify_retirement_date_rejects_non_exact_date_quality(
    quality: str, retirement_date: str, claims: object, expected: SlideEligibility
) -> None:
    assert classify_retirement_date(
        aggregate(retirement_date=retirement_date, quality=quality, claims=claims),
        CommitteeWindow(date(2026, 7, 30)),
    ) is expected


def test_classify_retirement_date_does_not_mine_date_like_prose() -> None:
    record = aggregate(
        retirement_date="",
        quality="missing",
        claims=[],
    )

    assert classify_retirement_date(record, CommitteeWindow(date(2026, 7, 30))) is SlideEligibility.MISSING_RETIREMENT_DATE
