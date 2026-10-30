from __future__ import annotations

import pytest

from src.comitato.comitato_azure_retirements_v2.retirements.contracts.committee import (
    merge,
)


def test_merge_preserves_committee_text_only_when_description_is_unchanged() -> None:
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
        {
            "id_elemento": "same",
            "descrizione_originale_completa": "Same source text",
            "retirement_date": "2027-01-01 — Data di ritiro (Azure Advisor)\n2026-09-20 — Ultimo aggiornamento (Azure Advisor)",
            "link_fonti": "https://example.test/source",
        },
        {
            "id_elemento": "changed",
            "descrizione_originale_completa": "New source text",
            "retirement_date": "2027-02-01 — Data di ritiro (Azure Advisor)",
            "link_fonti": "https://example.test/changed",
        },
        {
            "id_elemento": "new",
            "descrizione_originale_completa": "New row",
            "retirement_date": "",
            "link_fonti": "",
        },
    )

    merged_rows, updated = merge(old, rows)

    assert merged_rows[0]["comitato_descrizione"] == "Keep this wording"
    assert merged_rows[0]["comitato_retirement_date"] == "2027-01-15"
    assert merged_rows[1]["comitato_descrizione"] == ""
    assert merged_rows[1]["comitato_retirement_date"] == "2027-02-15"
    assert merged_rows[2]["comitato_descrizione"] == ""
    assert set(updated) == {"same", "changed", "new"}
    assert updated["same"]["retirement_date"] == [
        {
            "data": "2027-01-01",
            "tipo": "ritiro",
            "fonte": "Azure Advisor (raccomandazione)",
        },
        {
            "data": "2026-09-20",
            "tipo": "ultimo_aggiornamento",
            "fonte": "Azure Advisor",
        },
    ]
    assert updated["same"]["link_fonti"] == ["https://example.test/source"]


@pytest.mark.parametrize(
    ("old", "expected_description", "expected_sources"),
    [
        ({}, "", []),
        (
            {
                "comitato_descrizione": "Service: change. Suggerimento: migrate.",
                "descrizione_originale_completa": "Current source",
                "comitato_fonti": [
                    {"titolo": "Migration guide", "url": "https://example.test/guide"}
                ],
                "unrelated": "Do not retain unknown fields",
            },
            "Service: change. Suggerimento: migrate.",
            [{"titolo": "Migration guide", "url": "https://example.test/guide"}],
        ),
        (
            {
                "comitato_descrizione": "Stale wording",
                "descrizione_originale_completa": "Old source",
                "comitato_fonti": [
                    {"titolo": "Old guide", "url": "https://example.test/old"}
                ],
            },
            "",
            [],
        ),
        (
            {
                "comitato_descrizione": "Legacy wording without editorial sources",
                "descrizione_originale_completa": "Current source",
            },
            "Legacy wording without editorial sources",
            [],
        ),
    ],
    ids=["new-template", "unchanged-source", "changed-source", "legacy-entry"],
)
def test_merge_keeps_editorial_sources_with_current_description_only(
    old: dict[str, object],
    expected_description: str,
    expected_sources: list[dict[str, str]],
) -> None:
    row = {
        "id_elemento": "item",
        "descrizione_originale_completa": "Current source",
        "link_fonti": "https://example.test/original",
    }

    merged_rows, updated = merge({"item": old}, (row,))

    assert updated["item"]["comitato_descrizione"] == expected_description
    assert updated["item"]["comitato_fonti"] == expected_sources
    assert updated["item"]["link_fonti"] == ["https://example.test/original"]
    assert "unrelated" not in updated["item"]
    assert "comitato_fonti" not in dict(merged_rows[0].values)


def test_merge_maps_every_date_meaning_and_drops_portal_links() -> None:
    row = {
        "id_elemento": "item",
        "descrizione_originale_completa": "Text",
        "retirement_date": "\n".join(
            (
                "2026-03-31 — Data di ritiro (metadati Azure Advisor)",
                "2026-04-22 — Rimozione immagine (Azure Advisor)",
                "2026-04-01 — Aggiornamento meno recente osservato (Azure Advisor)",
                "2026-09-22 — Avviso pubblicato il",
                "2026-10-06 — Avviso attivo fino al",
                "2026-09-23 — Ultimo aggiornamento (Azure Service Health)",
            )
        ),
        "link_fonti": "; ".join(
            (
                "https://app.azure.com/h/DYDQ-ZLZ",
                "https://portal.azure.com/#view/x",
                "https://aka.ms/AzureServiceHealthAdvisories",
                "https://learn.microsoft.com/azure/x",
            )
        ),
    }

    _, updated = merge({}, (row,))

    assert updated["item"]["link_fonti"] == ["https://learn.microsoft.com/azure/x"]
    assert updated["item"]["retirement_date"] == [
        {"data": "2026-03-31", "tipo": "ritiro", "fonte": "Azure Advisor (metadati)"},
        {"data": "2026-04-22", "tipo": "rimozione_immagine", "fonte": "Azure Advisor"},
        {
            "data": "2026-04-01",
            "tipo": "aggiornamento_meno_recente",
            "fonte": "Azure Advisor",
        },
        {
            "data": "2026-09-22",
            "tipo": "avviso_inizio",
            "fonte": "Azure Service Health",
        },
        {"data": "2026-10-06", "tipo": "avviso_fine", "fonte": "Azure Service Health"},
        {
            "data": "2026-09-23",
            "tipo": "ultimo_aggiornamento",
            "fonte": "Azure Service Health",
        },
    ]
