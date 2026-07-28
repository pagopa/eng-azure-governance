from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.service_health_text import (
    html_to_ascii_text,
)


def test_html_to_ascii_text_preserves_structure_entities_and_links() -> None:
    source = (
        "<p>We\u2019ll retire Caf\u00e9.</p>"
        "<ul><li>Read <a href=\"https://example.com/a?x=1&amp;y=2\">the guide</a>.</li></ul>"
    )

    result = html_to_ascii_text(source)

    assert result == "We'll retire Cafe. Read the guide (https://example.com/a?x=1&y=2)."
    assert result.isascii()


def test_html_to_ascii_text_keeps_plain_url_and_removes_tags() -> None:
    result = html_to_ascii_text("<p>Use https://example.com/plain</p>")
    assert result == "Use https://example.com/plain"
    assert "<p>" not in result

def test_html_to_ascii_text_normalizes_literal_angle_characters() -> None:
    result = html_to_ascii_text("<p>Use keySize &lt; 1024 and x &gt; 0.</p>")
    assert result == "Use keySize less than 1024 and x greater than 0."
