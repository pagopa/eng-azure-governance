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