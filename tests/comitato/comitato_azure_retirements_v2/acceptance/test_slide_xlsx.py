import copy
import csv
import io
from dataclasses import replace
from datetime import date
from pathlib import Path

import yaml

import src.comitato.comitato_azure_retirements_v2.src.paths as runtime_paths
from src.comitato.comitato_azure_retirements_v2.src.domain.execution import (
    ReportSelector,
)
from tests.comitato.comitato_azure_retirements_v2.acceptance.harness import (
    load_scenario,
    read_workbook_cell_types,
    read_workbook_rows,
    run_scenario,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"
SLIDE_PATH = "03_azure_retirements_slide.xlsx"
EXPECTED_DATA_FILES = {
    "01_azure_advisor_retirements_raw.tsv",
    "01_azure_service_health_advisories_raw.tsv",
    "02_azure_retirements_aggregate.tsv",
    SLIDE_PATH,
}


def _tsv_flattened(
    rows: tuple[tuple[str, ...], ...],
) -> tuple[tuple[str, ...], ...]:
    return tuple(
        tuple(
            value.replace("\t", " ").replace("\r", " ").replace("\n", " ")
            for value in row
        )
        for row in rows
    )


def _fixture_slide_rows(fixture: Path) -> tuple[tuple[str, ...], ...]:
    content = fixture / "expected" / "current" / "03_azure_retirements_slide.tsv"
    return tuple(
        tuple(row)
        for row in csv.reader(
            io.StringIO(content.read_text(encoding="utf-8")), delimiter="\t"
        )
    )


def _support_files(destination: Path, as_of_date: date = date(2026, 7, 30)) -> set[str]:
    support = (
        destination.with_name(f"{destination.name}-support")
        / f"{as_of_date.year:04d}"
        / f"{as_of_date.month:02d}"
    )
    return {
        path.relative_to(support).as_posix()
        for path in support.rglob("*")
        if path.is_file()
    }


def test_all_publication_emits_exact_xlsx_and_tsv_bundle(tmp_path: Path) -> None:
    fixture = FIXTURES / "s01_explicitly_correlated"

    result = run_scenario(load_scenario(fixture), tmp_path)

    assert result.exit_status == 0
    assert set(result.current_tree) == EXPECTED_DATA_FILES
    assert _support_files(tmp_path) == {
        "01_azure_advisor_retirements_raw.jsonl",
        "01_azure_service_health_advisories_raw.jsonl",
        "publication-manifest.json",
        "saved-acquisition-inputs.json",
    }
    assert _tsv_flattened(
        read_workbook_rows(result.current_tree[SLIDE_PATH])
    ) == _fixture_slide_rows(fixture)
    assert (
        result.current_tree["01_azure_advisor_retirements_raw.tsv"]
        == (
            fixture / "expected" / "current" / "01_azure_advisor_retirements_raw.tsv"
        ).read_bytes()
    )
    assert (
        result.current_tree["01_azure_service_health_advisories_raw.tsv"]
        == (
            fixture
            / "expected"
            / "current"
            / "01_azure_service_health_advisories_raw.tsv"
        ).read_bytes()
    )
    assert (
        result.current_tree["02_azure_retirements_aggregate.tsv"]
        == (
            fixture / "expected" / "current" / "02_azure_retirements_aggregate.tsv"
        ).read_bytes()
    )


def test_slide_workbook_preserves_literal_text_as_text(tmp_path: Path) -> None:
    scenario = load_scenario(FIXTURES / "s01_explicitly_correlated")
    pages = copy.deepcopy(scenario.advisor_pages)
    pages[0]["items"][0]["properties"]["serviceName"] = "00123 – Servizio"
    pages[0]["items"][0]["properties"]["shortDescription"]["problem"] = "=1+1"

    result = run_scenario(replace(scenario, advisor_pages=tuple(pages)), tmp_path)

    assert result.exit_status == 0
    rows = read_workbook_rows(result.current_tree[SLIDE_PATH])
    assert rows[1][1] == "00123 – Servizio"
    assert rows[1][2] == "=1+1"
    assert read_workbook_cell_types(result.current_tree[SLIDE_PATH])[1][2] == "s"
    assert rows[1][8] == ""


def test_empty_slide_publication_emits_header_only_workbook(tmp_path: Path) -> None:
    fixture = FIXTURES / "s06_complete_empty"

    result = run_scenario(load_scenario(fixture), tmp_path)

    assert result.exit_status == 0
    rows = read_workbook_rows(result.current_tree[SLIDE_PATH])
    assert rows == _fixture_slide_rows(fixture)


def test_slide_publication_rejects_values_that_excel_would_truncate(
    tmp_path: Path,
) -> None:
    scenario = load_scenario(FIXTURES / "s01_explicitly_correlated")
    item_id = (
        "azure-retirement:v2:"
        "1cce18c669c4cd0b03ad9f7480b3dff528415386056ba269ab0646a6857ac1cc"
    )
    committee_path = tmp_path / "committee.yaml"
    committee_path.write_text(
        yaml.safe_dump(
            {
                item_id: {
                    "comitato_descrizione": "x" * 32_767,
                    "descrizione_originale_completa": (
                        "Advisor: Advisor evidence\n\nS01 problem"
                    ),
                }
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    boundary = run_scenario(
        scenario,
        tmp_path / "a",
        committee_yaml_path=committee_path,
    )

    assert boundary.exit_status == 0
    assert len(read_workbook_rows(boundary.current_tree[SLIDE_PATH])[1][6]) == 32_767

    document = yaml.safe_load(committee_path.read_text(encoding="utf-8"))
    document[item_id]["comitato_descrizione"] += "x"
    committee_path.write_text(yaml.safe_dump(document), encoding="utf-8")
    rejected = run_scenario(
        scenario,
        tmp_path / "b",
        committee_yaml_path=committee_path,
    )

    assert rejected.exit_status == 1
    assert rejected.current_tree == {}
    assert b"Excel text limit" in rejected.stderr_jsonl


def test_november_2026_all_publication_has_exact_clean_destinations(
    tmp_path: Path,
    monkeypatch,
) -> None:
    november = date(2026, 11, 1)
    scenario = replace(
        load_scenario(FIXTURES / "s01_explicitly_correlated"),
        as_of_date=november,
        run_id="november-2026",
    )

    monkeypatch.setattr(
        runtime_paths,
        "COMPONENT_TMP_ROOT",
        tmp_path / "repository-tmp" / "comitato_azure_retirements_v2",
    )
    output_root = tmp_path / "src" / "comitato_azure_retirements_v2" / "exports"
    monkeypatch.setattr(runtime_paths, "DEFAULT_OUTPUT_ROOT", output_root)
    support_root = runtime_paths.publication_support_root(output_root)
    result = run_scenario(scenario, output_root, support_destination=support_root)

    assert result.exit_status == 0
    assert set(result.current_tree) == EXPECTED_DATA_FILES
    support_month = support_root / "2026" / "11"
    assert {
        path.relative_to(support_month).as_posix()
        for path in support_month.rglob("*")
        if path.is_file()
    } == {
        "01_azure_advisor_retirements_raw.jsonl",
        "01_azure_service_health_advisories_raw.jsonl",
        "publication-manifest.json",
        "saved-acquisition-inputs.json",
    }
    assert "repository-tmp" in str(support_month)
    assert support_root.name == "default"
    assert not list(output_root.rglob("*.json"))
    assert not list(output_root.rglob("*.jsonl"))


def test_slide_selector_emits_only_xlsx_and_data_selectors_never_emit_xlsx(
    tmp_path: Path,
) -> None:
    scenario = load_scenario(FIXTURES / "s01_explicitly_correlated")
    expected_exports = {
        ReportSelector.ADVISOR: "01_azure_advisor_retirements_raw.tsv",
        ReportSelector.SERVICE_HEALTH: ("01_azure_service_health_advisories_raw.tsv"),
        ReportSelector.AGGREGATE: "02_azure_retirements_aggregate.tsv",
        ReportSelector.SLIDES: SLIDE_PATH,
    }

    for selector, expected in expected_exports.items():
        result = run_scenario(
            replace(scenario, selector=selector, run_id=f"selector-{selector.value}"),
            tmp_path / selector.value,
        )
        assert result.exit_status == 0
        assert set(result.current_tree) == {expected}
