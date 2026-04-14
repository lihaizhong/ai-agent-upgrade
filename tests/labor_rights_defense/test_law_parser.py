from __future__ import annotations

import sys
import unittest
from pathlib import Path


class TestLawParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        scripts_dir = repo_root / "agent-skills" / "labor-rights-defense" / "scripts"
        sys.path.insert(0, str(scripts_dir))

    def test_parse_articles(self) -> None:
        from law_parser import parse_law_html

        html = """
        <html>
          <head><title>中华人民共和国劳动合同法</title></head>
          <body>
            <div class="content">
              <p>第一条 为了完善劳动合同制度，明确劳动合同双方当事人的权利和义务。</p>
              <p>第二条 中华人民共和国境内的企业等组织与劳动者建立劳动关系，订立、履行、变更、解除或者终止劳动合同，适用本法。</p>
              <p>第三条 订立劳动合同，应当遵循合法、公平、平等自愿、协商一致、诚实信用的原则。</p>
            </div>
          </body>
        </html>
        """
        payload = parse_law_html(html)
        self.assertIn("articles", payload)
        self.assertEqual(len(payload["articles"]), 3)
        self.assertEqual(payload["articles"][0]["locator"], "第一条")
        self.assertTrue(payload["articles"][0]["text"].startswith("第一条"))


if __name__ == "__main__":
    unittest.main()
