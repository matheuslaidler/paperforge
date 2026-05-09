"""Markdown -> HTML renderer with TOC/anchors that preserve accents."""

from __future__ import annotations

import markdown
from markdown.extensions.toc import slugify_unicode

DEFAULT_EXTENSIONS = [
    "tables",
    "fenced_code",
    "attr_list",
    "toc",
    "sane_lists",
    "smarty",
    "pymdownx.superfences",
    "pymdownx.tilde",
    "pymdownx.tasklist",
]


def render_markdown(md_text: str, extensions: list[str] | None = None) -> str:
    """Render Markdown to HTML body fragment.

    Critical: ``slugify_unicode`` is required to preserve accents in heading
    anchors so links like ``#3-introdução`` from the document's table of
    contents work in the final PDF. The default ASCII slugify breaks them.
    """
    return markdown.markdown(
        md_text,
        extensions=extensions or DEFAULT_EXTENSIONS,
        extension_configs={"toc": {"slugify": slugify_unicode}},
        output_format="html5",
    )


MATHJAX_HEAD = r"""
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$']],
    displayMath: [['$$', '$$']],
    processEscapes: true
  },
  options: { renderActions: { addMenu: [] } }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
"""

# KaTeX bundle would be loaded from local assets when --mathjax-engine=katex-local.
# For now we ship the CDN-based engine; KaTeX local is a future enhancement.
KATEX_HEAD_PLACEHOLDER = r"""
<!-- KaTeX local bundle would be embedded here for offline rendering. -->
"""


def wrap_html(
    body: str,
    *,
    title: str,
    css: str,
    lang: str = "en",
    mathjax: bool = True,
    mathjax_engine: str = "cdn",
) -> str:
    """Wrap a body fragment in a full HTML5 document with embedded CSS and head scripts."""
    head_scripts = ""
    if mathjax:
        head_scripts = MATHJAX_HEAD if mathjax_engine == "cdn" else KATEX_HEAD_PLACEHOLDER

    return (
        "<!DOCTYPE html>\n"
        f'<html lang="{lang}">\n<head>\n'
        '<meta charset="utf-8">\n'
        f"<title>{title}</title>\n"
        f"<style>{css}</style>\n"
        f"{head_scripts}\n"
        "</head>\n<body>\n"
        f"{body}\n"
        "</body>\n</html>\n"
    )
