from __future__ import annotations

import importlib
from pathlib import Path

import pytest

try:
    committee = importlib.import_module("src.comitato.comitato_azure_retirements_v2.domain.committee")
except ModuleNotFoundError:
    committee = None


def test_merge_preserves_committee_text_only_when_description_is_unchanged() -> None:
    assert committee is not None, "committee merge module is missing"
    old = {
        "same": {
            "comitato_descrizione": "Keep this wording",
            "comitato_retirement_date": "2027-01-15",
            "descrizione_originale_completa": "Same source text",
        },
        "changed": {
            "comitato_descrizione": "Reset this wording",
            "comitato_retirement_date": "2027-02-15",
            "descrizione_originale_completa": "Old source text",
        },
        "removed": {"comitato_descrizione": "Drop"},
    }
    rows = (
        {"id_elemento": "same", "descrizione_originale_completa": "Same source text", "retirement_date": "2027-01-01 — Data di ritiro (Azure Advisor)\n2026-09-20 — Ultimo aggiornamento (Azure Advisor)", "link_fonti": "https://example.test/source"},
        {"id_elemento": "changed", "descrizione_originale_completa": "New source text", "retirement_date": "2027-02-01 — Data di ritiro (Azure Advisor)", "link_fonti": "https://example.test/changed"},
        {"id_elemento": "new", "descrizione_originale_completa": "New row", "retirement_date": "", "link_fonti": ""},
    )

    merged_rows, updated = committee.merge(old, rows)

    assert merged_rows[0]["comitato_descrizione"] == "Keep this wording"
    assert merged_rows[0]["comitato_retirement_date"] == "2027-01-15"
    assert merged_rows[1]["comitato_descrizione"] == ""
    assert merged_rows[1]["comitato_retirement_date"] == "2027-02-15"
    assert merged_rows[2]["comitato_descrizione"] == ""
    assert set(updated) == {"same", "changed", "new"}
    assert updated["same"]["retirement_date"] == ["2027-01-01 — Data di ritiro (Azure Advisor)"]
    assert updated["same"]["link_fonti"] == ["https://example.test/source"]


def test_missing_committee_file_loads_as_empty_and_write_round_trips(tmp_path: Path) -> None:
    assert committee is not None
    path = tmp_path / "committee.yaml"
    assert committee.load(path) == {}
    committee.write(path, {"item": {"comitato_descrizione": "Testo italiano"}})
    assert committee.load(path) == {"item": {"comitato_descrizione": "Testo italiano"}}
