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
        exam_history_file = TEST_WORKSPACE / "exam" / "exam-history.jsonl"
        if exam_history_file.exists():
            exam_history_file.unlink()

    def _mc_question(self, num: int, difficulty: str, correct_answer: str = "A") -> dict:
        return {
            "type": "mc",
            "num": num,
            "difficulty": difficulty,
            "question": f"第 {num} 题题干",
            "options": [
                {"label": "A", "text": "选项 A", "description": ""},
                {"label": "B", "text": "选项 B", "description": ""},
                {"label": "C", "text": "选项 C", "description": ""},
                {"label": "D", "text": "选项 D", "description": ""},
            ],
            "correct_answer": correct_answer,
            "score": 5,
        }

    def _fill_question(self, num: int, difficulty: str, answer: str = "test answer") -> dict:
        return {
            "type": "fill",
            "num": num,
            "difficulty": difficulty,
            "question": f"第 {num} 题填空",
            "answer": answer,
            "acceptable_variants": [],
            "score": 10,
        }

    def _essay_question(self, num: int, difficulty: str) -> dict:
        return {
            "type": "essay",
            "num": num,
            "difficulty": difficulty,
            "scenario": f"第 {num} 题场景",
            "requirements": ["要求 1", "要求 2"],
            "scoring_rubric": {
                "结构完整": 0.4,
                "技术选择": 0.3,
                "权衡分析": 0.3,
            },
            "score": 15,
        }

    def _complete_diagnostic_exam(self, session_id: str) -> dict:
        difficulties = [
            "初级",
            "初级",
            "中级",
            "中级",
            "高级/专家",
            "中级",
            "中级",
            "高级",
            "中级",
            "高级",
            "专家",
        ]
        for num, difficulty in enumerate(difficulties, start=1):
            if num <= 5:
                question = self._mc_question(num, difficulty)
                payload = {"question": question, "answer": "A"}
            elif num <= 8:
                question = self._fill_question(num, difficulty)
                payload = {"question": question, "answer": "test answer"}
            else:
                question = self._essay_question(num, difficulty)
                payload = {
                    "question": question,
                    "answer": "完整回答",
                    "rubric_scores": {
                        "结构完整": 6,
                        "技术选择": 4.5,
                        "权衡分析": 4.5,
                    },
                }
            run_cli("exam", "--submit-answer", "--session", session_id, stdin_data=payload)
        return run_cli("exam", "--finish", "--session", session_id)

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

    def test_submit_answer_advances_without_feedback(self) -> None:
        started = run_cli("exam", "--start", "--type", "diagnostic")
        submit = run_cli(
            "exam",
            "--submit-answer",
            "--session",
            started["session_id"],
            stdin_data={
                "question": self._mc_question(1, "初级"),
                "answer": "A",
            },
        )
        current = run_cli(
            "exam",
            "--current-question",
            "--session",
            started["session_id"],
        )

        self.assertTrue(submit["recorded"])
        self.assertFalse(submit["finished"])
        self.assertEqual(submit["next_question_num"], 2)
        self.assertNotIn("score", submit)
        self.assertEqual(current["current_question_num"], 2)
        self.assertEqual(current["current_slot"]["num"], 2)

    def test_finish_session_generates_report_and_history(self) -> None:
        started = run_cli("exam", "--start", "--type", "diagnostic")
        finished = self._complete_diagnostic_exam(started["session_id"])
        session_file = TEST_WORKSPACE / "exam" / "current-session.json"
        exam_history_path = TEST_WORKSPACE / "exam" / "exam-history.jsonl"
        session = read_json(session_file)
        rows = [
            json.loads(line)
            for line in exam_history_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self.assertTrue(finished["finished"])
        self.assertEqual(finished["score"], 100)
        self.assertTrue(Path(finished["report_path"]).exists())
        self.assertEqual(session["status"], "completed")
        self.assertEqual(rows[-1]["score"], 100)
        self.assertEqual(rows[-1]["exam_type"], "diagnostic")


if __name__ == "__main__":
    unittest.main()
