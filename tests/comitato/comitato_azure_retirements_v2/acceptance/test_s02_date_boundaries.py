from pathlib import Path

from src.comitato.comitato_azure_retirements_v2.domain.dates import SlideEligibility
from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import load_scenario, run_scenario


FIXTURE = Path(__file__).parent.parent / "fixtures" / "s02_date_boundaries"


def test_s02_selects_only_inclusive_boundaries_and_reports_exact_exclusions(tmp_path: Path) -> None:
    result = run_scenario(load_scenario(FIXTURE), tmp_path)

    assert result.exit_status == 0
    assert [row["aggregate_id"] for row in result.slide_records]  # type: ignore[attr-defined]
    assert set(result.slide_selection) == {  # type: ignore[attr-defined]
        SlideEligibility.ELAPSED_RETIREMENT_DATE.value,
        SlideEligibility.BEYOND_COMMITTEE_WINDOW.value,
        SlideEligibility.MISSING_RETIREMENT_DATE.value,
        SlideEligibility.INVALID_RETIREMENT_DATE.value,
        SlideEligibility.CONFLICTING_RETIREMENT_DATE.value,
    }
    assert all(len(ids) == 1 for ids in result.slide_selection.values())  # type: ignore[attr-defined]
    expected = {
        relative_path: (FIXTURE / "expected" / "current" / relative_path).read_bytes()
        for relative_path in sorted(path.name for path in (FIXTURE / "expected" / "current").iterdir())
    }
    assert result.current_tree == expected
