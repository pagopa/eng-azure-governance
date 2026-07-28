from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from src.comitato.comitato_azure_retirements.libs.workflow_exports import (
    build_aggregate_rows,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures/workbook_impacted_services_2026-07-28.csv"


def test_approved_workbook_keys_and_resource_counts_reconcile() -> None:
    with FIXTURE_PATH.open(newline="", encoding="utf-8") as fixture_file:
        workbook_rows = list(csv.DictReader(fixture_file))

    advisor_rows: list[dict[str, str]] = []
    for workbook_row in workbook_rows:
        resource_count = int(workbook_row["# Resources"])
        for resource_index in range(resource_count):
            source_id = (
                f"/subscriptions/sub-1/resourceGroups/rg-test/providers/"
                f"Microsoft.Test/{resource_index}/{workbook_row['Retiring Feature']}"
            )
            advisor_rows.append(
                {
                    "service_name": workbook_row["Service Name"],
                    "retiring_feature": workbook_row["Retiring Feature"],
                    "short_description_problem": workbook_row["Retiring Feature"],
                    "short_description_solution": workbook_row["Actions"],
                    "retirement_date": workbook_row["Retirement Date"],
                    "subscription_name": "PROD-IO",
                    "source_system": "advisor_joined",
                    "source_id": source_id,
                    "advisor_recommendation_id": source_id,
                    "platform_state": "New",
                    "as_of_date": "2026-07-28",
                }
            )

    aggregate_result = build_aggregate_rows(
        advisor_rows=advisor_rows,
        service_rows=[],
        active_platform_map={"prod-io": "IO"},
        as_of_date=date(2026, 7, 28),
    )
    aggregate_rows = aggregate_result.advisor_rows

    workbook_keys = {
        (
            row["Service Name"],
            row["Retiring Feature"],
            row["Retirement Date"],
        ): int(row["# Resources"])
        for row in workbook_rows
    }
    aggregate_keys = {
        (
            row["technology_or_service"],
            row["retiring_feature"],
            row["retirement_date"],
        ): len(set(row["source_identifiers"].split(", ")))
        for row in aggregate_rows
    }

    assert aggregate_keys.keys() == workbook_keys.keys()
    assert aggregate_keys == workbook_keys
    assert "9HB8-C00" not in " ".join(
        row["source_identifiers"] for row in aggregate_rows
    )
    assert all(
        date(2026, 7, 28)
        <= date.fromisoformat(row["retirement_date"])
        <= date(2027, 7, 28)
        for row in aggregate_rows
    )
