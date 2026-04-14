from __future__ import annotations

import sys
import unittest
from pathlib import Path


class TestProcedureCrawler(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        scripts_dir = repo_root / "agent-skills" / "labor-rights-defense" / "scripts"
        sys.path.insert(0, str(scripts_dir))

    def test_crawl_stays_within_gov_cn(self) -> None:
        from procedure_crawler import FetchedPage, crawl_procedure_pages

        pages = {
            "https://zj.gov.cn/seed": """
              <html><body>
                <a href="https://hangzhou.gov.cn/arbitration">HZ</a>
                <a href="https://example.com/phish">NO</a>
              </body></html>
            """.encode("utf-8"),
            "https://hangzhou.gov.cn/arbitration": """
              <html><body>
                <p>劳动人事争议仲裁 办事指南</p>
                <a href="https://hzhrss.gov.cn/more">more</a>
              </body></html>
            """.encode("utf-8"),
            "https://hzhrss.gov.cn/more": "<html><body><p>仲裁材料清单</p></body></html>".encode(
                "utf-8"
            ),
        }

        def fetcher(url: str) -> FetchedPage:
            return FetchedPage(url=url, retrieved_at="2026-04-14T00:00:00+08:00", body=pages[url])

        crawled = crawl_procedure_pages(
            seed_urls=["https://zj.gov.cn/seed"],
            fetcher=fetcher,
            max_pages=10,
        )
        urls = [p.url for p in crawled]
        self.assertIn("https://hangzhou.gov.cn/arbitration", urls)
        self.assertIn("https://hzhrss.gov.cn/more", urls)
        self.assertNotIn("https://example.com/phish", urls)

        referrers = {p.url: p.referrer_url for p in crawled}
        self.assertEqual(referrers["https://hangzhou.gov.cn/arbitration"], "https://zj.gov.cn/seed")


if __name__ == "__main__":
    unittest.main()
