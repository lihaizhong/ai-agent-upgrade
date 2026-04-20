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
WORKSPACE_ROOT = Path(tempfile.mkdtemp(prefix="prompt-learning-practice-workspace-"))
TEST_USERNAME = "prompt-learning-practice-test"
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


class PromptLearningPracticeCenterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        if WORKSPACE_ROOT.exists():
            shutil.rmtree(WORKSPACE_ROOT)

    def test_entry_points_returns_selector(self) -> None:
        entry = run_cli("practice", "--entry-points")

        self.assertEqual(entry["interaction"]["mode"], "selector")
        self.assertEqual(entry["question"]["header"], "练习中心")
        self.assertEqual(len(entry["question"]["options"]), 3)

        values = [opt["value"] for opt in entry["question"]["options"]]
        self.assertEqual(values, ["current", "targeted", "mistake"])

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
        mistakes_file = TEST_WORKSPACE / "practice" / "mistakes.jsonl"
        if mistakes_file.exists():
            mistakes_file.unlink()
        history_file = TEST_WORKSPACE / "practice" / "practice-history.jsonl"
        if history_file.exists():
            history_file.unlink()

    def test_resume_target_with_current_course(self) -> None:
        run_cli("learning", "--lesson-meta", "--course", "4")
        resume = run_cli("practice", "--resume")

        self.assertEqual(resume["entry_type"], "current")
        self.assertEqual(resume["course_id"], 4)
        self.assertEqual(resume["course_name"], "自我一致性")

    def test_resume_target_without_current_course(self) -> None:
        resume = run_cli("practice", "--resume")

        self.assertEqual(resume["entry_type"], "targeted")
        self.assertIsNone(resume["course_id"])

    def test_blueprint_current_mode(self) -> None:
        run_cli("learning", "--lesson-meta", "--course", "3")
        blueprint = run_cli("practice", "--blueprint", "--mode", "current")

        self.assertEqual(blueprint["mode"], "current")
        self.assertEqual(blueprint["course_id"], 3)
        self.assertEqual(blueprint["course_name"], "思维链提示")
        self.assertEqual(blueprint["question_type"], "diagnose")
        self.assertIn("constraints", blueprint)
        self.assertIn("response_schema", blueprint)

    def test_blueprint_targeted_mode(self) -> None:
        blueprint = run_cli("practice", "--blueprint", "--mode", "targeted", "--course", "10")

        self.assertEqual(blueprint["mode"], "targeted")
        self.assertEqual(blueprint["course_id"], 10)
        self.assertEqual(blueprint["course_name"], "程序辅助语言模型")
        self.assertEqual(blueprint["question_type"], "design")

    def test_blueprint_mistake_mode(self) -> None:
        blueprint = run_cli("practice", "--blueprint", "--mode", "mistake", "--course", "5")

        self.assertEqual(blueprint["mode"], "mistake")
        self.assertEqual(blueprint["question_type"], "diagnose")
        self.assertIn("围绕历史错误模式", blueprint["goal"])

    def test_blueprint_question_type_mapping(self) -> None:
        test_cases = [
            (1, "diagnose"),
            (3, "diagnose"),
            (4, "design"),
            (8, "design"),
            (12, "compare"),
            (14, "compare"),
            (15, "compose"),
            (17, "compose"),
        ]
        for course_id, expected_type in test_cases:
            with self.subTest(course_id=course_id):
                blueprint = run_cli("practice", "--blueprint", "--mode", "targeted", "--course", str(course_id))
                self.assertEqual(blueprint["question_type"], expected_type)

    def test_blueprint_rejects_invalid_mode(self) -> None:
        error = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "practice", "--blueprint", "--mode", "invalid", "--username", TEST_USERNAME],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, **TEST_ENV},
        )

        self.assertNotEqual(error.returncode, 0)
        self.assertIn("invalid choice", error.stderr)

    def test_blueprint_current_mode_requires_course(self) -> None:
        error = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "practice", "--blueprint", "--mode", "current", "--username", TEST_USERNAME],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, **TEST_ENV},
        )

        self.assertNotEqual(error.returncode, 0)
        self.assertIn("必须提供课程编号", error.stderr)

    def test_record_result_creates_history_and_mistakes(self) -> None:
        result = run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 3,
                "course_name": "思维链提示",
                "entry_type": "targeted",
                "question_type": "diagnose",
                "result": "weak",
                "mistake_tags": ["clarity", "structure"],
                "strength_tags": [],
                "feedback_summary": "概念理解不清，结构混乱。",
            },
        )

        self.assertTrue(result["recorded"])
        self.assertEqual(result["written_mistakes"], 2)
        self.assertEqual(result["resolved_mistakes"], 0)

        history_path = TEST_WORKSPACE / "practice" / "practice-history.jsonl"
        self.assertTrue(history_path.exists())

        mistakes_path = TEST_WORKSPACE / "practice" / "mistakes.jsonl"
        self.assertTrue(mistakes_path.exists())

        mastery = read_json(TEST_WORKSPACE / "progress" / "mastery.json")
        self.assertEqual(mastery["courses"]["3"]["mistake_count"], 2)

    def test_record_result_good_does_not_write_mistakes(self) -> None:
        result = run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 3,
                "course_name": "思维链提示",
                "entry_type": "targeted",
                "question_type": "diagnose",
                "result": "good",
                "mistake_tags": [],
                "feedback_summary": "完全正确。",
            },
        )

        self.assertTrue(result["recorded"])
        self.assertEqual(result["written_mistakes"], 0)

    def test_record_result_resolves_mistakes_on_good_mistake_entry(self) -> None:
        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 5,
                "course_name": "思维树",
                "entry_type": "targeted",
                "question_type": "diagnose",
                "result": "weak",
                "mistake_tags": ["branching", "evaluation"],
                "feedback_summary": "第一次练习有错误。",
            },
        )

        result = run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 5,
                "course_name": "思维树",
                "entry_type": "mistake",
                "question_type": "diagnose",
                "result": "good",
                "resolved_mistake_tags": ["branching", "evaluation"],
                "feedback_summary": "错题回练已修正。",
            },
        )

        self.assertTrue(result["recorded"])
        self.assertEqual(result["resolved_mistakes"], 2)

        mastery = read_json(TEST_WORKSPACE / "progress" / "mastery.json")
        self.assertEqual(mastery["courses"]["5"]["mistake_count"], 0)

    def test_record_result_rejects_invalid_result(self) -> None:
        error = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "practice", "--record-result", "--username", TEST_USERNAME],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, **TEST_ENV},
            input=json.dumps({
                "course_id": 1,
                "result": "invalid",
            }, ensure_ascii=False),
        )

        self.assertNotEqual(error.returncode, 0)
        self.assertIn("result 必须是", error.stderr)

    def test_list_open_mistakes_returns_unresolved_items(self) -> None:
        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 6,
                "course_name": "生成知识提示",
                "entry_type": "targeted",
                "question_type": "diagnose",
                "result": "weak",
                "mistake_tags": ["coverage"],
                "feedback_summary": "覆盖不足。",
            },
        )

        mistakes = run_cli("practice", "--review-mistakes")

        self.assertGreater(mistakes["count"], 0)
        self.assertTrue(all(item["status"] == "open" for item in mistakes["items"]))

    def test_list_open_mistakes_empty_when_none(self) -> None:
        mistakes = run_cli("practice", "--review-mistakes", "--course", "99")

        self.assertEqual(mistakes["count"], 0)
        self.assertEqual(mistakes["items"], [])

    def test_practice_summary_recommends_mistake_when_open(self) -> None:
        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 7,
                "course_name": "检索增强生成",
                "entry_type": "targeted",
                "question_type": "diagnose",
                "result": "weak",
                "mistake_tags": ["retrieval"],
                "feedback_summary": "检索策略有误。",
            },
        )

        summary = run_cli("practice", "--summary")

        self.assertEqual(summary["recommended_entry"], "mistake")
        self.assertGreater(summary["open_mistake_count"], 0)

    def test_practice_summary_recommends_current_when_no_mistakes(self) -> None:
        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 8,
                "course_name": "提示词链",
                "entry_type": "targeted",
                "question_type": "diagnose",
                "result": "good",
                "feedback_summary": "完全正确。",
            },
        )

        summary = run_cli("practice", "--summary")

        self.assertEqual(summary["recommended_entry"], "current")
        self.assertEqual(summary["open_mistake_count"], 0)


if __name__ == "__main__":
    unittest.main()
