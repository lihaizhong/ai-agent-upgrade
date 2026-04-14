from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

try:
    from .http_utils import assert_host_allowed, fetch_https
    from .law_store import latest_parsed_payload, store_law_html
    from .workspace import ensure_workspace, get_workspace_paths
except ImportError:  # pragma: no cover
    from http_utils import assert_host_allowed, fetch_https
    from law_store import latest_parsed_payload, store_law_html
    from workspace import ensure_workspace, get_workspace_paths


LABOR_CONTRACT_LAW_DOC_ID = "labor_contract_law"
LABOR_CONTRACT_LAW_URL = (
    "https://flk.npc.gov.cn/detail?"
    "id=2c909fdd678bf17901678bf74d7106b3&fileId=&type=&title="
    "%E4%B8%AD%E5%8D%8E%E4%BA%BA%E6%B0%91%E5%85%B1%E5%92%8C%E5%9B%BD"
    "%E5%8A%B3%E5%8A%A8%E5%90%88%E5%90%8C%E6%B3%95"
)


_ALLOWED_LAW_HOSTS = {"flk.npc.gov.cn"}


@dataclass(frozen=True)
class LawFetchOutput:
    doc_id: str
    source_url: str
    retrieved_at: str
    content_hash: str
    parsed_json_path: str


def _decode_html(content_type: str | None, body: bytes) -> str:
    encoding = "utf-8"
    if content_type:
        match = re.search(r"charset=([\\w\\-]+)", content_type, re.IGNORECASE)
        if match:
            encoding = match.group(1).lower()
    try:
        return body.decode(encoding)
    except LookupError:
        return body.decode("utf-8", errors="replace")
    except UnicodeDecodeError:
        return body.decode("utf-8", errors="replace")


def fetch_and_store_law(
    skill_dir: Path,
    *,
    doc_id: str,
    url: str,
    username: str | None = None,
) -> LawFetchOutput:
    ensure_workspace(skill_dir, username=username)
    assert_host_allowed(url, _ALLOWED_LAW_HOSTS)

    result = fetch_https(url)
    html = _decode_html(result.content_type, result.body)

    paths = get_workspace_paths(skill_dir, username=username)
    stored = store_law_html(
        cache_law_dir=paths["cache_law_dir"],
        doc_id=doc_id,
        source_url=url,
        retrieved_at=result.retrieved_at,
        content_hash=result.sha256,
        html=html,
    )
    return LawFetchOutput(
        doc_id=stored.doc_id,
        source_url=stored.source_url,
        retrieved_at=stored.retrieved_at,
        content_hash=stored.content_hash,
        parsed_json_path=stored.parsed_json_path,
    )


def show_latest_parsed(
    skill_dir: Path,
    *,
    doc_id: str,
    username: str | None = None,
) -> dict | None:
    ensure_workspace(skill_dir, username=username)
    paths = get_workspace_paths(skill_dir, username=username)
    return latest_parsed_payload(paths["cache_law_dir"], doc_id)

