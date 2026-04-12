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
WORKSPACE_ROOT = Path(tempfile.mkdtemp(prefix="prompt-learning-state-workspace-"))
TEST_USERNAME = "prompt-learning-state-test"
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


class PromptLearningStateFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        if WORKSPACE_ROOT.exists():
            shutil.rmtree(WORKSPACE_ROOT)

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
            if json.loads(line).get("course_id") == 4
        ]

        self.assertEqual(current_state["current_module"], "practice")
        self.assertEqual(current_state["last_action"], "practice_completed")
        self.assertEqual(current_state["recommended_next_action"], "review_mistakes")
        self.assertEqual(mastery["courses"]["4"]["practice_attempts"], 1)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["status"] == "open" for row in rows))

        recommendation = run_cli("home", "--recommend")
        self.assertEqual(recommendation["action"], "review_mistakes")

    def test_mistake_review_reduces_mastery_mistake_count(self) -> None:
        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 5,
                "course_name": "思维树",
                "entry_type": "targeted",
                "question_type": "diagnose",
                "result": "weak",
                "mistake_tags": ["sampling", "consistency"],
                "feedback_summary": "第一次练习仍有两个关键错误。",
            },
        )

        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 5,
                "course_name": "思维树",
                "entry_type": "mistake",
                "question_type": "diagnose",
                "result": "good",
                "resolved_mistake_tags": ["sampling", "consistency"],
                "feedback_summary": "这次已经修正历史错误。",
            },
        )

        mastery = read_json(TEST_WORKSPACE / "progress" / "mastery.json")
        mistakes_path = TEST_WORKSPACE / "practice" / "mistakes.jsonl"
        rows = [
            json.loads(line)
            for line in mistakes_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
            if json.loads(line).get("course_id") == 5
        ]

        self.assertEqual(mastery["courses"]["5"]["practice_attempts"], 2)
        self.assertEqual(mastery["courses"]["5"]["mistake_count"], 0)
        self.assertEqual(mastery["courses"]["5"]["level"], "good")
        self.assertTrue(all(row["status"] == "resolved" for row in rows))

    def test_partial_mistake_review_keeps_review_mistakes_recommendation(self) -> None:
        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 6,
                "course_name": "生成知识提示",
                "entry_type": "targeted",
                "question_type": "diagnose",
                "result": "weak",
                "mistake_tags": ["context", "coverage"],
                "feedback_summary": "存在两个未解决错误。",
            },
        )

        run_cli(
            "practice",
            "--record-result",
            stdin_data={
                "course_id": 6,
                "course_name": "生成知识提示",
                "entry_type": "mistake",
                "question_type": "diagnose",
                "result": "good",
                "resolved_mistake_tags": ["context"],
                "feedback_summary": "这次只修正了其中一个历史错误。",
            },
        )

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        mastery = read_json(TEST_WORKSPACE / "progress" / "mastery.json")
        recommendation = run_cli("home", "--recommend")

        self.assertEqual(mastery["courses"]["6"]["mistake_count"], 1)
        self.assertEqual(current_state["recommended_next_action"], "review_mistakes")
        self.assertEqual(recommendation["action"], "review_mistakes")

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
                "review": {
                    "任务目标是否单一明确": "pass",
                    "输入信息是否定义清楚": "pass",
                    "输出格式是否可直接判定": "pass",
                    "约束条件是否可执行": "pass",
                    "是否明确了失败或边界处理方式": "pass",
                    "是否避免了重复或冲突指令": "pass",
                },
                "revisions": [],
                "confirmed": True,
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

        recommendation = run_cli("home", "--recommend")
        self.assertEqual(recommendation["action"], "review_weak_topics")

    def test_exam_history_without_weaknesses_returns_to_dashboard(self) -> None:
        run_cli(
            "exam",
            "--record-history",
            stdin_data={
                "exam_type": "final",
                "score": 100,
                "total_score": 100,
                "weak_courses": [],
                "weak_topics": [],
                "report_path": "/tmp/prompt-learning-perfect-report.md",
            },
        )

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        recommendation = run_cli("home", "--recommend")

        self.assertEqual(current_state["current_module"], "exam")
        self.assertEqual(current_state["last_action"], "exam_completed")
        self.assertEqual(current_state["recommended_next_action"], "open_dashboard")
        self.assertEqual(recommendation["action"], "continue_learning")
        self.assertNotEqual(recommendation["action"], "open_dashboard")

    def test_lab_save_template_requires_validation_and_confirmation(self) -> None:
        result = run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "unsafe-template",
                "topic": "writing",
                "slots": {
                    "task": "写提纲",
                    "input": "文章主题",
                    "output_format": "列表",
                    "constraints": "分三层",
                },
                "prompt": "请生成提纲",
                "review": {
                    "任务目标是否单一明确": "pass",
                    "输入信息是否定义清楚": "pass",
                    "输出格式是否可直接判定": "pass",
                    "约束条件是否可执行": "pass",
                    "是否明确了失败或边界处理方式": "pass",
                    "是否避免了重复或冲突指令": "pass",
                },
                "revisions": [],
                "confirmed": False,
            },
        )

        self.assertFalse(result["saved"])
        self.assertTrue(result["errors"])

    def test_lab_save_template_rejects_failed_review_items(self) -> None:
        result = run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "failed-review-template",
                "topic": "writing",
                "slots": {
                    "task": "写提纲",
                    "input": "文章主题",
                    "output_format": "列表",
                    "constraints": "分三层",
                    "quality_bar": "结构清晰",
                },
                "prompt": "请根据主题生成三层提纲",
                "review": {
                    "任务目标是否单一明确": "fail",
                    "输入信息是否定义清楚": "pass",
                    "输出格式是否可直接判定": "pass",
                    "约束条件是否可执行": "pass",
                    "是否明确了失败或边界处理方式": "pass",
                    "是否避免了重复或冲突指令": "pass",
                },
                "revisions": ["补充任务边界，但尚未重新审查通过。"],
                "confirmed": True,
            },
        )

        self.assertFalse(result["saved"])
        self.assertTrue(result["errors"])

    def test_lab_rejects_blank_string_slots(self) -> None:
        slot_validation = run_cli(
            "lab",
            "--validate-slots",
            "--topic",
            "writing",
            stdin_data={
                "task": "   ",
                "input": "文章主题",
                "output_format": "列表",
                "constraints": "分三层",
                "quality_bar": "结构清晰",
            },
        )
        save_result = run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "blank-slot-template",
                "topic": "writing",
                "slots": {
                    "task": "   ",
                    "input": "文章主题",
                    "output_format": "列表",
                    "constraints": "分三层",
                    "quality_bar": "结构清晰",
                },
                "prompt": "请根据主题生成三层提纲",
                "review": {
                    "任务目标是否单一明确": "pass",
                    "输入信息是否定义清楚": "pass",
                    "输出格式是否可直接判定": "pass",
                    "约束条件是否可执行": "pass",
                    "是否明确了失败或边界处理方式": "pass",
                    "是否避免了重复或冲突指令": "pass",
                },
                "revisions": [],
                "confirmed": True,
            },
        )

        self.assertFalse(slot_validation["valid"])
        self.assertIn("task", slot_validation["empty_slots"])
        self.assertFalse(save_result["saved"])
        self.assertTrue(save_result["errors"])


if __name__ == "__main__":
    unittest.main()
