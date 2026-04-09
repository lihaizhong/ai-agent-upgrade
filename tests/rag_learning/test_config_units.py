from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "agent-skills" / "rag-learning"
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from catalog import load_course_catalog, load_recommended_paths, load_scenarios  # noqa: E402
from config import load_lab_topics  # noqa: E402
from config import load_platform_config  # noqa: E402
from config import load_review_fields  # noqa: E402
from config import load_review_scenarios  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "rag_learning_workspace", SCRIPTS_DIR / "workspace.py"
)
if spec is None or spec.loader is None:
    raise ImportError("Cannot load rag-learning workspace module")
workspace_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = workspace_module
spec.loader.exec_module(workspace_module)
get_workspace_root = workspace_module.get_workspace_root


class RagLearningConfigUnitTest(unittest.TestCase):
    def test_workspace_root_resolves_from_skill_symlink_paths(self) -> None:
        expected = REPO_ROOT / "rag-learning-workspace"

        self.assertEqual(
            get_workspace_root(REPO_ROOT / ".codex" / "skills" / "rag-learning"),
            expected,
        )
        self.assertEqual(
            get_workspace_root(REPO_ROOT / ".opencode" / "skills" / "rag-learning"),
            expected,
        )

    def test_load_course_catalog_returns_expected_fields(self) -> None:
        courses = load_course_catalog(SKILL_DIR)

        self.assertEqual(len(courses), 12)
        self.assertEqual(courses[0]["id"], 1)
        self.assertEqual(courses[0]["track"], "foundations")
        self.assertEqual(courses[6]["id"], 7)
        self.assertEqual(courses[6]["track"], "practice")
        self.assertTrue(all(item["slug"].endswith(".md") for item in courses))

    def test_recommended_paths_match_documented_sequences(self) -> None:
        paths = load_recommended_paths(SKILL_DIR)

        self.assertEqual(paths["novice"], [1, 2, 3, 7])
        self.assertEqual(paths["intermediate"], [4, 6, 7, 8])
        self.assertEqual(paths["advanced"], [5, 9, 11, 12])
        self.assertEqual(paths["enterprise"], [10, 11, 12])

    def test_load_scenarios_maps_known_projects(self) -> None:
        scenarios = load_scenarios(SKILL_DIR)
        scenario_map = {item["name"]: item for item in scenarios}

        self.assertEqual(
            scenario_map["文档问答系统"]["project_id"], "local-minimum-rag"
        )
        self.assertEqual(
            scenario_map["客服机器人"]["project_id"], "customer-support-rag"
        )
        self.assertEqual(
            scenario_map["企业知识库搜索"]["project_id"],
            "enterprise-knowledge-search",
        )
        self.assertIsNone(scenario_map["垂直领域问答"]["project_id"])

    def test_platform_config_contains_required_sections(self) -> None:
        config = load_platform_config(SKILL_DIR)

        self.assertIn("lab_topics", config)
        self.assertIn("review_scenarios", config)
        self.assertIn("review_fields", config)

    def test_lab_topics_have_required_keys(self) -> None:
        topics = load_lab_topics(SKILL_DIR)

        for topic_name, topic in topics.items():
            self.assertIn("label", topic, msg=topic_name)
            self.assertIn("goal", topic, msg=topic_name)
            self.assertIn("metrics", topic, msg=topic_name)
            self.assertIn("competency_area", topic, msg=topic_name)
            self.assertGreaterEqual(len(topic["default_variants"]), 2, msg=topic_name)

    def test_review_scenarios_and_fields_are_stable(self) -> None:
        scenarios = load_review_scenarios(SKILL_DIR)
        fields = load_review_fields(SKILL_DIR)

        self.assertIn("enterprise-knowledge-search", scenarios)
        self.assertIn("customer-support-rag", scenarios)
        self.assertIn("private-deployment-rag", scenarios)
        self.assertIn("推荐架构", fields)
        self.assertIn("主要风险", fields)
        self.assertGreaterEqual(len(fields), 10)


if __name__ == "__main__":
    unittest.main()
