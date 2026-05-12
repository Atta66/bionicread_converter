from __future__ import annotations

from io import BytesIO
from typing import Iterable

from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT

from bionic_app.bionic_text import bionify_text_to_html, flatten_text_blocks
from bionic_app.converters.epub_converter import _bionify_soup_text_nodes


def _wrap_html(body_html: str, title: str) -> str:
    return (
        "<!doctype html>"
        "<html lang=\"en\">"
        "<head>"
        "<meta charset=\"utf-8\" />"
        f"<title>{title}</title>"
        "<style>body{font-family:serif;line-height:1.5;}strong{font-weight:700;}</style>"
        "</head>"
        f"<body>{body_html}</body>"
        "</html>"
    )


def convert_pdf_text_to_html(text_by_page: Iterable[str], ratio: float = 0.5, title: str = "Bionic PDF Export") -> bytes:
    page_sections: list[str] = []

    for index, page_text in enumerate(text_by_page, start=1):
        text = flatten_text_blocks([page_text])
        bionic_html = bionify_text_to_html(text, ratio=ratio)
        page_sections.append(f"<section><h2>Page {index}</h2><p>{bionic_html}</p></section>")

    body = "".join(page_sections)
    return _wrap_html(body, title=title).encode("utf-8")


def convert_epub_to_html(input_bytes: bytes, ratio: float = 0.5, title: str = "Bionic EPUB Export") -> bytes:
    book = epub.read_epub(BytesIO(input_bytes))
    sections: list[str] = []

    for item in book.get_items():
        if item.get_type() != ITEM_DOCUMENT:
            continue

        soup = BeautifulSoup(item.get_content(), "lxml")
        _bionify_soup_text_nodes(soup, ratio=ratio)
        body_html = soup.body.decode_contents() if soup.body else str(soup)
        sections.append(f"<section>{body_html}</section>")

    body = "".join(sections)
    return _wrap_html(body, title=title).encode("utf-8")
