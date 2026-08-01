from pathlib import Path

from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector
from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import (
    load_scenario,
    run_scenario,
)


FIXTURE = Path(__file__).parent.parent / "fixtures" / "s06_complete_empty"


def test_s06_fixture_preserves_fixed_runtime_and_empty_scope_inputs() -> None:
    scenario = load_scenario(FIXTURE)

    assert scenario.selector is ReportSelector.ALL
    assert scenario.run_id == "s06-empty"
    assert scenario.as_of_date.isoformat() == "2026-07-30"
    assert scenario.created_at.isoformat() == "2026-07-30T00:00:00+00:00"
    assert scenario.expected_exit_status == 0
    assert scenario.scope.subscription_ids == (
        "11111111-1111-1111-1111-111111111111",
    )
    assert scenario.advisor_pages == ({"items": [], "next_link": None},)
    assert scenario.service_health_pages == ({"items": [], "next_link": None},)


def test_s06_complete_empty_matches_reviewed_expected_publication(tmp_path: Path) -> None:
    scenario = load_scenario(FIXTURE)

    result = run_scenario(scenario, tmp_path)

    assert result.exit_status == 0
    assert result.stderr_jsonl == (FIXTURE / "expected" / "stderr.jsonl").read_bytes()
    assert result.current_tree == {
        relative_path: (FIXTURE / "expected" / "current" / relative_path).read_bytes()
        for relative_path in sorted(
            path.name for path in (FIXTURE / "expected" / "current").iterdir()
        )
    }
