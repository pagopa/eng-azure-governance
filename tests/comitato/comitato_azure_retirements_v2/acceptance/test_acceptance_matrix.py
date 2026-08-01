from __future__ import annotations

import json
from pathlib import Path


FIXTURES = Path(__file__).parent.parent / "fixtures"
MATRIX = {
    "S1": {"fixture": "s01_explicitly_correlated", "proof": "golden-tree"},
    "S2": {"fixture": "s02_date_boundaries", "proof": "golden-tree"},
    "S3": {"fixture": "s03_explicit_global", "proof": "golden-tree"},
    "S4": {"fixture": "s04_ambiguous_correlation", "proof": "golden-tree"},
    "S5": {"fixture": "s05_pagination_duplicate", "proof": "golden-tree"},
    "S6": {"fixture": "s06_complete_empty", "proof": "golden-tree"},
    "S7": {"fixture": "s07_missing_non_global_subscription", "proof": "unchanged-current"},
    "S8": {"fixture": "s08_unmapped_subscription", "proof": "unchanged-current"},
    "S9": {"fixture": "s09_conflicting_duplicate_identity", "proof": "unchanged-current"},
    "S10": {"fixture": "s10_incomplete_acquisition", "proof": "unchanged-current"},
    "S11": {"fixture": "s11_invalid_classification_schema", "proof": "unchanged-current"},
    "S12": {"fixture": "s12_precommit_filesystem_failure", "proof": "unchanged-current"},
}


def test_acceptance_matrix_has_exactly_s1_to_s12_with_proof_metadata() -> None:
    assert set(MATRIX) == {f"S{index}" for index in range(1, 13)}
    for scenario_id, metadata in MATRIX.items():
        fixture = FIXTURES / metadata["fixture"]
        scenario = json.loads((fixture / "scenario.json").read_text(encoding="utf-8"))
        assert metadata["proof"] in {"golden-tree", "unchanged-current"}
        assert scenario["expected_exit_status"] == (0 if metadata["proof"] == "golden-tree" else 1)
        assert (fixture / "catalog.yaml").is_file()
        assert (fixture / "expected" / "stderr.jsonl").is_file()
        if metadata["proof"] == "golden-tree":
            assert (fixture / "expected" / "current").is_dir()
            assert {path.name for path in (fixture / "expected" / "current").iterdir()} >= {
                "publication-manifest.json"
            }
        else:
            assert (fixture / "expected" / "exit-status.txt").is_file()
            assert (fixture / "seeded" / "current").is_dir()
