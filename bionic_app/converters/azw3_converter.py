from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def _ensure_ebook_convert() -> str:
    env_path = os.environ.get("CALIBRE_CONVERT_PATH")
    if env_path:
        candidate = Path(env_path)
        if candidate.exists():
            return str(candidate)

    tool = shutil.which("ebook-convert")
    if not tool:
        default_paths = [
            Path("C:/Program Files/Calibre2/ebook-convert.exe"),
            Path("C:/Program Files (x86)/Calibre2/ebook-convert.exe"),
        ]
        for candidate in default_paths:
            if candidate.exists():
                return str(candidate)

        raise RuntimeError(
            "Calibre's ebook-convert was not found. "
            "Install Calibre, add it to PATH, or set CALIBRE_CONVERT_PATH."
        )
    return tool


def convert_epub_bytes_to_azw3(epub_bytes: bytes, title: str) -> bytes:
    tool = _ensure_ebook_convert()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_path = tmp_path / "input.epub"
        output_path = tmp_path / "output.azw3"
        input_path.write_bytes(epub_bytes)

        subprocess.run(
            [
                tool,
                str(input_path),
                str(output_path),
                "--title",
                title,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        return output_path.read_bytes()


def convert_epub_bytes_with_calibre(epub_bytes: bytes, title: str, epub_version: str = "2") -> bytes:
    tool = _ensure_ebook_convert()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_path = tmp_path / "input.epub"
        output_path = tmp_path / "output.epub"
        input_path.write_bytes(epub_bytes)

        subprocess.run(
            [
                tool,
                str(input_path),
                str(output_path),
                "--title",
                title,
                "--epub-version",
                epub_version,
                "--no-default-epub-cover",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        return output_path.read_bytes()
