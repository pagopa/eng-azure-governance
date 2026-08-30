from hashlib import sha256
from pathlib import Path

from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import (
    load_scenario,
    run_scenario,
)


FIXTURE = Path(__file__).parent.parent / "fixtures" / "s12_precommit_filesystem_failure"


def test_s12_precommit_failure_emits_logical_artifact_and_preserves_seeded_current(tmp_path: Path) -> None:
    scenario = load_scenario(FIXTURE)
    seeded = {
        path.relative_to(FIXTURE / "seeded" / "current").as_posix(): path.read_bytes()
        for path in (FIXTURE / "seeded" / "current").rglob("*")
        if path.is_file()
    }
    before = {name: sha256(data).hexdigest() for name, data in seeded.items()}

    result = run_scenario(scenario, tmp_path)

    assert result.exit_status == 1
    assert result.stderr_jsonl == (FIXTURE / "expected" / "stderr.jsonl").read_bytes()
    assert result.current_tree == seeded
    after = {name: sha256(data).hexdigest() for name, data in result.current_tree.items()}
    assert after == before
