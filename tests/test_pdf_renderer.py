"""Renderer tests — markdown -> HTML, references wrapper, anchor accents."""

import re

from paperforge.pdf.post_processors import wrap_references_section
from paperforge.pdf.renderer import render_markdown


def test_render_markdown_preserves_accents_in_anchors() -> None:
    md = "## 1. Introdução\nbody"
    html = render_markdown(md)
    # The id must keep the accent (introdução), not strip it.
    m = re.search(r'<h2 id="([^"]+)"', html)
    assert m is not None
    assert "introdução" in m.group(1)


def test_render_markdown_table() -> None:
    md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
    html = render_markdown(md)
    assert "<table>" in html
    assert "<th>A</th>" in html
    assert "<td>2</td>" in html


def test_wrap_references_section_pt_br() -> None:
    html = (
        "<h2>1. Intro</h2><p>body</p>"
        "<h2>2. Referências bibliográficas (ABNT)</h2>"
        "<p>Author, A. Title.</p>"
    )
    out = wrap_references_section(html)
    assert '<div class="referencias">' in out
    assert out.count('<div class="referencias">') == 1


def test_wrap_references_section_english() -> None:
    html = (
        "<h2>Intro</h2><p>body</p>"
        "<h2>References</h2><p>cite</p>"
    )
    out = wrap_references_section(html)
    assert '<div class="referencias">' in out


def test_wrap_references_section_no_match() -> None:
    html = "<h2>Intro</h2><p>body</p>"
    assert wrap_references_section(html) == html
