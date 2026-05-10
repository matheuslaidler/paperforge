"""Parse Markdown content into typed slide blocks (paragraph/list/table/code/image/quote)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, Union

BlockKind = Literal["para", "list", "table", "code", "quote", "image"]


@dataclass
class Block:
    kind: BlockKind
    payload: Union[str, list[str]]


@dataclass
class Slide:
    title: str
    blocks: list[Block]


# --------------------------------------------------------------------------- #
#  Inline markdown                                                            #
# --------------------------------------------------------------------------- #
def parse_inline(text: str) -> list[tuple[str, bool]]:
    """Strip markdown decorations and return ``[(chunk, bold), ...]``."""
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)        # images
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)    # links -> label
    text = re.sub(r"`([^`]+)`", r"\1", text)                # inline code
    parts: list[tuple[str, bool]] = []
    last = 0
    for m in re.finditer(r"\*\*([^*]+)\*\*", text):
        if m.start() > last:
            parts.append((text[last:m.start()], False))
        parts.append((m.group(1), True))
        last = m.end()
    if last < len(text):
        parts.append((text[last:], False))
    return parts or [(text, False)]


def parse_table(lines: Iterable[str]) -> list[list[str]]:
    """Parse a Markdown table block into a list of rows (header first)."""
    rows: list[list[str]] = []
    for raw in lines:
        ln = raw.strip()
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            continue
        rows.append(cells)
    return rows


# --------------------------------------------------------------------------- #
#  Block parser                                                               #
# --------------------------------------------------------------------------- #
def parse_blocks(body: str) -> list[Block]:
    """Split a slide body into typed blocks (paragraph/list/table/code/quote/image)."""
    body = body.strip("\n")
    blocks: list[Block] = []
    buf_para: list[str] = []
    in_table = in_list = in_code = False

    def flush() -> None:
        nonlocal buf_para
        if buf_para:
            text = " ".join(s.strip() for s in buf_para).strip()
            if text:
                blocks.append(Block("para", text))
        buf_para = []

    for ln in body.splitlines():
        # ```code fences```
        if ln.strip().startswith("```"):
            if not in_code:
                flush()
                blocks.append(Block("code", []))
                in_code = True
            else:
                in_code = False
            continue
        if in_code and isinstance(blocks[-1].payload, list):
            blocks[-1].payload.append(ln)
            continue

        # horizontal rules — silently dropped
        if re.match(r"^\s*---+\s*$", ln) or re.match(r"^\s*\*\*\*+\s*$", ln):
            flush()
            in_list = in_table = False
            continue

        # image block
        m = re.match(r"\s*!\[([^\]]*)\]\(([^)]+)\)\s*$", ln)
        if m:
            flush()
            in_list = in_table = False
            blocks.append(Block("image", m.group(2)))
            continue

        # tables
        if ln.strip().startswith("|"):
            if not in_table:
                flush()
                blocks.append(Block("table", []))
                in_table = True
            assert isinstance(blocks[-1].payload, list)
            blocks[-1].payload.append(ln)
            in_list = False
            continue
        in_table = False

        # bullet lists
        if re.match(r"^\s*[-*]\s+", ln):
            if not in_list:
                flush()
                blocks.append(Block("list", []))
                in_list = True
            assert isinstance(blocks[-1].payload, list)
            blocks[-1].payload.append(re.sub(r"^\s*[-*]\s+", "", ln))
            continue
        in_list = False

        # blockquotes
        if ln.strip().startswith("> "):
            flush()
            blocks.append(Block("quote", ln.strip()[2:]))
            continue

        # paragraphs
        if ln.strip() == "":
            flush()
        else:
            buf_para.append(ln)
    flush()
    return blocks


# --------------------------------------------------------------------------- #
#  Document-level parser                                                      #
# --------------------------------------------------------------------------- #
SLIDE_HEADING_RE = re.compile(
    r"(?m)^##\s+(?:Slide\s+)?(\d+)(?:\s*[—\-:]\s*(.*?))?\s*$",
    re.IGNORECASE,
)


def parse_document(md_text: str) -> list[Slide]:
    """Split a Markdown document into Slides keyed by ``## Slide N`` headings.

    Accepts ``## Slide 1 — title``, ``## Slide 1: title`` or simply ``## 1 - title``.
    Returns an empty list if no slide headings are found.
    """
    matches = list(SLIDE_HEADING_RE.finditer(md_text))
    if not matches:
        return []

    slides: list[Slide] = []
    for idx, match in enumerate(matches):
        number = match.group(1)
        title_part = (match.group(2) or "").strip()
        title = f"Slide {number}" if not title_part else title_part
        body_start = match.end()
        body_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(md_text)
        body = md_text[body_start:body_end].strip("\n")
        blocks = parse_blocks(body)
        slides.append(Slide(title=title, blocks=blocks))
    return slides


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
def resolve_image_path(reference: str, base_dir: Path) -> Path | None:
    """Resolve a relative image reference against ``base_dir``; return None if missing.

    HTTP URLs are returned as-is when their ``~/.paperforge/cache/imgs`` cache
    file exists; otherwise None (URL fetching happens in builder.py).
    """
    if reference.startswith(("http://", "https://")):
        return None  # URL fetch handled by caller
    p = (base_dir / reference).resolve()
    return p if p.is_file() else None
