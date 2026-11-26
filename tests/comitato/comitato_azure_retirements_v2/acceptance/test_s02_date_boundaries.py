from pathlib import Path

from src.comitato.comitato_azure_retirements_v2.src.domain.dates import (
    SlideEligibility,
)
from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import (
    assert_matches_fixture_publication,
    load_scenario,
    run_scenario,
)

FIXTURE = Path(__file__).parent.parent / "fixtures" / "s02_date_boundaries"


def test_s02_selects_only_inclusive_boundaries_and_reports_exact_exclusions(
    tmp_path: Path,
) -> None:
    result = run_scenario(load_scenario(FIXTURE), tmp_path)

    assert result.exit_status == 0
    assert [row["id_elemento"] for row in result.slide_records]  # type: ignore[attr-defined]
    assert set(result.slide_selection) == {  # type: ignore[attr-defined]
        SlideEligibility.BEYOND_COMMITTEE_WINDOW.value,
    }
    assert all(len(ids) == 1 for ids in result.slide_selection.values())  # type: ignore[attr-defined]
    assert_matches_fixture_publication(result, FIXTURE)
