"""Task-local identity for concurrent Azure downloads."""

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar

_DOWNLOAD_CONTEXT: ContextVar[Mapping[str, object]] = ContextVar(
    "azure_download_context", default={}
)


def download_context() -> Mapping[str, object]:
    return _DOWNLOAD_CONTEXT.get()


def source_label(source: str) -> str:
    return {"advisor": "Advisor", "service-health": "Service Health"}.get(
        source, "Azure"
    )


@contextmanager
def download_scope(**values: object) -> Iterator[None]:
    token = _DOWNLOAD_CONTEXT.set({**download_context(), **values})
    try:
        yield
    finally:
        _DOWNLOAD_CONTEXT.reset(token)
