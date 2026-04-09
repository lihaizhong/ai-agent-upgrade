from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "agent-skills" / "rag-learning"
COURSES_DIR = SKILL_DIR / "courses"
REFERENCE_DIR = SKILL_DIR / "reference"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_catalog_course_rows() -> list[dict]:
    lines = read_text(REFERENCE_DIR / "catalog.md").splitlines()
    header = "| 编号 | 课程 | 难度 | 预计时长 | 适用人群 |"
    start = lines.index(header)
    rows: list[dict] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(
            {
                "id": int(cells[0]),
                "name": cells[1],
                "difficulty": cells[2],
                "duration": cells[3],
                "audience": cells[4],
            }
        )
    return rows


class RagLearningContentQualityTest(unittest.TestCase):
    def test_skill_contract_uses_platform_modules(self) -> None:
        skill_text = read_text(SKILL_DIR / "SKILL.md")
        for token in ["学习中心", "实战中心", "RAG Lab", "架构评审", "学习档案"]:
            self.assertIn(token, skill_text)
        self.assertNotIn("零步检查", skill_text)

    def test_catalog_matches_course_files(self) -> None:
        rows = parse_catalog_course_rows()
        course_files = sorted(COURSES_DIR.glob("[0-9][0-9]-*.md"))

        self.assertEqual(len(rows), len(course_files))

        expected_ids = {row["id"] for row in rows}
        actual_ids = {int(path.name[:2]) for path in course_files}
        self.assertEqual(expected_ids, actual_ids)

    def test_courses_readme_declares_platform_mainline(self) -> None:
        readme = read_text(COURSES_DIR / "README.md")
        for token in ["平台主线", "基础理解", "组件选型", "第一个项目", "企业与线上"]:
            self.assertIn(token, readme)

    def test_key_courses_include_platform_positioning(self) -> None:
        expected_files = [
            "04-Embedding模型选择.md",
            "05-Rerank模型选择.md",
            "06-检索策略优化.md",
            "07-文档问答RAG.md",
            "10-企业级RAG架构.md",
            "12-RAG评估与调优.md",
        ]
        for name in expected_files:
            content = read_text(COURSES_DIR / name)
            self.assertIn("## 在平台中的位置", content, msg=name)
            self.assertIn("## 使用提醒", content, msg=name)

    def test_platform_config_has_lab_and_review_definitions(self) -> None:
        config = json.loads(read_text(REFERENCE_DIR / "platform-config.json"))

        self.assertEqual(
            set(config["lab_topics"].keys()),
            {"embedding", "rerank", "chunking"},
        )
        self.assertEqual(
            set(config["review_scenarios"].keys()),
            {
                "enterprise-knowledge-search",
                "customer-support-rag",
                "private-deployment-rag",
            },
        )
        self.assertGreaterEqual(len(config["review_fields"]), 10)

    def test_catalog_declares_learning_center_mainline_and_handoffs(self) -> None:
        catalog = read_text(REFERENCE_DIR / "catalog.md")
        for token in ["学习中心主线", "模块衔接建议", "学完 04", "学完 07", "学完 10 / 12"]:
            self.assertIn(token, catalog)

    def test_evals_reflect_platform_mental_model(self) -> None:
        evals = json.loads(read_text(SKILL_DIR / "evals" / "evals.json"))
        self.assertEqual(evals["version"], "2.0.0")

        eval_names = {item["name"] for item in evals["evals"]}
        self.assertIn("学习中心-基础入门推荐", eval_names)
        self.assertIn("意图不明确-平台首页分流", eval_names)

    def test_no_unassigned_track_left_in_catalog_mainline_logic(self) -> None:
        catalog = read_text(REFERENCE_DIR / "catalog.md")
        mainline_section = re.search(
            r"## 学习中心主线(.*?)## 模块衔接建议", catalog, flags=re.S
        )
        self.assertIsNotNone(mainline_section)
        section = mainline_section.group(1)
        self.assertIn("07", section)
        self.assertIn("08", section)
        self.assertIn("09", section)


if __name__ == "__main__":
    unittest.main()
