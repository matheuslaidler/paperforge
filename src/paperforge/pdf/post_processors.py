"""HTML post-processors that run after Markdown -> HTML conversion."""

from __future__ import annotations

import re

# Matches the typical "References" heading in English and Portuguese.
REFERENCES_HEADING_RE = re.compile(
    r'(<h2[^>]*>\s*\d*\.?\s*'
    r'(refer[eê]ncias\s+bibliogr[aá]ficas|references|bibliography)'
    r'[^<]*</h2>)',
    re.IGNORECASE,
)


def wrap_references_section(html: str) -> str:
    """Wrap the references block in ``<div class="referencias">`` for ABNT styling.

    Triggers on the first heading whose text matches an English or Portuguese
    bibliography label. Everything from that heading to end-of-document is
    wrapped, so the CSS hanging-indent rule applies only to bibliographic
    entries.
    """
    match = REFERENCES_HEADING_RE.search(html)
    if not match:
        return html
    cut = match.end()
    return html[:cut] + '\n<div class="referencias">\n' + html[cut:] + '\n</div>\n'
