from pathlib import Path

import pytest

from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import (
    load_scenario,
    run_scenario,
)


FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.parametrize(
    "name",
    (
        "s09_conflicting_duplicate_identity",
        "s10_incomplete_acquisition",
        "s11_invalid_classification_schema",
    ),
)
def test_negative_acceptance_scenarios_emit_stable_errors_and_publish_nothing(
    name: str, tmp_path: Path
) -> None:
    fixture = FIXTURES / name
    scenario = load_scenario(fixture)

    result = run_scenario(scenario, tmp_path)

    assert result.exit_status == int((fixture / "expected" / "exit-status.txt").read_text())
    assert result.stderr_jsonl == (fixture / "expected" / "stderr.jsonl").read_bytes()
    assert result.current_tree == {}
