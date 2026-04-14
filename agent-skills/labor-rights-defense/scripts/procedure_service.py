from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from .config import find_province_seeds, load_procedure_seeds
    from .http_utils import assert_https_url, fetch_https
    from .procedure_crawler import FetchedPage, crawl_procedure_pages, is_gov_cn_host
    from .workspace import ensure_workspace, get_workspace_paths
except ImportError:  # pragma: no cover
    from config import find_province_seeds, load_procedure_seeds
    from http_utils import assert_https_url, fetch_https
    from procedure_crawler import FetchedPage, crawl_procedure_pages, is_gov_cn_host
    from workspace import ensure_workspace, get_workspace_paths


@dataclass(frozen=True)
class ProcedureCrawlRun:
    run_id: str
    run_dir: str
    pages: list[dict]


def _run_id() -> str:
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def crawl_procedure(
    skill_dir: Path,
    *,
    province: str,
    city: str | None = None,
    max_pages: int = 30,
    username: str | None = None,
) -> ProcedureCrawlRun:
    ensure_workspace(skill_dir, username=username)
    seeds = load_procedure_seeds(skill_dir)
    province_item = find_province_seeds(seeds, province)
    if not province_item:
        raise ValueError(f"Unknown province in seeds config: {province}")

    seed_urls: list[str] = []
    seed_urls.extend(province_item.get("province_seeds", []))
    seed_urls.extend(province_item.get("city_seeds", []))
    if not seed_urls:
        raise ValueError(f"No seed URLs configured for province: {province}")

    for url in seed_urls:
        assert_https_url(url)
        if not is_gov_cn_host(url):
            raise ValueError("procedure seed must be *.gov.cn")

    paths = get_workspace_paths(skill_dir, username=username)
    run_id = _run_id()
    run_dir = Path(paths["cache_procedure_dir"]) / province / run_id
    pages_dir = run_dir / "pages"
    _ensure_dir(pages_dir)

    def fetcher(url: str) -> FetchedPage:
        assert_https_url(url)
        if not is_gov_cn_host(url):
            raise ValueError("procedure fetch must be *.gov.cn")
        result = fetch_https(url)
        return FetchedPage(url=url, retrieved_at=result.retrieved_at, body=result.body)

    pages = crawl_procedure_pages(
        seed_urls=seed_urls,
        fetcher=fetcher,
        max_pages=max_pages,
    )

    stored_pages: list[dict] = []
    for page in pages:
        raw_path = pages_dir / f"{page.content_hash}.html"
        meta_path = pages_dir / f"{page.content_hash}.json"

        if not raw_path.exists():
            # Raw body is not kept by crawler; re-fetch to store raw snapshot for traceability.
            fetched = fetcher(page.url)
            raw_path.write_bytes(fetched.body)

        meta = {
            "url": page.url,
            "referrer_url": page.referrer_url,
            "retrieved_at": page.retrieved_at,
            "content_hash": page.content_hash,
            "text_snippet": page.text_snippet,
            "matched_keywords": page.matched_keywords,
            "raw_html_path": str(raw_path),
        }
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        stored_pages.append(meta)

    run_summary = {
        "run_id": run_id,
        "province": province,
        "city": city,
        "max_pages": max_pages,
        "seed_urls": seed_urls,
        "page_count": len(stored_pages),
        "pages_dir": str(pages_dir),
        "pages": stored_pages,
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(
        json.dumps(run_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return ProcedureCrawlRun(run_id=run_id, run_dir=str(run_dir), pages=stored_pages)

