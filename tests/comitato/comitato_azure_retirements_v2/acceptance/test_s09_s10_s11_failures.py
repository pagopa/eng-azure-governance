from pathlib import Path
from dataclasses import replace

import pytest

from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import (
    load_scenario,
    run_scenario,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import ReportSelector


FIXTURES = Path(__file__).parent.parent / "fixtures"


def seeded_current(fixture: Path) -> dict[str, bytes]:
    root = fixture / "seeded" / "current"
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


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
    assert result.current_tree == seeded_current(fixture)


def test_s07_missing_non_global_subscription_is_blocking_and_publishes_nothing(tmp_path):
    fixture = FIXTURES / "s07_missing_non_global_subscription"
    scenario = load_scenario(fixture)
    result = run_scenario(scenario, tmp_path)
    assert result.exit_status == 1
    assert result.stderr_jsonl == (fixture / "expected" / "stderr.jsonl").read_bytes()
    assert result.current_tree == seeded_current(fixture)


def test_s08_unmapped_subscription_blocks_every_selector(tmp_path_factory):
    fixture = FIXTURES / "s08_unmapped_subscription"
    base = load_scenario(fixture)
    for selector in ReportSelector:
        scenario = replace(base, selector=selector, run_id=f"s08-{selector.value}")
        destination = tmp_path_factory.mktemp(selector.value)
        result = run_scenario(scenario, destination)
        assert result.exit_status == 1
        assert result.current_tree == seeded_current(fixture)
        assert b'"code":"platform_mapping_unmapped_subscription"' in result.stderr_jsonl


def test_s03_explicit_global_raw_evidence_has_no_subscription_fallback(tmp_path):
    fixture = FIXTURES / "s03_explicit_global"
    scenario = load_scenario(fixture)
    result = run_scenario(scenario, tmp_path)
    assert result.exit_status == 0
    raw = result.current_tree["01_azure_service_health_advisories_raw.tsv"].decode()
    header, row = raw.splitlines()
    values = dict(zip(header.split("\t"), row.split("\t"), strict=True))
    assert values["record_type"] == "service_health_event_global"
    assert values["subscription_id"] == ""
    assert values["subscription_evidence_source"] == "explicit_global"
    expected = {
        relative_path: (fixture / "expected" / "current" / relative_path).read_bytes()
        for relative_path in sorted(path.name for path in (fixture / "expected" / "current").iterdir())
    }
    assert result.current_tree == expected
