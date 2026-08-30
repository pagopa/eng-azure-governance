from pathlib import Path

import pytest

from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import load_scenario, run_scenario


FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.parametrize("name", ("s01_explicitly_correlated", "s04_ambiguous_correlation", "s05_pagination_duplicate"))
def test_positive_publication_scenarios_match_complete_golden_trees(name: str, tmp_path: Path) -> None:
    fixture = FIXTURES / name
    result = run_scenario(load_scenario(fixture), tmp_path)

    expected = {
        relative_path: (fixture / "expected" / "current" / relative_path).read_bytes()
        for relative_path in sorted(path.name for path in (fixture / "expected" / "current").iterdir())
    }
    assert result.exit_status == 0
    assert result.stderr_jsonl == b""
    assert result.current_tree == expected
    aggregate_rows = result.current_tree["02_azure_retirements_aggregate.tsv"].decode().splitlines()
    if name == "s01_explicitly_correlated":
        assert aggregate_rows[1].split("\t")[4] == "explicitly_correlated"
        slide_row = result.current_tree["03_azure_retirements_slide.tsv"].decode().splitlines()[1]
        assert slide_row.endswith("\t\t\t\t")
    elif name == "s04_ambiguous_correlation":
        assert len(aggregate_rows) == 4
        assert all(row.split("\t")[4] == "ambiguous_unmerged" for row in aggregate_rows[1:])
    else:
        assert len(result.current_tree["01_azure_advisor_retirements_raw.tsv"].decode().splitlines()) == 2
        manifest = result.current_tree["publication-manifest.json"].decode()
        assert '"pages":2,"source_records":1' in manifest
