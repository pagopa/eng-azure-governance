from dataclasses import replace
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2.acquisition.model import AcquisitionReceipt
from src.comitato.comitato_azure_retirements_v2.publication.model import (
    ValidatedStagedGeneration,
)
from src.comitato.comitato_azure_retirements_v2.publication.staging import (
    PublicationError,
    stage_candidate,
)
from tests.comitato.comitato_azure_retirements_v2.publication.test_empty_publication import (
    empty_candidate,
)


def _mutate(path: str, mutation):
    def apply(generation: Path) -> None:
        target = generation / path
        target.write_bytes(mutation(target.read_bytes()))

    return apply


def test_stage_rereads_and_validates_mutated_tsv_header(tmp_path: Path) -> None:
    candidate = empty_candidate()

    with pytest.raises(PublicationError) as raised:
        stage_candidate(
            candidate,
            tmp_path,
            staged_byte_mutator=_mutate(
                "01_azure_advisor_retirements_raw.tsv",
                lambda data: data.replace(b"schema_version", b"schema_broken", 1),
            ),
        )

    assert raised.value.diagnostics[0].artifact == "01_azure_advisor_retirements_raw.tsv"
    assert raised.value.diagnostics[0].code in {"invalid_staged_header", "staged_bytes_changed"}


def test_stage_rejects_missing_and_extra_payload_files(tmp_path: Path) -> None:
    candidate = empty_candidate()

    def remove_payload(generation: Path) -> None:
        (generation / candidate.artifacts[0].logical_path).unlink()

    with pytest.raises(PublicationError):
        stage_candidate(candidate, tmp_path, staged_byte_mutator=remove_payload)

    def add_payload(generation: Path) -> None:
        (generation / "undeclared.tsv").write_bytes(b"unexpected")

    with pytest.raises(PublicationError):
        stage_candidate(candidate, tmp_path, staged_byte_mutator=add_payload)


def test_stage_rejects_mutated_jsonl_reference_and_changed_measured_hash(tmp_path: Path) -> None:
    candidate = empty_candidate()

    def mutate_reference(generation: Path) -> None:
        (generation / "01_azure_advisor_retirements_raw.jsonl").write_bytes(
            b'{"raw_record_ref":"unpaired"}\n'
        )

    with pytest.raises(PublicationError) as raised:
        stage_candidate(candidate, tmp_path, staged_byte_mutator=mutate_reference)

    codes = {item.code for item in raised.value.diagnostics}
    assert "staged_bytes_changed" in codes
    assert "raw_pair_bijection_failed" in codes or "invalid_staged_jsonl" in codes


def test_stage_rejects_incomplete_acquisition_and_reports_no_success_manifest(tmp_path: Path) -> None:
    candidate = empty_candidate()
    incomplete = replace(
        candidate,
        acquisitions=(
            replace(
                candidate.acquisitions[0],
                receipt=replace(candidate.acquisitions[0].receipt, complete=False),
            ),
            *candidate.acquisitions[1:],
        ),
    )

    with pytest.raises(PublicationError) as raised:
        stage_candidate(incomplete, tmp_path)

    assert raised.value.diagnostics[0].code == "incomplete_acquisition"
    assert not list((tmp_path / ".staging").glob("*/publication-manifest.json"))


def test_stage_returns_validated_generation_and_manifest_uses_measured_facts(tmp_path: Path) -> None:
    staged = stage_candidate(empty_candidate(), tmp_path)

    assert isinstance(staged, ValidatedStagedGeneration)
    assert staged.manifest["validation"] == {"error_count": 0, "status": "passed"}
    for measured in staged.artifacts:
        assert measured.bytes == len((staged.generation_dir / measured.logical_path).read_bytes())
        manifest_item = next(item for item in staged.manifest["artifacts"] if item["path"] == measured.logical_path)
        assert manifest_item["bytes"] == measured.bytes
        assert manifest_item["sha256"] == measured.digest
