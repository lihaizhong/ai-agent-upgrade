from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT / "agent-skills" / "prompt-learning" / "scripts" / "__main__.py"
)
WORKSPACE_ROOT = Path(tempfile.mkdtemp(prefix="prompt-learning-learning-workspace-"))
TEST_USERNAME = "prompt-learning-learning-test"
TEST_WORKSPACE = WORKSPACE_ROOT / TEST_USERNAME
TEST_ENV = {
    "PROMPT_LEARNING_ALLOW_USERNAME_OVERRIDE": "1",
    "PROMPT_LEARNING_WORKSPACE_ROOT": str(WORKSPACE_ROOT),
}


def run_cli(*args: str, stdin_data: dict | list | None = None) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args, "--username", TEST_USERNAME],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, **TEST_ENV},
        input=(
            None
            if stdin_data is None
            else json.dumps(stdin_data, ensure_ascii=False)
        ),
    )
    return json.loads(result.stdout)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class PromptLearningLearningCenterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        if WORKSPACE_ROOT.exists():
            shutil.rmtree(WORKSPACE_ROOT)

    def test_catalog_returns_selector_with_categories_and_courses(self) -> None:
        catalog = run_cli("learning", "--catalog")

        self.assertEqual(catalog["interaction"]["mode"], "selector")
        self.assertEqual(catalog["question"]["header"], "选择课程类别")
        self.assertEqual(len(catalog["categories"]), 6)

        first_category = catalog["categories"][0]
        self.assertEqual(first_category["name"], "基础课程")
        self.assertIn("interaction", first_category)
        self.assertIn("courses", first_category)
        self.assertGreater(len(first_category["courses"]), 0)

        first_course = first_category["courses"][0]
        self.assertIn("id", first_course)
        self.assertIn("name", first_course)
        self.assertIn("prerequisites", first_course)

    def test_category_filter_with_alias(self) -> None:
        category = run_cli("learning", "--category", "基础")

        self.assertEqual(category["name"], "基础课程")
        self.assertEqual(category["interaction"]["mode"], "selector")
        self.assertGreater(len(category["courses"]), 0)

    def test_category_filter_with_full_name(self) -> None:
        category = run_cli("learning", "--category", "推理课程")

        self.assertEqual(category["name"], "推理课程")

    def test_unknown_category_raises_error(self) -> None:
        error = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "learning", "--category", "不存在", "--username", TEST_USERNAME],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, **TEST_ENV},
        )

        self.assertNotEqual(error.returncode, 0)
        self.assertIn("未知课程类别", error.stderr)

    def test_lesson_meta_returns_course_info_and_updates_state(self) -> None:
        meta = run_cli("learning", "--lesson-meta", "--course", "3")

        self.assertEqual(meta["course_id"], 3)
        self.assertEqual(meta["course_name"], "思维链提示")
        self.assertEqual(meta["interaction"]["mode"], "inform")
        self.assertIn("file_path", meta)

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        self.assertEqual(current_state["current_module"], "learning")
        self.assertEqual(current_state["current_course_id"], 3)

    def test_lesson_meta_rejects_invalid_course(self) -> None:
        error = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "learning", "--lesson-meta", "--course", "99", "--username", TEST_USERNAME],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, **TEST_ENV},
        )

        self.assertNotEqual(error.returncode, 0)
        self.assertIn("课程 99 不存在", error.stderr)

    def test_code_meta_returns_code_file_path(self) -> None:
        meta = run_cli("learning", "--code-meta", "--course", "7")

        self.assertEqual(meta["course_id"], 7)
        self.assertEqual(meta["course_name"], "检索增强生成")
        self.assertIn("file_path", meta)
        self.assertTrue(Path(meta["file_path"]).exists())

    def test_code_meta_rejects_invalid_course(self) -> None:
        error = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "learning", "--code-meta", "--course", "99", "--username", TEST_USERNAME],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, **TEST_ENV},
        )

        self.assertNotEqual(error.returncode, 0)

    def test_lesson_panel_returns_selector_with_followup_options(self) -> None:
        panel = run_cli("learning", "--lesson-panel", "--course", "3")

        self.assertEqual(panel["interaction"]["mode"], "selector")
        self.assertEqual(panel["course_id"], 3)
        self.assertEqual(panel["question"]["header"], "练习完成")
        self.assertEqual(len(panel["question"]["options"]), 3)

        option_values = [opt["value"] for opt in panel["question"]["options"]]
        self.assertEqual(option_values, ["ask", "practice_more", "code"])

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        self.assertEqual(current_state["last_action"], "lesson_completed_waiting_practice")
        self.assertEqual(current_state["recommended_next_action"], "start_practice")

    def test_code_outline_returns_workflow_and_sections(self) -> None:
        outline = run_cli("learning", "--code-outline", "--course", "1")

        self.assertEqual(outline["interaction"]["mode"], "inform")
        self.assertEqual(outline["course_id"], 1)
        self.assertIn("workflow", outline)
        self.assertIn("sections", outline)
        self.assertGreater(len(outline["sections"]), 0)

        section_keys = [s["key"] for s in outline["sections"]]
        self.assertIn("setup", section_keys)
        self.assertIn("execution", section_keys)

    def test_recommend_course_with_current_course(self) -> None:
        run_cli("learning", "--lesson-meta", "--course", "5")
        rec = run_cli("learning", "--recommend-course")

        self.assertEqual(rec["course_id"], 5)
        self.assertEqual(rec["course_name"], "思维树")
        self.assertIn("继续当前课程", rec["recommendation"])

    def setUp(self) -> None:
        current_state_file = TEST_WORKSPACE / "progress" / "current-state.json"
        if current_state_file.exists():
            current_state_file.write_text(
                json.dumps({
                    "current_module": "home",
                    "current_course_id": None,
                    "current_course_name": None,
                    "last_action": "workspace_initialized",
                    "recommended_next_action": "open_dashboard",
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        course_progress_file = TEST_WORKSPACE / "progress" / "course-progress.json"
        if course_progress_file.exists():
            course_progress_file.write_text(
                json.dumps({
                    "completed_courses": [],
                    "in_progress_course": None,
                    "last_completed_course": None,
                    "course_status": {},
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def test_recommend_course_fresh_workspace(self) -> None:
        rec = run_cli("learning", "--recommend-course")

        self.assertEqual(rec["course_id"], 1)
        self.assertEqual(rec["course_name"], "零样本提示")

    def test_complete_course_updates_progress(self) -> None:
        run_cli("learning", "--complete", "--course", "2")

        progress = read_json(TEST_WORKSPACE / "progress" / "course-progress.json")
        self.assertIn(2, progress["completed_courses"])
        self.assertEqual(progress["last_completed_course"], 2)

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        self.assertEqual(current_state["last_action"], "course_completed")

    def test_complete_course_rejects_invalid_course(self) -> None:
        error = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "learning", "--complete", "--course", "99", "--username", TEST_USERNAME],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, **TEST_ENV},
        )

        self.assertNotEqual(error.returncode, 0)
        self.assertIn("课程 99 不存在", error.stderr)


if __name__ == "__main__":
    unittest.main()
