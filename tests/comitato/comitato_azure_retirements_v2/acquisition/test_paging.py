from __future__ import annotations

import pytest

from src.comitato.comitato_azure_retirements_v2.acquisition.paging import (
    AcquisitionIntegrityError,
    ScriptedRequest,
    SourcePage,
    collect_complete_pages,
)


def test_collect_complete_pages_traverses_pages_and_collapses_exact_duplicates() -> None:
    requests = (
        ScriptedRequest(
            subscription_id="sub-b",
            pages=(
                SourcePage(
                    subscription_id="sub-b",
                    items=({"id": "b-2", "value": 2},),
                    continuation_token="next-b",
                ),
                SourcePage(
                    subscription_id="sub-b",
                    items=({"id": "b-1", "value": 1},),
                ),
            ),
        ),
        ScriptedRequest(
            subscription_id="sub-a",
            pages=(
                SourcePage(
                    subscription_id="sub-a",
                    items=(
                        {"id": "a-1", "value": 1},
                        {"id": "a-1", "value": 1},
                    ),
                ),
            ),
        ),
    )

    acquisition = collect_complete_pages(requests, lambda item: item["id"])

    assert acquisition.receipt.complete is True
    assert acquisition.receipt.expected_subscriptions == 2
    assert acquisition.receipt.completed_subscriptions == 2
    assert acquisition.receipt.pages == 3
    assert [record.identity for record in acquisition.records] == [
        "a-1",
        "b-1",
        "b-2",
    ]


def test_collect_complete_pages_rejects_a_repeated_continuation_token() -> None:
    request = ScriptedRequest(
        subscription_id="sub-a",
        pages=(
            SourcePage(subscription_id="sub-a", items=(), continuation_token="same"),
            SourcePage(subscription_id="sub-a", items=(), continuation_token="same"),
        ),
    )

    with pytest.raises(AcquisitionIntegrityError, match="repeated continuation token"):
        collect_complete_pages((request,), lambda item: item["id"])


def test_collect_complete_pages_rejects_conflicting_payloads_for_one_identity() -> None:
    request = ScriptedRequest(
        subscription_id="sub-a",
        pages=(
            SourcePage(
                subscription_id="sub-a",
                items=({"id": "same", "value": 1},),
            ),
            SourcePage(
                subscription_id="sub-a",
                items=({"id": "same", "value": 2},),
            ),
        ),
    )

    with pytest.raises(AcquisitionIntegrityError, match="conflicting payload"):
        collect_complete_pages((request,), lambda item: item["id"])
