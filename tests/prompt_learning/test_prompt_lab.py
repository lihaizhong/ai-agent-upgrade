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
WORKSPACE_ROOT = Path(tempfile.mkdtemp(prefix="prompt-learning-lab-workspace-"))
TEST_USERNAME = "prompt-learning-lab-test"
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


class PromptLearningPromptLabTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        if WORKSPACE_ROOT.exists():
            shutil.rmtree(WORKSPACE_ROOT)

    def test_review_checklist_has_six_items(self) -> None:
        checklist = run_cli("lab", "--review-checklist")

        self.assertEqual(checklist["interaction"]["mode"], "inform")
        self.assertEqual(len(checklist["checklist"]), 6)
        self.assertIn("任务目标是否单一明确", checklist["checklist"])
        self.assertIn("是否避免了重复或冲突指令", checklist["checklist"])

    def test_review_checklist_with_topic(self) -> None:
        checklist = run_cli("lab", "--review-checklist", "--topic", "writing")

        self.assertEqual(checklist["topic"], "writing")
        self.assertEqual(len(checklist["checklist"]), 6)

    def test_interview_blueprint_has_five_slots(self) -> None:
        blueprint = run_cli("lab", "--interview-blueprint")

        self.assertEqual(blueprint["interaction"]["mode"], "inform")
        self.assertEqual(len(blueprint["slots"]), 5)

        slot_names = [s["name"] for s in blueprint["slots"]]
        self.assertEqual(slot_names, ["task", "input", "output_format", "constraints", "quality_bar"])

        for slot in blueprint["slots"]:
            self.assertTrue(slot["required"])
            self.assertEqual(slot["interaction"]["mode"], "open_ended")
            self.assertIn("question", slot)

    def test_interview_blueprint_with_topic(self) -> None:
        blueprint = run_cli("lab", "--interview-blueprint", "--topic", "summary")

        self.assertEqual(blueprint["topic"], "summary")

    def test_validate_slots_all_present(self) -> None:
        result = run_cli(
            "lab",
            "--validate-slots",
            stdin_data={
                "task": "写总结",
                "input": "会议纪要",
                "output_format": "JSON",
                "constraints": "只用中文",
                "quality_bar": "字段稳定",
            },
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["missing_slots"], [])
        self.assertEqual(result["empty_slots"], [])

    def test_validate_slots_missing_slots(self) -> None:
        result = run_cli(
            "lab",
            "--validate-slots",
            stdin_data={
                "task": "写总结",
                "input": "会议纪要",
            },
        )

        self.assertFalse(result["valid"])
        self.assertEqual(len(result["missing_slots"]), 3)

    def test_validate_slots_empty_string_slots(self) -> None:
        result = run_cli(
            "lab",
            "--validate-slots",
            stdin_data={
                "task": "   ",
                "input": "会议纪要",
                "output_format": "JSON",
                "constraints": "只用中文",
                "quality_bar": "字段稳定",
            },
        )

        self.assertFalse(result["valid"])
        self.assertIn("task", result["empty_slots"])

    def test_validate_slots_empty_list_and_dict(self) -> None:
        result = run_cli(
            "lab",
            "--validate-slots",
            stdin_data={
                "task": "写总结",
                "input": "会议纪要",
                "output_format": "JSON",
                "constraints": [],
                "quality_bar": {},
            },
        )

        self.assertFalse(result["valid"])
        self.assertIn("constraints", result["empty_slots"])
        self.assertIn("quality_bar", result["empty_slots"])

    def setUp(self) -> None:
        template_index_file = TEST_WORKSPACE / "prompt-lab" / "template-index.json"
        if template_index_file.exists():
            template_index_file.write_text(
                json.dumps({"templates": [], "updated_at": None}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        templates_dir = TEST_WORKSPACE / "prompt-lab" / "templates"
        if templates_dir.exists():
            for f in templates_dir.iterdir():
                f.unlink()

    def test_save_template_success(self) -> None:
        result = run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "test-template",
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

        self.assertTrue(result["saved"])
        self.assertIn("template_id", result)
        self.assertTrue(Path(result["path"]).exists())

        template_index = read_json(TEST_WORKSPACE / "prompt-lab" / "template-index.json")
        self.assertEqual(len(template_index["templates"]), 1)
        self.assertEqual(template_index["templates"][0]["name"], "test-template")

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        self.assertEqual(current_state["last_action"], "template_saved")

    def test_save_template_rejects_blank_name(self) -> None:
        result = run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "   ",
                "topic": "writing",
                "slots": {
                    "task": "写提纲",
                    "input": "文章主题",
                    "output_format": "列表",
                    "constraints": "分三层",
                    "quality_bar": "结构清晰",
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
                "confirmed": True,
            },
        )

        self.assertFalse(result["saved"])
        self.assertTrue(any("name" in err for err in result["errors"]))

    def test_save_template_rejects_missing_slots(self) -> None:
        result = run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "incomplete-template",
                "topic": "writing",
                "slots": {
                    "task": "写提纲",
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
                "confirmed": True,
            },
        )

        self.assertFalse(result["saved"])
        self.assertTrue(any("缺少必填项" in err for err in result["errors"]))

    def test_save_template_rejects_unconfirmed(self) -> None:
        result = run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "unconfirmed-template",
                "topic": "writing",
                "slots": {
                    "task": "写提纲",
                    "input": "文章主题",
                    "output_format": "列表",
                    "constraints": "分三层",
                    "quality_bar": "结构清晰",
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
        self.assertTrue(any("confirmed" in err for err in result["errors"]))

    def test_list_templates_returns_saved_templates(self) -> None:
        run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "list-test-template",
                "topic": "summary",
                "slots": {
                    "task": "写总结",
                    "input": "会议纪要",
                    "output_format": "JSON",
                    "constraints": "只用中文",
                    "quality_bar": "字段稳定",
                },
                "prompt": "请把会议纪要总结成 JSON",
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

        templates = run_cli("lab", "--list-templates")

        self.assertEqual(templates["count"], 1)
        self.assertEqual(len(templates["templates"]), 1)
        self.assertEqual(templates["templates"][0]["name"], "list-test-template")

    def test_list_templates_empty_when_none(self) -> None:
        templates = run_cli("lab", "--list-templates")

        self.assertEqual(templates["count"], 0)
        self.assertEqual(templates["templates"], [])

    def test_multiple_templates_increment_ids(self) -> None:
        for i in range(3):
            result = run_cli(
                "lab",
                "--save-template",
                stdin_data={
                    "name": f"multi-template-{i}",
                    "topic": "writing",
                    "slots": {
                        "task": f"任务{i}",
                        "input": "输入",
                        "output_format": "文本",
                        "constraints": "无",
                        "quality_bar": "合格",
                    },
                    "prompt": f"请完成任务{i}",
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
            self.assertTrue(result["saved"])

        templates = run_cli("lab", "--list-templates")
        self.assertEqual(templates["count"], 3)

        ids = [t["id"] for t in templates["templates"]]
        self.assertEqual(len(set(ids)), 3)

    def test_save_template_with_tags(self) -> None:
        result = run_cli(
            "lab",
            "--save-template",
            stdin_data={
                "name": "tagged-template",
                "topic": "coding",
                "slots": {
                    "task": "写代码",
                    "input": "需求",
                    "output_format": "Python",
                    "constraints": "无",
                    "quality_bar": "可运行",
                },
                "prompt": "请根据需求写 Python 代码",
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
                "tags": ["python", "code-generation"],
            },
        )

        self.assertTrue(result["saved"])
        template_index = read_json(TEST_WORKSPACE / "prompt-lab" / "template-index.json")
        self.assertEqual(template_index["templates"][-1]["tags"], ["python", "code-generation"])


if __name__ == "__main__":
    unittest.main()
