from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse


@dataclass(frozen=True)
class Link:
    href: str
    absolute_url: str


class _LinkExtractor(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self._base_url = base_url
        self.links: list[Link] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag != "a":
            return
        href = None
        for key, value in attrs:
            if key == "href":
                href = value
                break
        if not href:
            return
        absolute = urljoin(self._base_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            return
        self.links.append(Link(href=href, absolute_url=absolute))


def extract_links(html: str, *, base_url: str) -> list[Link]:
    parser = _LinkExtractor(base_url)
    parser.feed(html)
    return parser.links

