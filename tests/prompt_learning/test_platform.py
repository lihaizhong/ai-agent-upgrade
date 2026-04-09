from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT / "agent-skills" / "prompt-learning" / "scripts" / "__main__.py"
)
WORKSPACE_ROOT = REPO_ROOT / "prompt-learning-workspace"
TEST_USERNAME = "prompt-learning-test"
TEST_WORKSPACE = WORKSPACE_ROOT / TEST_USERNAME


def run_cli(*args: str, stdin_data: dict | list | None = None) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args, "--username", TEST_USERNAME],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        input=(
            None
            if stdin_data is None
            else json.dumps(stdin_data, ensure_ascii=False)
        ),
    )
    return json.loads(result.stdout)


class PromptLearningPlatformSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)

    def test_workspace_bootstrap_creates_expected_files(self) -> None:
        learner_file = TEST_WORKSPACE / "profile" / "learner.json"
        current_state_file = TEST_WORKSPACE / "progress" / "current-state.json"
        template_index_file = TEST_WORKSPACE / "prompt-lab" / "template-index.json"

        self.assertTrue(learner_file.exists())
        self.assertTrue(current_state_file.exists())
        self.assertTrue(template_index_file.exists())

        learner = json.loads(learner_file.read_text(encoding="utf-8"))
        self.assertEqual(learner["workspace_user"], TEST_USERNAME)

    def test_home_dashboard_and_learning_catalog(self) -> None:
        dashboard = run_cli("home", "--dashboard")
        self.assertEqual(dashboard["user"]["workspace_user"], TEST_USERNAME)
        self.assertEqual(len(dashboard["cards"]), 4)
        self.assertEqual(dashboard["question"]["header"], "学习平台")

        catalog = run_cli("learning", "--catalog")
        self.assertEqual(len(catalog["categories"]), 6)
        self.assertEqual(catalog["categories"][0]["name"], "基础课程")

        recommend = run_cli("learning", "--recommend-course")
        self.assertEqual(recommend["course_id"], 1)
        self.assertEqual(recommend["course_name"], "零样本提示")

    def test_learning_practice_lab_exam_and_profile_flows(self) -> None:
        lesson_meta = run_cli("learning", "--lesson-meta", "--course", "3")
        self.assertEqual(lesson_meta["course_id"], 3)

        blueprint = run_cli("practice", "--blueprint", "--mode", "current")
        self.assertEqual(blueprint["course_id"], 3)
        self.assertEqual(blueprint["question_type"], "diagnose")

        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 3,
                "course_name": "思维链提示",
                "entry_type": "current",
                "question_type": "diagnose",
                "result": "partial",
                "mistake_tags": ["clarity"],
                "strength_tags": ["structure"],
                "feedback_summary": "能说出主思路，但约束和边界不够清楚。",
            },
        )

        checklist = run_cli("lab", "--review-checklist")
        self.assertGreaterEqual(len(checklist["checklist"]), 6)

        saved_template = run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "meeting-summary",
                "topic": "summary",
                "slots": {
                    "task": "写总结",
                    "input": "会议纪要",
                    "output_format": "JSON",
                    "constraints": "只用中文",
                    "quality_bar": "字段稳定",
                },
                "prompt": "请把会议纪要总结成 JSON",
                "notes": "smoke-test",
                "tags": ["summary"],
            },
        )
        self.assertTrue(saved_template["saved"])

        exam_structure = run_cli("exam", "--structure", "--type", "diagnostic")
        self.assertEqual(exam_structure["total_questions"], 11)

        run_cli(
            "exam",
            "--record-history",
            stdin_data={
                "exam_type": "diagnostic",
                "score": 72,
                "total_score": 100,
                "weak_courses": [3],
                "weak_topics": ["clarity"],
                "report_path": "/tmp/prompt-learning-report.md",
            },
        )

        profile = run_cli("profile", "--summary")
        self.assertEqual(profile["current"]["module"], "exam")
        self.assertGreaterEqual(profile["mistakes"]["open_count"], 1)
        self.assertEqual(profile["exams"]["count"], 1)
        self.assertEqual(profile["templates"]["count"], 1)


if __name__ == "__main__":
    unittest.main()
