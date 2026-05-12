from __future__ import annotations

from io import BytesIO
from typing import Literal

from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT

from bionic_app.bionic_text import flatten_text_blocks
from bionic_app.converters.epub_converter import convert_epub_to_epub, convert_pdf_text_to_epub
from bionic_app.converters.html_converter import convert_epub_to_html, convert_pdf_text_to_html
from bionic_app.converters.azw3_converter import convert_epub_bytes_to_azw3, convert_epub_bytes_with_calibre
from bionic_app.converters.pdf_converter import (
    convert_epub_text_to_pdf,
    convert_pdf_to_pdf,
    extract_pdf_page_texts,
)

SupportedFormat = Literal["pdf", "epub", "html", "azw3"]


def convert_document(
    input_bytes: bytes,
    input_format: SupportedFormat,
    output_format: SupportedFormat,
    ratio: float = 0.5,
    keep_page_size: bool = True,
    use_calibre_epub: bool = False,
) -> bytes:
    if input_format == "pdf" and output_format == "pdf":
        return convert_pdf_to_pdf(input_bytes, ratio=ratio, keep_page_size=keep_page_size)

    if input_format == "epub" and output_format == "epub":
        epub_bytes = convert_epub_to_epub(input_bytes, ratio=ratio)
        if use_calibre_epub:
            return convert_epub_bytes_with_calibre(epub_bytes, title="Bionic Converted EPUB")
        return epub_bytes

    if input_format == "pdf" and output_format == "epub":
        page_texts = extract_pdf_page_texts(input_bytes)
        epub_bytes = convert_pdf_text_to_epub(page_texts, ratio=ratio, title="Bionic Converted PDF")
        if use_calibre_epub:
            return convert_epub_bytes_with_calibre(epub_bytes, title="Bionic Converted PDF")
        return epub_bytes

    if input_format == "pdf" and output_format == "html":
        page_texts = extract_pdf_page_texts(input_bytes)
        return convert_pdf_text_to_html(page_texts, ratio=ratio, title="Bionic Converted PDF")

    if input_format == "pdf" and output_format == "azw3":
        page_texts = extract_pdf_page_texts(input_bytes)
        epub_bytes = convert_pdf_text_to_epub(page_texts, ratio=ratio, title="Bionic Converted PDF")
        return convert_epub_bytes_to_azw3(epub_bytes, title="Bionic Converted PDF")

    if input_format == "epub" and output_format == "pdf":
        full_text = _extract_epub_text(input_bytes)
        return convert_epub_text_to_pdf(full_text, ratio=ratio, keep_page_size=keep_page_size)

    if input_format == "epub" and output_format == "html":
        return convert_epub_to_html(input_bytes, ratio=ratio, title="Bionic Converted EPUB")

    if input_format == "epub" and output_format == "azw3":
        epub_bytes = convert_epub_to_epub(input_bytes, ratio=ratio)
        return convert_epub_bytes_to_azw3(epub_bytes, title="Bionic Converted EPUB")

    raise ValueError(f"Unsupported conversion: {input_format} -> {output_format}")


def _extract_epub_text(input_bytes: bytes) -> str:
    book = epub.read_epub(BytesIO(input_bytes))
    sections: list[str] = []

    for item in book.get_items():
        if item.get_type() != ITEM_DOCUMENT:
            continue

        soup = BeautifulSoup(item.get_content(), "lxml")
        section_text = soup.get_text("\n", strip=True)
        if section_text:
            sections.append(section_text)

    return flatten_text_blocks(sections)
