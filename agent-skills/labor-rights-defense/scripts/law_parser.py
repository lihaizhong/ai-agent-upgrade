from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser


class _VisibleTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in {"p", "br", "div", "li", "h1", "h2", "h3", "h4"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in {"p", "div", "li"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if not text:
            return
        self._chunks.append(text)
        self._chunks.append("\n")

    def text(self) -> str:
        raw = "".join(self._chunks)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


_ARTICLE_RE = re.compile(r"^第([一二三四五六七八九十百千万零〇\d]+)条")


@dataclass(frozen=True)
class Article:
    locator: str
    number_raw: str
    text: str


def extract_visible_text(html: str) -> str:
    parser = _VisibleTextExtractor()
    parser.feed(html)
    return parser.text()


def parse_articles_from_text(text: str) -> list[Article]:
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    articles: list[Article] = []
    current_locator: str | None = None
    current_number_raw: str | None = None
    current_parts: list[str] = []

    def flush() -> None:
        nonlocal current_locator, current_number_raw, current_parts
        if current_locator and current_number_raw and current_parts:
            articles.append(
                Article(
                    locator=current_locator,
                    number_raw=current_number_raw,
                    text="\n".join(current_parts).strip(),
                )
            )
        current_locator = None
        current_number_raw = None
        current_parts = []

    for line in lines:
        match = _ARTICLE_RE.match(line)
        if match:
            flush()
            number_raw = match.group(1)
            locator = f"第{number_raw}条"
            current_locator = locator
            current_number_raw = number_raw
            current_parts.append(line)
        else:
            if current_locator:
                current_parts.append(line)

    flush()
    return articles


def parse_law_html(html: str) -> dict:
    text = extract_visible_text(html)
    articles = parse_articles_from_text(text)
    return {
        "text": text,
        "articles": [
            {"locator": a.locator, "number_raw": a.number_raw, "text": a.text}
            for a in articles
        ],
    }

