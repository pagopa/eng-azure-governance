import csv
import json
import re
from pathlib import Path

from src.comitato.comitato_azure_retirements_v2.retirements.adapters.filesystem.committee_yaml import (
    load,
    write,
)


def test_write_wraps_long_descriptions_and_round_trips_exactly(tmp_path: Path) -> None:
    original = (
        "Advisor: "
        + " ".join(["word"] * 60)
        + "\n\nSecond paragraph with  double  spaces and ’quotes’."
    )
    note = "Nota del comitato " + "molto lunga " * 20
    path = tmp_path / "data" / "committee.yaml"

    write(
        path,
        {
            "item": {
                "comitato_descrizione": note,
                "descrizione_originale_completa": original,
                "link_fonti": [],
            }
        },
    )

    lines = path.read_text(encoding="utf-8").splitlines()
    assert max(len(line) for line in lines) <= 110
    assert load(path) == {
        "item": {
            "comitato_descrizione": note,
            "descrizione_originale_completa": original,
            "link_fonti": [],
        }
    }


def test_missing_committee_file_loads_as_empty_and_write_round_trips(
    tmp_path: Path,
) -> None:
    path = tmp_path / "committee.yaml"
    assert load(path) == {}
    write(path, {"item": {"comitato_descrizione": "Testo italiano"}})
    assert load(path) == {"item": {"comitato_descrizione": "Testo italiano"}}


def test_write_creates_a_tsv_version_of_the_full_document(tmp_path: Path) -> None:
    path = tmp_path / "comitato_editoriale.yaml"
    document = {
        "item-2": {
            "comitato_descrizione": "Azure Service - SDK 1: ritiro\n\nSuggerimento: migrare.",
            "comitato_fonti": [
                {"titolo": "Guida", "url": "https://example.test/guide"}
            ],
            "comitato_retirement_date": "",
            "retirement_date": [
                {
                    "data": "2027-01-15",
                    "tipo": "ritiro",
                    "fonte": "Azure Advisor",
                }
            ],
        },
        "item-1": {
            "comitato_descrizione": "",
            "link_fonti": ["https://example.test/source"],
        },
    }

    write(path, document)

    tsv_path = path.with_suffix(".tsv")
    with tsv_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    assert [row["id_elemento"] for row in rows] == ["item-1", "item-2"]
    assert rows[0]["comitato_descrizione"] == ""
    assert rows[0]["comitato_fonti"] == ""
    assert rows[1]["comitato_descrizione"] == (
        "Azure Service - SDK 1: ritiro  Suggerimento: migrare."
    )
    assert json.loads(rows[1]["comitato_fonti"]) == document["item-2"][
        "comitato_fonti"
    ]
    assert json.loads(rows[1]["retirement_date"]) == document["item-2"][
        "retirement_date"
    ]


def test_editorial_inventory_separates_plain_text_from_reference_metadata() -> None:
    path = (
        Path(__file__).resolve().parents[4]
        / "src/comitato/comitato_azure_retirements_v2/data/comitato_editoriale.yaml"
    )
    entries = load(path)

    assert entries
    for item_id, entry in entries.items():
        assert "comitato_retirement_date" in entry, item_id
        description = entry["comitato_descrizione"]
        assert "**" not in description, item_id
        assert not re.search(r"\[[^\]]+\]\([^)]+\)|https?://", description), item_id
        assert "Suggerimento:" in description, item_id
        assert isinstance(entry["comitato_fonti"], list), item_id
        assert entry["comitato_fonti"], item_id
        for source in entry["comitato_fonti"]:
            assert set(source) == {"titolo", "url"}, item_id
            assert isinstance(source["titolo"], str) and source["titolo"].strip(), (
                item_id
            )
            assert isinstance(source["url"], str) and source["url"].startswith(
                "https://"
            ), item_id

    tsv_path = path.with_suffix(".tsv")
    assert tsv_path.is_file()
    with tsv_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    assert [row["id_elemento"] for row in rows] == sorted(entries)
    assert all(row["comitato_retirement_date"] is not None for row in rows)
