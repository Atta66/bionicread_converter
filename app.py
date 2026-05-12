from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from bionic_app.processor import convert_document

st.set_page_config(page_title="Bionic Reading Converter", page_icon="📚", layout="centered")

st.title("📚 Bionic Reading Converter")
st.write("Convert PDF/EPUB to a bionic-reading-friendly output for better focus.")

uploaded = st.file_uploader("Upload input document", type=["pdf", "epub"])
output_format = st.selectbox("Output format", options=["pdf", "epub", "html", "azw3"], index=0)
ratio = st.slider("Bionic emphasis strength", min_value=0.3, max_value=0.7, value=0.5, step=0.05)
keep_page_size = st.checkbox("Keep same/similar page size", value=True)
use_calibre_epub = st.checkbox("Kindle-safe EPUB (rebuild with Calibre)", value=True)

st.caption(
    "Best size/quality preservation is available for same-format conversion (PDF→PDF or EPUB→EPUB). "
    "Cross-format conversion keeps content fidelity but may adjust layout."
)

if uploaded and st.button("Convert", type="primary"):
    input_name = uploaded.name
    input_suffix = Path(input_name).suffix.lower().replace(".", "")

    if input_suffix not in {"pdf", "epub"}:
        st.error("Only PDF and EPUB inputs are supported.")
        st.stop()

    with st.spinner("Converting document..."):
        input_bytes = uploaded.read()
        output_bytes = convert_document(
            input_bytes=input_bytes,
            input_format=input_suffix,
            output_format=output_format,
            ratio=ratio,
            keep_page_size=keep_page_size,
            use_calibre_epub=use_calibre_epub,
        )

    base_name = os.path.splitext(input_name)[0]
    output_name = f"{base_name}.bionic.{output_format}"

    st.success("Conversion complete.")
    if output_format == "pdf":
        mime_type = "application/pdf"
    elif output_format == "epub":
        mime_type = "application/epub+zip"
    elif output_format == "azw3":
        mime_type = "application/vnd.amazon.ebook"
    else:
        mime_type = "text/html"

    st.download_button(
        "Download converted file",
        data=output_bytes,
        file_name=output_name,
        mime=mime_type,
    )
