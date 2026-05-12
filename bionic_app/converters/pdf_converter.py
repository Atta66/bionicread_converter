from __future__ import annotations

from io import BytesIO
from typing import List

import fitz
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from bionic_app.bionic_text import bionify_text_to_html


def _pdf_color_to_css(color_value: int) -> str:
    red = (color_value >> 16) & 255
    green = (color_value >> 8) & 255
    blue = color_value & 255
    return f"#{red:02x}{green:02x}{blue:02x}"


def extract_pdf_page_texts(input_bytes: bytes) -> List[str]:
    document = fitz.open(stream=input_bytes, filetype="pdf")
    page_texts = [page.get_text("text") for page in document]
    document.close()
    return page_texts


def convert_pdf_to_pdf(input_bytes: bytes, ratio: float = 0.5, keep_page_size: bool = True) -> bytes:
    source = fitz.open(stream=input_bytes, filetype="pdf")
    output = fitz.open()

    for page in source:
        page_rect = page.rect
        out_page = output.new_page(
            width=page_rect.width if keep_page_size else fitz.paper_size("a4")[0],
            height=page_rect.height if keep_page_size else fitz.paper_size("a4")[1],
        )

        blocks = page.get_text("dict").get("blocks", [])
        for block in blocks:
            if block.get("type") != 0:
                continue

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if not text.strip():
                        continue

                    bbox = fitz.Rect(span.get("bbox", (0, 0, 0, 0)))
                    font_size = float(span.get("size", 10))
                    font_name = span.get("font", "Times-Roman")
                    color_css = _pdf_color_to_css(int(span.get("color", 0)))
                    transformed_html = bionify_text_to_html(text, ratio=ratio)

                    css = f"* {{ font-family: '{font_name}'; font-size: {font_size}px; color: {color_css}; }}"
                    html = f"<span>{transformed_html}</span>"

                    try:
                        out_page.insert_htmlbox(bbox, html, css=css)
                    except Exception:
                        out_page.insert_text(
                            fitz.Point(bbox.x0, bbox.y1),
                            text,
                            fontsize=font_size,
                            color=(0, 0, 0),
                        )

    output_bytes = output.tobytes(garbage=4, deflate=True)
    source.close()
    output.close()
    return output_bytes


def convert_epub_text_to_pdf(full_text: str, ratio: float = 0.5, keep_page_size: bool = True) -> bytes:
    packet = BytesIO()
    page_size = A4 if not keep_page_size else A4
    pdf = canvas.Canvas(packet, pagesize=page_size)

    width, height = page_size
    margin = 50
    cursor_y = height - margin
    line_height = 16

    for paragraph in full_text.splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            cursor_y -= line_height
            if cursor_y <= margin:
                pdf.showPage()
                cursor_y = height - margin
            continue

        words = paragraph.split(" ")
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if pdf.stringWidth(test_line, "Helvetica", 12) <= (width - margin * 2):
                line = test_line
                continue

            _draw_bionic_line(pdf, line, margin, cursor_y, ratio)
            cursor_y -= line_height
            if cursor_y <= margin:
                pdf.showPage()
                cursor_y = height - margin
            line = word

        if line:
            _draw_bionic_line(pdf, line, margin, cursor_y, ratio)
            cursor_y -= line_height
            if cursor_y <= margin:
                pdf.showPage()
                cursor_y = height - margin

    pdf.save()
    packet.seek(0)
    return packet.getvalue()


def _draw_bionic_line(pdf: canvas.Canvas, line: str, x: float, y: float, ratio: float) -> None:
    cursor_x = x
    for token in line.split(" "):
        if not token:
            continue
        prefix_len = max(1, int(round(len(token) * ratio))) if any(c.isalpha() for c in token) else 0
        strong = token[:prefix_len]
        rest = token[prefix_len:]

        if strong:
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(cursor_x, y, strong)
            cursor_x += pdf.stringWidth(strong, "Helvetica-Bold", 12)

        if rest:
            pdf.setFont("Helvetica", 12)
            pdf.drawString(cursor_x, y, rest)
            cursor_x += pdf.stringWidth(rest, "Helvetica", 12)

        pdf.setFont("Helvetica", 12)
        pdf.drawString(cursor_x, y, " ")
        cursor_x += pdf.stringWidth(" ", "Helvetica", 12)
