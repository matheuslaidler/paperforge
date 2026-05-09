"""Parser tests for ``slides.parser``."""

from paperforge.slides.parser import (
    parse_blocks,
    parse_document,
    parse_inline,
    parse_table,
)


def test_parse_inline_bold_and_links() -> None:
    chunks = parse_inline("see **this** [link](http://x)")
    text = "".join(c[0] for c in chunks)
    bolds = [c[1] for c in chunks]
    assert "this" in text
    assert "link" in text  # the label survives
    assert any(bolds)


def test_parse_table_minimal() -> None:
    rows = parse_table([
        "| A | B |",
        "|---|---|",
        "| 1 | 2 |",
        "| 3 | 4 |",
    ])
    assert rows == [["A", "B"], ["1", "2"], ["3", "4"]]


def test_parse_blocks_classifies_each_kind() -> None:
    blocks = parse_blocks(
        "para line\n\n"
        "- item 1\n- item 2\n\n"
        "| A | B |\n|---|---|\n| 1 | 2 |\n\n"
        "```\ncode line\n```\n\n"
        "> a quote\n\n"
        "![alt](image.png)"
    )
    kinds = [b.kind for b in blocks]
    assert "para" in kinds
    assert "list" in kinds
    assert "table" in kinds
    assert "code" in kinds
    assert "quote" in kinds
    assert "image" in kinds


def test_parse_document_finds_slides() -> None:
    md = (
        "## Slide 1 — Intro\n\nfirst body\n\n"
        "## Slide 2 — Methods\n\nsecond body\n"
    )
    slides = parse_document(md)
    assert len(slides) == 2
    assert slides[0].title == "Intro"
    assert slides[1].title == "Methods"


def test_parse_document_no_slides_returns_empty() -> None:
    assert parse_document("# A document\n\nNo slide headings.") == []
