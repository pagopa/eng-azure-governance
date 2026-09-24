from collections.abc import Callable, Mapping
from typing import Any

from ..acquisition.evidence import SourcePage
from ..acquisition.model import AcquisitionReceipt, SourceAcquisition
from ..acquisition.paging import ScriptedRequest, collect_complete_pages
from ..domain.execution import RunContext
from .arm_http import ArmHttpClient


def acquire_subscription_list(
    http: ArmHttpClient,
    context: RunContext,
    *,
    source: str,
    api_version: str,
    response_name: str,
    url_for: Callable[[str], str],
    params: Mapping[str, str],
    annotate: Callable[[dict[str, Any], str], dict[str, Any]],
) -> SourceAcquisition:
    requests: list[ScriptedRequest] = []
    response_context: list[dict[str, Any]] = []
    for subscription_id in context.scope.subscription_ids:
        pages = http.list_pages(
            url_for(subscription_id),
            params=dict(params),
            run_id=context.run_id,
        )
        requests.append(
            ScriptedRequest(
                subscription_id,
                tuple(
                    SourcePage(
                        subscription_id,
                        tuple(
                            annotate(_object(item, response_name), subscription_id)
                            for item in page.items
                        ),
                        page.continuation_url,
                    )
                    for page in pages
                ),
            )
        )
        response_context.extend(
            {
                "subscription_id": subscription_id,
                "page_number": page_number,
                "url": page.url,
                "continuation_url": page.continuation_url or "",
                "item_count": len(page.items),
            }
            for page_number, page in enumerate(pages, start=1)
        )
    collected = collect_complete_pages(
        requests,
        lambda item: str(item.get("id", "")),
    )
    return SourceAcquisition(
        receipt=AcquisitionReceipt(
            source=source,
            api_version=api_version,
            expected_subscriptions=collected.receipt.expected_subscriptions,
            completed_subscriptions=collected.receipt.completed_subscriptions,
            pages=collected.receipt.pages,
            source_records=collected.receipt.source_records,
            complete=collected.receipt.complete,
            continuation_tokens=collected.receipt.continuation_tokens,
            completeness_reason=(
                "complete_empty"
                if collected.receipt.complete and collected.receipt.source_records == 0
                else "complete"
                if collected.receipt.complete
                else "incomplete_subscriptions"
            ),
        ),
        records=collected.records,
        collection_context={
            "source": source,
            "api_version": api_version,
            "response_name": response_name,
            "subscription_ids": tuple(context.scope.subscription_ids),
            "query": dict(params),
        },
        response_context=tuple(response_context),
    )


def _object(item: Any, response_name: str) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError(f"{response_name} response item must be an object")
    return dict(item)
