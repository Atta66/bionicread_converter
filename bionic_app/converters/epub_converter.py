from __future__ import annotations

from io import BytesIO
from typing import Iterable

from bs4 import BeautifulSoup, NavigableString
from ebooklib import epub, ITEM_DOCUMENT, ITEM_NAVIGATION

from bionic_app.bionic_text import bionify_text_to_html, flatten_text_blocks


def _default_epub_css() -> bytes:
    return b"body{font-family:serif;line-height:1.5;}strong{font-weight:700;}"


def _wrap_xhtml(body_html: str, css_path: str) -> bytes:
    xhtml = (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        "<!DOCTYPE html>"
        "<html xmlns=\"http://www.w3.org/1999/xhtml\">"
        "<head>"
        f"<link rel=\"stylesheet\" type=\"text/css\" href=\"{css_path}\" />"
        "</head>"
        f"<body>{body_html}</body>"
        "</html>"
    )
    return xhtml.encode("utf-8")


def _bionify_soup_text_nodes(soup: BeautifulSoup, ratio: float = 0.5) -> None:
    excluded_tags = {"script", "style", "code", "pre", "svg", "math"}

    for text_node in list(soup.find_all(string=True)):
        parent = text_node.parent
        if not isinstance(text_node, NavigableString) or parent is None:
            continue

        if parent.name and parent.name.lower() in excluded_tags:
            continue

        original = str(text_node)
        if not original.strip():
            continue

        transformed_html = bionify_text_to_html(original, ratio=ratio)
        fragment = BeautifulSoup(transformed_html, "lxml")
        for new_node in list(fragment.body.children if fragment.body else fragment.contents):
            text_node.insert_before(new_node)
        text_node.extract()


def convert_epub_to_epub(input_bytes: bytes, ratio: float = 0.5) -> bytes:
    src = epub.read_epub(BytesIO(input_bytes))
    dst = epub.EpubBook()

    dst.set_identifier(src.get_metadata("DC", "identifier")[0][0] if src.get_metadata("DC", "identifier") else "bionic-book")
    dst.set_title(src.get_metadata("DC", "title")[0][0] if src.get_metadata("DC", "title") else "Bionic Reading Output")
    dst.set_language(src.get_metadata("DC", "language")[0][0] if src.get_metadata("DC", "language") else "en")

    style_item = epub.EpubItem(
        uid="style",
        file_name="style/style.css",
        media_type="text/css",
        content=_default_epub_css(),
    )
    dst.add_item(style_item)

    for creator in src.get_metadata("DC", "creator"):
        dst.add_author(creator[0])

    items_for_spine: list[epub.EpubHtml] = []

    for item in src.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            content_bytes = item.get_content() or b""
            if not content_bytes.strip():
                content_bytes = b"<p></p>"

            soup = BeautifulSoup(content_bytes, "lxml")
            _bionify_soup_text_nodes(soup, ratio=ratio)

            body_html = soup.body.decode_contents() if soup.body else str(soup)
            if not body_html.strip():
                body_html = "<p></p>"
            content = _wrap_xhtml(body_html, css_path="style/style.css")
            chapter = epub.EpubHtml(
                uid=item.get_id(),
                file_name=item.file_name,
                title=item.get_name(),
                content=content,
            )
            chapter.add_item(style_item)
            dst.add_item(chapter)
            items_for_spine.append(chapter)
        else:
            is_ncx = (
                item.file_name.lower().endswith("toc.ncx")
                or item.get_id().lower() == "ncx"
                or item.media_type == "application/x-dtbncx+xml"
            )
            if item.get_type() == ITEM_NAVIGATION or is_ncx:
                continue
            dst.add_item(item)

    dst.toc = tuple(items_for_spine)
    dst.spine = items_for_spine
    dst.add_item(epub.EpubNcx())

    output = BytesIO()
    epub.write_epub(output, dst, {"epub3": False})
    return output.getvalue()


def convert_pdf_text_to_epub(text_by_page: Iterable[str], ratio: float = 0.5, title: str = "Bionic PDF Export") -> bytes:
    book = epub.EpubBook()
    book.set_identifier("pdf-to-epub-bionic")
    book.set_title(title)
    book.set_language("en")

    style_item = epub.EpubItem(
        uid="style",
        file_name="style/style.css",
        media_type="text/css",
        content=_default_epub_css(),
    )
    book.add_item(style_item)

    chapters: list[epub.EpubHtml] = []

    for index, page_text in enumerate(text_by_page, start=1):
        text = flatten_text_blocks([page_text])
        bionic_html = bionify_text_to_html(text, ratio=ratio)
        chapter = epub.EpubHtml(title=f"Page {index}", file_name=f"page_{index}.xhtml", lang="en")
        body_html = f"<h2>Page {index}</h2><p>{bionic_html}</p>"
        chapter.content = _wrap_xhtml(body_html, css_path="style/style.css")
        chapter.add_item(style_item)
        book.add_item(chapter)
        chapters.append(chapter)

    book.toc = tuple(chapters)
    book.spine = chapters
    book.add_item(epub.EpubNcx())

    output = BytesIO()
    epub.write_epub(output, book, {"epub3": False})
    return output.getvalue()
