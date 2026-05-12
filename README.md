# Bionic Reading Converter (PDF/EPUB/HTML/AZW3)

A Streamlit app that converts documents into bionic-reading style to improve focus while reading.

## Features

- Input: `PDF` or `EPUB`
- Output: choose `PDF`, `EPUB`, `HTML`, or `AZW3`
- Bionic emphasis strength control
- Keep same/similar page size option
- Best size/quality preservation for same-format conversion:
  - `PDF -> PDF`
  - `EPUB -> EPUB`

## Quick Start

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

Venv activation helper

Windows (PowerShell):

```powershell
# create venv
python -m venv .venv
# activate for current session
& ".\.venv\Scripts\Activate.ps1"
```

Windows (Command Prompt):

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

macOS / Linux (bash/zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If you prefer not to activate, run pip using the venv's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

4. Open the URL shown by Streamlit (typically `http://localhost:8501`).

## Notes on Size & Quality

- **Same format output** (`PDF->PDF`, `EPUB->EPUB`) keeps structure/page sizing closest to source.
- **Cross format output** (`PDF->EPUB`, `EPUB->PDF`) prioritizes readable text + bionic styling; layout may change.
- **HTML output** is a simple, Kindle-friendly option if EPUB delivery fails.
- **AZW3 output** is for USB sideloading (Send-to-Kindle email does not accept AZW3).
- **Kindle-safe EPUB** uses Calibre's `ebook-convert` to rebuild EPUB for email delivery. If it is not on PATH, set
  `CALIBRE_CONVERT_PATH` (example: `C:\Program Files\Calibre2\ebook-convert.exe`).

## Tech Stack

- Streamlit (UI)
- PyMuPDF (PDF parsing/writing)
- EbookLib + BeautifulSoup (EPUB parsing/writing)
- ReportLab (EPUB text to PDF rendering)
