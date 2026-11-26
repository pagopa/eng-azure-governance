from pathlib import Path

import pytest

from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import (
    assert_matches_fixture_publication,
    load_scenario,
    run_scenario,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.parametrize(
    "name",
    (
        "s01_explicitly_correlated",
        "s04_ambiguous_correlation",
        "s05_pagination_duplicate",
    ),
)
def test_positive_publication_scenarios_match_complete_golden_trees(
    name: str, tmp_path: Path
) -> None:
    fixture = FIXTURES / name
    result = run_scenario(load_scenario(fixture), tmp_path)

    assert result.exit_status == 0
    assert result.stderr_jsonl == b""
    assert_matches_fixture_publication(result, fixture)
    aggregate_rows = (
        result.current_tree["02_azure_retirements_aggregate.tsv"].decode().splitlines()
    )
    if name == "s01_explicitly_correlated":
        assert aggregate_rows[1].split("\t")[4] == "single_source"
        assert "03_azure_retirements_slide.tsv" not in result.current_tree
    elif name == "s04_ambiguous_correlation":
        assert len(aggregate_rows) == 4
        assert all(row.split("\t")[4] == "single_source" for row in aggregate_rows[1:])
    else:
        assert (
            len(
                result.current_tree["01_azure_advisor_retirements_raw.tsv"]
                .decode()
                .splitlines()
            )
            == 2
        )
        manifest = (
            tmp_path.with_name(f"{tmp_path.name}-support")
            / "2026"
            / "07"
            / "publication-manifest.json"
        ).read_text(encoding="utf-8")
        assert '"pages":2,"source_records":1' in manifest
