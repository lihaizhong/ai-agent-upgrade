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
TEST_USERNAME = "prompt-learning-exam-session-test"
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


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class PromptLearningExamSessionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)

    def setUp(self) -> None:
        session_file = TEST_WORKSPACE / "exam" / "current-session.json"
        if session_file.exists():
            session_file.unlink()

    def test_start_session_creates_in_progress_exam(self) -> None:
        result = run_cli("exam", "--start", "--type", "diagnostic")

        self.assertEqual(result["status"], "in_progress")
        self.assertEqual(result["exam_type"], "diagnostic")
        self.assertEqual(result["current_question_num"], 1)
        self.assertEqual(result["current_slot"]["num"], 1)

        session_file = TEST_WORKSPACE / "exam" / "current-session.json"
        saved = read_json(session_file)
        self.assertEqual(saved["status"], "in_progress")
        self.assertEqual(saved["current_question_num"], 1)

    def test_resume_prompt_blocks_second_session(self) -> None:
        first = run_cli("exam", "--start", "--type", "final")
        second = run_cli("exam", "--start", "--type", "diagnostic")

        self.assertEqual(first["status"], "in_progress")
        self.assertTrue(second["has_in_progress"])
        self.assertEqual(second["interaction"]["mode"], "selector")
        self.assertEqual(second["question"]["options"][0]["value"], "resume")
        self.assertEqual(second["question"]["options"][1]["value"], "abandon")

    def test_current_question_and_abandon_session(self) -> None:
        started = run_cli("exam", "--start", "--type", "diagnostic")
        current = run_cli(
            "exam",
            "--current-question",
            "--session",
            started["session_id"],
        )
        abandoned = run_cli("exam", "--abandon", "--session", started["session_id"])
        resume = run_cli("exam", "--resume")

        self.assertEqual(current["session_id"], started["session_id"])
        self.assertEqual(current["current_slot"]["goal"], "基础概念识别")
        self.assertTrue(abandoned["abandoned"])
        self.assertEqual(abandoned["status"], "abandoned")
        self.assertFalse(resume["has_in_progress"])


if __name__ == "__main__":
    unittest.main()
