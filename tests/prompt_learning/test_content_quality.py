from __future__ import annotations

import json
import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "agent-skills" / "prompt-learning"
COURSES_DIR = SKILL_DIR / "courses"
CODE_DIR = SKILL_DIR / "code"
DOCS_DIR = REPO_ROOT / "docs" / "prompt-learning-architecture"
SCRIPTS_DIR = SKILL_DIR / "scripts"

spec = importlib.util.spec_from_file_location(
    "prompt_learning_workspace", SCRIPTS_DIR / "workspace.py"
)
if spec is None or spec.loader is None:
    raise ImportError("Cannot load prompt-learning workspace module")
workspace_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = workspace_module
spec.loader.exec_module(workspace_module)
get_workspace_root = workspace_module.get_workspace_root


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class PromptLearningContentQualityTest(unittest.TestCase):
    def test_workspace_root_resolves_from_skill_symlink_paths(self) -> None:
        expected = REPO_ROOT / "prompt-learning-workspace"

        self.assertEqual(
            get_workspace_root(REPO_ROOT / ".codex" / "skills" / "prompt-learning"),
            expected,
        )
        self.assertEqual(
            get_workspace_root(REPO_ROOT / ".opencode" / "skills" / "prompt-learning"),
            expected,
        )

    def test_skill_contract_keeps_platform_modules_and_selector_rules(self) -> None:
        skill_text = read_text(SKILL_DIR / "SKILL.md")
        for token in ["学习中心", "练习中心", "考试中心", "Prompt Lab", "学习档案"]:
            self.assertIn(token, skill_text)
        self.assertIn("选择器优先", skill_text)
        self.assertNotIn("提示词生成模式", skill_text)

    def test_course_and_code_assets_match_catalog(self) -> None:
        course_files = sorted(COURSES_DIR.glob("[0-9][0-9]-*.md"))
        code_files = sorted(CODE_DIR.glob("[0-9][0-9]_*.py"))

        self.assertEqual(len(course_files), 17)
        self.assertEqual(len(code_files), 17)
        self.assertEqual(
            {int(path.name[:2]) for path in course_files},
            {int(path.name[:2]) for path in code_files},
        )

    def test_architecture_docs_cover_current_product_modules(self) -> None:
        expected_docs = [
            "overview.md",
            "cli-and-modules.md",
            "learning-center.md",
            "practice-center.md",
            "exam-center.md",
            "prompt-lab.md",
            "workspace-and-persistence.md",
            "state-model.md",
        ]
        for name in expected_docs:
            self.assertTrue((DOCS_DIR / name).exists(), msg=name)

    def test_evals_reflect_platform_mental_model(self) -> None:
        evals = json.loads(read_text(SKILL_DIR / "evals" / "evals.json"))
        self.assertEqual(evals["version"], "8.1.0")

        eval_names = {item["name"] for item in evals["evals"]}
        self.assertIn("平台首页-统一入口", eval_names)
        self.assertIn("Prompt Lab-实战入口", eval_names)
        self.assertIn("平台心智-不再暴露旧模式", eval_names)


if __name__ == "__main__":
    unittest.main()
