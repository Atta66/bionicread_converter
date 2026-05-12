from __future__ import annotations

import html
import re
from typing import Iterable

WORD_RE = re.compile(r"(\w+|\s+|[^\w\s]+)", re.UNICODE)


def bionic_prefix_len(word: str, ratio: float = 0.5) -> int:
    if len(word) <= 1:
        return len(word)
    return max(1, min(len(word), int(round(len(word) * ratio))))


def bionify_word(word: str, ratio: float = 0.5) -> str:
    if not word or not any(char.isalpha() for char in word):
        return word
    prefix = bionic_prefix_len(word, ratio)
    return f"<strong>{html.escape(word[:prefix])}</strong>{html.escape(word[prefix:])}"


def bionify_text_to_html(text: str, ratio: float = 0.5) -> str:
    if not text:
        return ""

    parts: list[str] = []
    for token in WORD_RE.findall(text):
        if token.isspace():
            parts.append(token.replace("\n", "<br/>").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;"))
            continue

        if token.isalnum() or any(char.isalpha() for char in token):
            parts.append(bionify_word(token, ratio=ratio))
        else:
            parts.append(html.escape(token))

    return "".join(parts)


def bionify_text_plain(text: str, ratio: float = 0.5) -> str:
    if not text:
        return ""

    def transform_token(token: str) -> str:
        if token.isspace() or not any(char.isalpha() for char in token):
            return token
        prefix = bionic_prefix_len(token, ratio)
        return f"{token[:prefix]}{token[prefix:]}"

    return "".join(transform_token(token) for token in WORD_RE.findall(text))


def flatten_text_blocks(lines: Iterable[str]) -> str:
    return "\n\n".join(line.strip() for line in lines if line and line.strip())
