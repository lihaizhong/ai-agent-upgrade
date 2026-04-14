from __future__ import annotations

import sys
import unittest
from pathlib import Path


class TestDraftService(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        scripts_dir = repo_root / "agent-skills" / "labor-rights-defense" / "scripts"
        sys.path.insert(0, str(scripts_dir))

    def test_generate_minimum_draft(self) -> None:
        from draft_service import generate_arbitration_application

        case = {
            "province": "浙江省",
            "city": "杭州市",
            "applicant": {"name": "张三", "phone": "13800000000"},
            "respondent": {"name": "某某科技有限公司"},
            "claims": ["支付拖欠工资人民币 X 元", "支付加班费人民币 Y 元"],
            "facts": [
                {"date": "2026-01-01", "event": "入职某某科技有限公司，岗位为软件工程师。"},
                {"date": "2026-03-31", "event": "公司未按约定支付工资并长期安排加班。"},
            ],
            "evidence": [
                {"name": "劳动合同", "purpose": "证明劳动关系与岗位/工资约定"},
                {"name": "考勤/工时记录", "purpose": "证明加班事实与时长"},
            ],
            "citations": [
                {
                    "doc_title": "《中华人民共和国劳动合同法》",
                    "doc_id": "labor_contract_law",
                    "locator": "第三条",
                    "source_url": "https://flk.npc.gov.cn/detail?id=xxx",
                    "retrieved_at": "2026-04-14T00:00:00+08:00",
                    "content_hash": "deadbeef",
                }
            ],
        }

        output = generate_arbitration_application(case)
        self.assertIn("劳动人事争议仲裁申请书", output.draft_markdown)
        self.assertIn("支付拖欠工资", output.draft_markdown)
        self.assertIn("## 官方依据引用", output.draft_markdown)
        self.assertEqual(output.warnings, [])


if __name__ == "__main__":
    unittest.main()

