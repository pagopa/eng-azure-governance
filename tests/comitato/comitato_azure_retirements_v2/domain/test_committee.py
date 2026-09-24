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
    assert updated["same"]["retirement_date"] == [
        {"data": "2027-01-01", "tipo": "ritiro", "fonte": "Azure Advisor (raccomandazione)"},
        {"data": "2026-09-20", "tipo": "ultimo_aggiornamento", "fonte": "Azure Advisor"},
    ]
    assert updated["same"]["link_fonti"] == ["https://example.test/source"]


def test_merge_maps_every_date_meaning_and_drops_portal_links() -> None:
    assert committee is not None
    row = {
        "id_elemento": "item",
        "descrizione_originale_completa": "Text",
        "retirement_date": "\n".join((
            "2026-03-31 — Data di ritiro (metadati Azure Advisor)",
            "2026-04-22 — Rimozione immagine (Azure Advisor)",
            "2026-04-01 — Aggiornamento meno recente osservato (Azure Advisor)",
            "2026-09-22 — Avviso pubblicato il",
            "2026-10-06 — Avviso attivo fino al",
            "2026-09-23 — Ultimo aggiornamento (Azure Service Health)",
        )),
        "link_fonti": "; ".join((
            "https://app.azure.com/h/DYDQ-ZLZ",
            "https://portal.azure.com/#view/x",
            "https://aka.ms/AzureServiceHealthAdvisories",
            "https://learn.microsoft.com/azure/x",
        )),
    }

    _, updated = committee.merge({}, (row,))

    assert updated["item"]["link_fonti"] == ["https://learn.microsoft.com/azure/x"]
    assert updated["item"]["retirement_date"] == [
        {"data": "2026-03-31", "tipo": "ritiro", "fonte": "Azure Advisor (metadati)"},
        {"data": "2026-04-22", "tipo": "rimozione_immagine", "fonte": "Azure Advisor"},
        {"data": "2026-04-01", "tipo": "aggiornamento_meno_recente", "fonte": "Azure Advisor"},
        {"data": "2026-09-22", "tipo": "avviso_inizio", "fonte": "Azure Service Health"},
        {"data": "2026-10-06", "tipo": "avviso_fine", "fonte": "Azure Service Health"},
        {"data": "2026-09-23", "tipo": "ultimo_aggiornamento", "fonte": "Azure Service Health"},
    ]


def test_write_wraps_long_descriptions_and_round_trips_exactly(tmp_path: Path) -> None:
    assert committee is not None
    original = "Advisor: " + " ".join(["word"] * 60) + "\n\nSecond paragraph with  double  spaces and ’quotes’."
    note = "Nota del comitato " + "molto lunga " * 20
    path = tmp_path / "data" / "committee.yaml"

    committee.write(path, {"item": {"comitato_descrizione": note, "descrizione_originale_completa": original, "link_fonti": []}})

    lines = path.read_text(encoding="utf-8").splitlines()
    assert max(len(line) for line in lines) <= 110
    assert committee.load(path) == {"item": {"comitato_descrizione": note, "descrizione_originale_completa": original, "link_fonti": []}}


def test_missing_committee_file_loads_as_empty_and_write_round_trips(tmp_path: Path) -> None:
    assert committee is not None
    path = tmp_path / "committee.yaml"
    assert committee.load(path) == {}
    committee.write(path, {"item": {"comitato_descrizione": "Testo italiano"}})
    assert committee.load(path) == {"item": {"comitato_descrizione": "Testo italiano"}}
