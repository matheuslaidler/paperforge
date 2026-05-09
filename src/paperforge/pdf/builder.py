"""High-level PDFBuilder — orchestrates Markdown -> HTML -> PDF."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from paperforge import i18n
from paperforge.browser import detect as detect_browser
from paperforge.pdf.post_processors import wrap_references_section
from paperforge.pdf.renderer import render_markdown, wrap_html
from paperforge.utils.logging import console, info, ok
from paperforge.utils.paths import asset

BUILTIN_STYLES = ("default", "minimal", "academic")


@dataclass
class PDFBuildOptions:
    style: str = "default"
    css_path: Optional[Path] = None
    orientation: str = "portrait"
    margins: tuple[str, str, str, str] = ("2cm", "1.8cm", "2cm", "1.8cm")  # T R B L
    mathjax: bool = True
    mathjax_engine: str = "cdn"
    mathjax_timeout: int = 8
    browser: Optional[Path] = None
    references_style: str = "abnt"
    keep_html: bool = False
    title: Optional[str] = None
    extra_browser_args: list[str] = field(default_factory=list)


@dataclass
class PDFBuildResult:
    path: Path
    size_kb: float
    pages: int


class PDFBuilder:
    """Encapsulates the PDF build pipeline."""

    def __init__(self, options: PDFBuildOptions | None = None) -> None:
        self.opts = options or PDFBuildOptions()

    # ------------------------------------------------------------------ #
    #  Public API                                                        #
    # ------------------------------------------------------------------ #
    def build(self, input_md: Path, output_pdf: Path) -> PDFBuildResult:
        input_md = Path(input_md).resolve()
        output_pdf = Path(output_pdf).resolve()

        if not input_md.is_file():
            raise FileNotFoundError(i18n.t("pdf.error.input_missing", path=str(input_md)))

        info(i18n.t("pdf.status.reading", path=str(input_md)))
        md_text = input_md.read_text(encoding="utf-8")

        info(i18n.t("pdf.status.converting"))
        html_body = render_markdown(md_text)
        if self.opts.references_style == "abnt":
            html_body = wrap_references_section(html_body)

        title = self.opts.title or self._derive_title(md_text, input_md)
        css = self._load_css()
        html_doc = wrap_html(
            html_body,
            title=title,
            css=css,
            mathjax=self.opts.mathjax,
            mathjax_engine=self.opts.mathjax_engine,
        )

        # Temp HTML lives alongside the input so relative image paths work.
        tmp_html = input_md.with_name(f"_{input_md.stem}_paperforge_tmp.html")
        tmp_html.write_text(html_doc, encoding="utf-8")

        info(
            i18n.t("pdf.status.rendering", timeout=self.opts.mathjax_timeout)
        )
        try:
            self._render_pdf(tmp_html, output_pdf)
        finally:
            if not self.opts.keep_html and tmp_html.is_file():
                tmp_html.unlink()
                info(i18n.t("pdf.status.cleanup"))

        if not output_pdf.is_file():
            raise RuntimeError(f"PDF was not created: {output_pdf}")

        size_kb = output_pdf.stat().st_size / 1024
        pages = self._count_pages(output_pdf)
        return PDFBuildResult(path=output_pdf, size_kb=size_kb, pages=pages)

    # ------------------------------------------------------------------ #
    #  Internals                                                         #
    # ------------------------------------------------------------------ #
    def _load_css(self) -> str:
        if self.opts.css_path:
            return self.opts.css_path.read_text(encoding="utf-8")

        if self.opts.style not in BUILTIN_STYLES:
            raise ValueError(
                i18n.t("pdf.error.style_unknown",
                       style=self.opts.style,
                       available=", ".join(BUILTIN_STYLES))
            )
        css_file = asset("pdf", "styles", f"{self.opts.style}.css")
        css = css_file.read_text(encoding="utf-8")

        # Apply orientation override if user specified landscape on a portrait CSS.
        if self.opts.orientation == "landscape":
            css = re.sub(
                r"size:\s*A4\s*portrait",
                "size: A4 landscape",
                css,
                flags=re.IGNORECASE,
            )

        # Replace margins if user customized them (T R B L tuple).
        t, r, b, l = self.opts.margins
        css = re.sub(
            r"margin:\s*[^;]+;",
            f"margin: {t} {r} {b} {l};",
            css,
            count=1,  # only the first @page rule
        )
        return css

    @staticmethod
    def _derive_title(md_text: str, input_path: Path) -> str:
        for line in md_text.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return input_path.stem.replace("_", " ").title()

    def _render_pdf(self, html_path: Path, pdf_path: Path) -> None:
        browser = detect_browser(self.opts.browser)
        # Edge/Chrome headless needs absolute paths and forward slashes.
        pdf_abs = pdf_path.resolve()
        pdf_abs.parent.mkdir(parents=True, exist_ok=True)
        # Wait for MathJax (in ms). KaTeX local would be synchronous (timeout=0).
        timeout_ms = (
            self.opts.mathjax_timeout * 1000
            if self.opts.mathjax and self.opts.mathjax_engine == "cdn"
            else 1000
        )
        cmd = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_abs}",
            f"--virtual-time-budget={timeout_ms}",
            *self.opts.extra_browser_args,
            html_path.absolute().as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        if result.returncode != 0:
            console.print(f"[error]Browser stderr:[/]\n{result.stderr}")
            raise RuntimeError(
                i18n.t("pdf.error.browser_failed", code=result.returncode)
            )
        # Some browsers ignore relative cwd; verify the absolute output exists
        # and copy back to the requested path if needed.
        if pdf_abs != pdf_path.resolve() and pdf_abs.is_file():
            import shutil
            shutil.copy2(pdf_abs, pdf_path)

    @staticmethod
    def _count_pages(pdf_path: Path) -> int:
        """Count PDF pages without external deps — parses /Type /Page entries."""
        try:
            data = pdf_path.read_bytes()
            return max(1, data.count(b"/Type /Page") - data.count(b"/Type /Pages"))
        except Exception:
            return 0
