from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Final
from urllib.parse import urlparse
from urllib.request import Request, urlopen


_DEFAULT_UA: Final[str] = "ai-agent-upgrade/0.1 (labor-rights-defense)"


@dataclass(frozen=True)
class FetchResult:
    url: str
    retrieved_at: str
    content_type: str | None
    body: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.body).hexdigest()


def assert_https_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("Only https URLs are allowed")
    if not parsed.netloc:
        raise ValueError("Invalid URL")


def assert_host_allowed(url: str, allowed_hosts: set[str]) -> None:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host not in allowed_hosts:
        raise ValueError(f"Host not allowed: {host}")


def fetch_https(url: str, *, timeout_s: int = 20) -> FetchResult:
    assert_https_url(url)
    retrieved_at = datetime.now().astimezone().isoformat()
    req = Request(url, headers={"User-Agent": _DEFAULT_UA})
    with urlopen(req, timeout=timeout_s) as resp:  # noqa: S310
        body = resp.read()
        content_type = resp.headers.get("Content-Type")
    return FetchResult(
        url=url,
        retrieved_at=retrieved_at,
        content_type=content_type,
        body=body,
    )

