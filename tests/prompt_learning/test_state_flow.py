from __future__ import annotations

import json
import os
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
TEST_USERNAME = "prompt-learning-state-test"
TEST_WORKSPACE = WORKSPACE_ROOT / TEST_USERNAME
TEST_ENV = {"PROMPT_LEARNING_ALLOW_USERNAME_OVERRIDE": "1"}


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


class PromptLearningStateFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)

    def test_learning_flow_updates_current_state_and_course_progress(self) -> None:
        run_cli("learning", "--lesson-meta", "--course", "4")
        run_cli("learning", "--complete", "--course", "4")

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        course_progress = read_json(TEST_WORKSPACE / "progress" / "course-progress.json")

        self.assertEqual(current_state["current_module"], "learning")
        self.assertEqual(current_state["current_course_id"], 4)
        self.assertEqual(current_state["last_action"], "course_completed")
        self.assertIn(4, course_progress["completed_courses"])
        self.assertEqual(course_progress["last_completed_course"], 4)

    def test_practice_flow_updates_mastery_and_mistakes(self) -> None:
        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 4,
                "course_name": "自我一致性",
                "entry_type": "targeted",
                "question_type": "design",
                "result": "weak",
                "mistake_tags": ["sampling", "consistency"],
                "feedback_summary": "能描述思路，但没有说清采样和投票关系。",
            },
        )

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        mastery = read_json(TEST_WORKSPACE / "progress" / "mastery.json")
        mistakes_path = TEST_WORKSPACE / "practice" / "mistakes.jsonl"
        rows = [
            json.loads(line)
            for line in mistakes_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self.assertEqual(current_state["current_module"], "practice")
        self.assertEqual(current_state["last_action"], "practice_completed")
        self.assertEqual(current_state["recommended_next_action"], "review_mistakes")
        self.assertEqual(mastery["courses"]["4"]["practice_attempts"], 1)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["status"] == "open" for row in rows))

    def test_lab_and_exam_flows_update_state_and_history(self) -> None:
        run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "outline-writer",
                "topic": "writing",
                "slots": {
                    "task": "写提纲",
                    "input": "文章主题",
                    "output_format": "列表",
                    "constraints": "分三层",
                    "quality_bar": "结构清晰",
                },
                "prompt": "请根据主题生成三层提纲",
            },
        )

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        template_index = read_json(TEST_WORKSPACE / "prompt-lab" / "template-index.json")
        self.assertEqual(current_state["current_module"], "lab")
        self.assertEqual(current_state["last_action"], "template_saved")
        self.assertEqual(len(template_index["templates"]), 1)

        run_cli(
            "exam",
            "--record-history",
            stdin_data={
                "exam_type": "final",
                "score": 88,
                "total_score": 100,
                "weak_courses": [10],
                "weak_topics": ["tool-use"],
                "report_path": "/tmp/prompt-learning-final-report.md",
            },
        )

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        exam_history_path = TEST_WORKSPACE / "exam" / "exam-history.jsonl"
        rows = [
            json.loads(line)
            for line in exam_history_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self.assertEqual(current_state["current_module"], "exam")
        self.assertEqual(current_state["last_action"], "exam_completed")
        self.assertEqual(current_state["recommended_next_action"], "review_weak_topics")
        self.assertEqual(rows[-1]["exam_type"], "final")
        self.assertEqual(rows[-1]["score"], 88)


if __name__ == "__main__":
    unittest.main()
