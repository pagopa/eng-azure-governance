"""Link classification shared by the aggregate and the committee YAML."""

from __future__ import annotations

import re
from urllib.parse import urlsplit


_PORTAL_HOSTS = frozenset({"app.azure.com", "portal.azure.com"})
_PORTAL_REDIRECTS = frozenset({"aka.ms/azureservicehealthadvisories"})
_URL = re.compile(r"https?://[^\s()<>\"']+")


def is_azure_portal_link(url: str) -> bool:
    parts = urlsplit(url.strip())
    host = parts.netloc.casefold()
    return host in _PORTAL_HOSTS or f"{host}{parts.path.rstrip('/')}".casefold() in _PORTAL_REDIRECTS


def text_links(text: str) -> tuple[str, ...]:
    return tuple(sorted({match.rstrip(".,;:") for match in _URL.findall(text or "")}))


__all__ = ["is_azure_portal_link", "text_links"]
