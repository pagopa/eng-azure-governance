from __future__ import annotations

from pathlib import Path

from src.comitato.comitato_azure_retirements.libs import runtime_runner


def test_default_counts_by_source_contains_expected_collectors() -> None:
    assert runtime_runner._default_counts_by_source() == {
        "advisor_metadata": 0,
        "advisor_recommendations": 0,
        "resource_graph_advisorresources": 0,
        "resource_health_events": 0,
    }


def test_platforms_source_path_resolves_source_of_truth_location() -> None:
    script_path = Path(
        "src/comitato/comitato_azure_retirements/comitato-azure-retirements.py"
    ).resolve()

    assert runtime_runner._platforms_source_path(script_path) == (
        script_path.parents[2] / "_source_of_truth" / "platforms.yaml"
    )
