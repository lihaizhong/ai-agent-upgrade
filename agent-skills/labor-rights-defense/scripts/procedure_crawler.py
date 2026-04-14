from __future__ import annotations

import hashlib
from dataclasses import dataclass
from urllib.parse import urlparse

try:
    from .html_links import extract_links
    from .law_parser import extract_visible_text
except ImportError:  # pragma: no cover
    from html_links import extract_links
    from law_parser import extract_visible_text


@dataclass(frozen=True)
class FetchedPage:
    url: str
    retrieved_at: str
    body: bytes


@dataclass(frozen=True)
class ProcedurePage:
    url: str
    referrer_url: str | None
    retrieved_at: str
    content_hash: str
    text_snippet: str
    matched_keywords: list[str]


def is_gov_cn_host(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    return host.endswith(".gov.cn") or host == "gov.cn"

def _sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def crawl_procedure_pages(
    *,
    seed_urls: list[str],
    fetcher,  # (url) -> FetchedPage
    max_pages: int = 50,
    keywords: list[str] | None = None,
) -> list[ProcedurePage]:
    if not seed_urls:
        raise ValueError("No seed URLs provided")
    if max_pages <= 0:
        raise ValueError("max_pages must be > 0")
    keywords = keywords or ["劳动人事争议仲裁", "仲裁", "劳动仲裁", "劳动争议"]

    queue: list[tuple[str, str | None]] = [(u, None) for u in seed_urls]
    seen: set[str] = set()
    pages: list[ProcedurePage] = []

    while queue and len(pages) < max_pages:
        url, referrer = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)

        if not is_gov_cn_host(url):
            continue

        fetched = fetcher(url)
        html = fetched.body.decode("utf-8", errors="replace")

        visible = extract_visible_text(html)
        matched = [kw for kw in keywords if kw in visible]
        snippet = visible[:400]

        pages.append(
            ProcedurePage(
                url=url,
                referrer_url=referrer,
                retrieved_at=fetched.retrieved_at,
                content_hash=_sha256_bytes(fetched.body),
                text_snippet=snippet,
                matched_keywords=matched,
            )
        )

        for link in extract_links(html, base_url=url):
            if link.absolute_url not in seen and is_gov_cn_host(link.absolute_url):
                queue.append((link.absolute_url, url))

    return pages
