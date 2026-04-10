from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
import importlib.util


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT / "agent-skills" / "prompt-learning" / "scripts" / "__main__.py"
)
WORKSPACE_ROOT = REPO_ROOT / "prompt-learning-workspace"
TEST_USERNAME = "prompt-learning-test"
TEST_WORKSPACE = WORKSPACE_ROOT / TEST_USERNAME
OTHER_USERNAME = "lihzsky"
OTHER_WORKSPACE = WORKSPACE_ROOT / OTHER_USERNAME
TEST_ENV = {"PROMPT_LEARNING_ALLOW_USERNAME_OVERRIDE": "1"}

spec = importlib.util.spec_from_file_location(
    "prompt_learning_workspace", REPO_ROOT / "agent-skills" / "prompt-learning" / "scripts" / "workspace.py"
)
if spec is None or spec.loader is None:
    raise ImportError("Cannot load prompt-learning workspace module")
workspace_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = workspace_module
spec.loader.exec_module(workspace_module)


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


def run_cli_for(username: str, *args: str, stdin_data: dict | list | None = None) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args, "--username", username],
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


def run_cli_error_for(
    username: str,
    *args: str,
    stdin_data: dict | list | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CalledProcessError:
    with unittest.TestCase().assertRaises(subprocess.CalledProcessError) as ctx:
        subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args, "--username", username],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, **TEST_ENV, **(extra_env or {})},
            input=(
                None
                if stdin_data is None
                else json.dumps(stdin_data, ensure_ascii=False)
            ),
        )
    return ctx.exception


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
        if OTHER_WORKSPACE.exists():
            shutil.rmtree(OTHER_WORKSPACE)

    def test_workspace_bootstrap_creates_expected_files(self) -> None:
        learner_file = TEST_WORKSPACE / "profile" / "learner.json"
        current_state_file = TEST_WORKSPACE / "progress" / "current-state.json"
        template_index_file = TEST_WORKSPACE / "prompt-lab" / "template-index.json"

        self.assertTrue(learner_file.exists())
        self.assertTrue(current_state_file.exists())
        self.assertTrue(template_index_file.exists())

        learner = json.loads(learner_file.read_text(encoding="utf-8"))
        self.assertEqual(learner["workspace_user"], TEST_USERNAME)

    def test_workspace_resolve_user_prefers_explicit_username(self) -> None:
        resolved = run_cli_for("baitanggao", "workspace", "--resolve-user")

        self.assertEqual(resolved["explicit_username"], "baitanggao")
        self.assertEqual(resolved["workspace_user"], "baitanggao")

    def test_rejects_explicit_username_that_conflicts_with_git_identity(self) -> None:
        error = run_cli_error_for(
            "baitanggao",
            "workspace",
            "--resolve-user",
            extra_env={
                "PROMPT_LEARNING_ALLOW_USERNAME_OVERRIDE": "0",
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "user.name",
                "GIT_CONFIG_VALUE_0": "lihzsky",
            },
        )

        self.assertIn("workspace identity mismatch", error.stderr)

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

    def test_new_user_bootstrap_does_not_fallback_to_existing_workspace(self) -> None:
        if OTHER_WORKSPACE.exists():
            shutil.rmtree(OTHER_WORKSPACE)
        other_paths = workspace_module.get_workspace_paths(
            REPO_ROOT / "agent-skills" / "prompt-learning", username=OTHER_USERNAME
        )
        other_paths["learner_file"].parent.mkdir(parents=True, exist_ok=True)
        other_paths["learner_file"].write_text(
            json.dumps(
                {
                    "workspace_user": OTHER_USERNAME,
                    "source_git_username": OTHER_USERNAME,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        baitanggao = run_cli_for("baitanggao", "workspace", "--bootstrap")

        self.assertEqual(baitanggao["workspace_user"], "baitanggao")
        self.assertEqual(
            baitanggao["workspace_root"],
            str(WORKSPACE_ROOT / "baitanggao"),
        )
        self.assertTrue((WORKSPACE_ROOT / "baitanggao" / "profile" / "learner.json").exists())
        self.assertTrue(other_paths["learner_file"].exists())

        shutil.rmtree(WORKSPACE_ROOT / "baitanggao")

    def test_bootstrap_rejects_conflicting_workspace_metadata(self) -> None:
        conflicting_workspace = WORKSPACE_ROOT / "baitanggao"
        if conflicting_workspace.exists():
            shutil.rmtree(conflicting_workspace)
        learner_file = conflicting_workspace / "profile" / "learner.json"
        learner_file.parent.mkdir(parents=True, exist_ok=True)
        learner_file.write_text(
            json.dumps(
                {
                    "workspace_user": "lihzsky",
                    "source_git_username": "lihzsky",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        error = run_cli_error_for("baitanggao", "workspace", "--bootstrap")

        self.assertIn("workspace ownership mismatch", error.stderr)
        shutil.rmtree(conflicting_workspace)

    def test_bootstrap_rejects_non_empty_workspace_without_metadata(self) -> None:
        conflicting_workspace = WORKSPACE_ROOT / "baitanggao"
        if conflicting_workspace.exists():
            shutil.rmtree(conflicting_workspace)
        state_file = conflicting_workspace / "progress" / "current-state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(
            json.dumps({"current_module": "exam"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        error = run_cli_error_for("baitanggao", "workspace", "--bootstrap")

        self.assertIn("workspace metadata missing", error.stderr)
        shutil.rmtree(conflicting_workspace)

    def test_home_entry_also_rejects_conflicting_workspace_metadata(self) -> None:
        conflicting_workspace = WORKSPACE_ROOT / "baitanggao"
        if conflicting_workspace.exists():
            shutil.rmtree(conflicting_workspace)
        learner_file = conflicting_workspace / "profile" / "learner.json"
        learner_file.parent.mkdir(parents=True, exist_ok=True)
        learner_file.write_text(
            json.dumps(
                {
                    "workspace_user": "lihzsky",
                    "source_git_username": "lihzsky",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        error = run_cli_error_for("baitanggao", "home", "--dashboard")

        self.assertIn("workspace ownership mismatch", error.stderr)
        shutil.rmtree(conflicting_workspace)

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
