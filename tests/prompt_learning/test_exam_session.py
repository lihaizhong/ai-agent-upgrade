from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path
import importlib.util


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT / "agent-skills" / "prompt-learning" / "scripts" / "__main__.py"
)
WORKSPACE_ROOT = Path(tempfile.mkdtemp(prefix="prompt-learning-exam-workspace-"))
TEST_USERNAME = "prompt-learning-exam-session-test"
TEST_WORKSPACE = WORKSPACE_ROOT / TEST_USERNAME
TEST_ENV = {
    "PROMPT_LEARNING_ALLOW_USERNAME_OVERRIDE": "1",
    "PROMPT_LEARNING_WORKSPACE_ROOT": str(WORKSPACE_ROOT),
}

spec = importlib.util.spec_from_file_location(
    "prompt_learning_exam_workspace",
    REPO_ROOT / "agent-skills" / "prompt-learning" / "scripts" / "workspace.py",
)
if spec is None or spec.loader is None:
    raise ImportError("Cannot load prompt-learning workspace module")
workspace_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = workspace_module
spec.loader.exec_module(workspace_module)
sys.path.append(str(REPO_ROOT / "agent-skills" / "prompt-learning"))
ExamEngine = importlib.import_module("scripts.exam").ExamEngine


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


def run_cli_error(*args: str, stdin_data: dict | list | None = None) -> subprocess.CalledProcessError:
    with unittest.TestCase().assertRaises(subprocess.CalledProcessError) as ctx:
        subprocess.run(
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
    return ctx.exception


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
        if WORKSPACE_ROOT.exists():
            shutil.rmtree(WORKSPACE_ROOT)

    def setUp(self) -> None:
        session_file = TEST_WORKSPACE / "exam" / "current-session.json"
        if session_file.exists():
            session_file.unlink()
        exam_history_file = TEST_WORKSPACE / "exam" / "exam-history.jsonl"
        if exam_history_file.exists():
            exam_history_file.unlink()

    def _mc_question(
        self,
        num: int,
        difficulty: str,
        correct_answer: str = "A",
        course_id: int | None = None,
        topic_tags: list[str] | None = None,
    ) -> dict:
        return {
            "type": "mc",
            "num": num,
            "difficulty": difficulty,
            "question": f"第 {num} 题题干",
            "course_id": course_id,
            "topic_tags": topic_tags or [],
            "options": [
                {"label": "A", "text": "选项 A", "description": ""},
                {"label": "B", "text": "选项 B", "description": ""},
                {"label": "C", "text": "选项 C", "description": ""},
                {"label": "D", "text": "选项 D", "description": ""},
            ],
            "correct_answer": correct_answer,
            "score": 5,
        }

    def _fill_question(
        self,
        num: int,
        difficulty: str,
        answer: str = "test answer",
        course_id: int | None = None,
        topic_tags: list[str] | None = None,
    ) -> dict:
        return {
            "type": "fill",
            "num": num,
            "difficulty": difficulty,
            "question": f"第 {num} 题填空",
            "course_id": course_id,
            "topic_tags": topic_tags or [],
            "answer": answer,
            "acceptable_variants": [],
            "score": 10,
        }

    def _essay_question(
        self,
        num: int,
        difficulty: str,
        course_id: int | None = None,
        topic_tags: list[str] | None = None,
    ) -> dict:
        return {
            "type": "essay",
            "num": num,
            "difficulty": difficulty,
            "scenario": f"第 {num} 题场景",
            "course_id": course_id,
            "topic_tags": topic_tags or [],
            "requirements": ["要求 1", "要求 2"],
            "scoring_rubric": {
                "结构完整": 0.4,
                "技术选择": 0.3,
                "权衡分析": 0.3,
            },
            "score": 15,
        }

    def _complete_exam(self, session_id: str, exam_type: str = "diagnostic") -> dict:
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
                question = self._mc_question(
                    num,
                    difficulty,
                    course_id=num if exam_type == "diagnostic" else num + 20,
                    topic_tags=[f"{exam_type}-mc-topic-{num}"],
                )
                answer = "A" if num == 1 else "B"
                answer_payload = {"answer": answer, "question_num": num}
            elif num <= 8:
                question = self._fill_question(
                    num,
                    difficulty,
                    course_id=num if exam_type == "diagnostic" else num + 20,
                    topic_tags=[f"{exam_type}-fill-topic-{num}"],
                )
                answer = "test answer" if num == 6 else "wrong answer"
                answer_payload = {"answer": answer, "question_num": num}
            else:
                question = self._essay_question(
                    num,
                    difficulty,
                    course_id=num if exam_type == "diagnostic" else num + 20,
                    topic_tags=[f"{exam_type}-essay-topic-{num}"],
                )
                answer_payload = {
                    "answer": "完整回答",
                    "question_num": num,
                    "rubric_scores": {
                        "结构完整": 6 if num == 9 else 3,
                        "技术选择": 4.5 if num == 9 else 2,
                        "权衡分析": 4.5 if num == 9 else 2,
                    },
                }
            run_cli(
                "exam",
                "--submit-question",
                "--session",
                session_id,
                stdin_data={"question": question},
            )
            run_cli(
                "exam",
                "--submit-answer",
                "--session",
                session_id,
                stdin_data=answer_payload,
            )
        return run_cli("exam", "--finish", "--session", session_id)

    def _assert_finished_exam(
        self,
        *,
        finished: dict,
        session: dict,
        rows: list[dict],
        expected_type: str,
        expected_weak_courses: list[int],
        expected_weak_topics: list[str],
    ) -> None:
        self.assertTrue(finished["finished"])
        self.assertEqual(finished["exam_type"], expected_type)
        self.assertLess(finished["score"], 100)
        self.assertTrue(Path(finished["report_path"]).exists())
        self.assertEqual(session["status"], "completed")
        self.assertEqual(finished["weak_courses"], expected_weak_courses)
        self.assertEqual(finished["weak_topics"], expected_weak_topics)
        self.assertEqual(rows[-1]["score"], finished["score"])
        self.assertEqual(rows[-1]["exam_type"], expected_type)
        self.assertEqual(rows[-1]["weak_courses"], expected_weak_courses)
        self.assertEqual(rows[-1]["weak_topics"], expected_weak_topics)

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
        run_cli(
            "exam",
            "--submit-question",
            "--session",
            started["session_id"],
            stdin_data={
                "question": self._mc_question(
                    1,
                    "初级",
                    course_id=1,
                    topic_tags=["diagnostic-mc-topic-1"],
                )
            },
        )
        stored_question = run_cli(
            "exam",
            "--current-question",
            "--session",
            started["session_id"],
        )
        submit = run_cli(
            "exam",
            "--submit-answer",
            "--session",
            started["session_id"],
            stdin_data={
                "answer": "A",
                "question_num": 1,
            },
        )
        current = run_cli(
            "exam",
            "--current-question",
            "--session",
            started["session_id"],
        )

        self.assertEqual(stored_question["interaction"]["mode"], "selector")
        self.assertEqual(stored_question["question"]["options"][0]["value"], "A")
        self.assertTrue(submit["recorded"])
        self.assertFalse(submit["finished"])
        self.assertEqual(submit["next_question_num"], 2)
        self.assertNotIn("score", submit)
        self.assertEqual(current["current_question_num"], 2)
        self.assertEqual(current["current_slot"]["num"], 2)

    def test_submit_answer_rejects_missing_weakness_metadata(self) -> None:
        started = run_cli("exam", "--start", "--type", "diagnostic")
        error = run_cli_error(
            "exam",
            "--submit-question",
            "--session",
            started["session_id"],
            stdin_data={
                "question": {
                    "type": "mc",
                    "num": 1,
                    "difficulty": "初级",
                    "question": "缺少元数据的题目",
                    "options": [
                        {"label": "A", "text": "选项 A", "description": ""},
                        {"label": "B", "text": "选项 B", "description": ""},
                        {"label": "C", "text": "选项 C", "description": ""},
                        {"label": "D", "text": "选项 D", "description": ""},
                    ],
                    "correct_answer": "A",
                    "score": 5,
                }
            },
        )

        self.assertIn("course_id 必须是整数", error.stderr)

    def test_report_path_uses_safe_username_component(self) -> None:
        skill_dir = REPO_ROOT / "agent-skills" / "prompt-learning"
        safe_username = workspace_module.normalize_workspace_username("../unsafe user")
        with mock.patch.dict(os.environ, TEST_ENV, clear=False):
            report_engine = ExamEngine(skill_dir=skill_dir, username=TEST_USERNAME)
            report_path = Path(
                report_engine.generate_report([], [], [], "../unsafe user")
            )

        self.assertEqual(
            report_path.parent.resolve(),
            (TEST_WORKSPACE / "exam" / "reports").resolve(),
        )
        self.assertEqual(report_path.name.count("/"), 0)
        self.assertIn(f"-{safe_username}-prompt-learning-exam.md", report_path.name)

    def test_grade_fill_treats_whitespace_only_formatting_diff_as_nonzero(self) -> None:
        skill_dir = REPO_ROOT / "agent-skills" / "prompt-learning"
        with mock.patch.dict(os.environ, TEST_ENV, clear=False):
            engine = ExamEngine(skill_dir=skill_dir, username=TEST_USERNAME)

        question = {
            "type": "fill",
            "num": 6,
            "difficulty": "中级",
            "question": "请填写术语",
            "course_id": 7,
            "topic_tags": ["rag"],
            "answer": "检索增强生成",
            "acceptable_variants": [],
            "score": 10,
        }

        is_correct, score = engine.grade_fill(question, "检索增强 生成")

        self.assertGreater(score, 0)
        self.assertIn(is_correct, {True, False})

    def test_grade_fill_does_not_give_full_score_to_nearby_wrong_term(self) -> None:
        skill_dir = REPO_ROOT / "agent-skills" / "prompt-learning"
        with mock.patch.dict(os.environ, TEST_ENV, clear=False):
            engine = ExamEngine(skill_dir=skill_dir, username=TEST_USERNAME)

        question = {
            "type": "fill",
            "num": 6,
            "difficulty": "中级",
            "question": "请填写术语",
            "course_id": 7,
            "topic_tags": ["rag"],
            "answer": "检索增强生成",
            "acceptable_variants": [],
            "score": 10,
        }

        is_correct, score = engine.grade_fill(question, "检索增强生存")

        self.assertFalse(is_correct)
        self.assertLess(score, question["score"])

    def test_finish_diagnostic_session_generates_report_and_history(self) -> None:
        started = run_cli("exam", "--start", "--type", "diagnostic")
        finished = self._complete_exam(started["session_id"], "diagnostic")
        session_file = TEST_WORKSPACE / "exam" / "current-session.json"
        exam_history_path = TEST_WORKSPACE / "exam" / "exam-history.jsonl"
        session = read_json(session_file)
        rows = [
            json.loads(line)
            for line in exam_history_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self._assert_finished_exam(
            finished=finished,
            session=session,
            rows=rows,
            expected_type="diagnostic",
            expected_weak_courses=[2, 3, 4, 5, 7, 8, 10, 11],
            expected_weak_topics=[
                "diagnostic-mc-topic-2",
                "diagnostic-mc-topic-3",
                "diagnostic-mc-topic-4",
                "diagnostic-mc-topic-5",
                "diagnostic-fill-topic-7",
                "diagnostic-fill-topic-8",
                "diagnostic-essay-topic-10",
                "diagnostic-essay-topic-11",
            ],
        )

    def test_finish_final_session_generates_report_and_history(self) -> None:
        started = run_cli("exam", "--start", "--type", "final")
        finished = self._complete_exam(started["session_id"], "final")
        session_file = TEST_WORKSPACE / "exam" / "current-session.json"
        exam_history_path = TEST_WORKSPACE / "exam" / "exam-history.jsonl"
        session = read_json(session_file)
        rows = [
            json.loads(line)
            for line in exam_history_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self._assert_finished_exam(
            finished=finished,
            session=session,
            rows=rows,
            expected_type="final",
            expected_weak_courses=[22, 23, 24, 25, 27, 28, 30, 31],
            expected_weak_topics=[
                "final-mc-topic-2",
                "final-mc-topic-3",
                "final-mc-topic-4",
                "final-mc-topic-5",
                "final-fill-topic-7",
                "final-fill-topic-8",
                "final-essay-topic-10",
                "final-essay-topic-11",
            ],
        )


if __name__ == "__main__":
    unittest.main()
