from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "agent-skills" / "rag-learning" / "scripts" / "__main__.py"
WORKSPACE_ROOT = REPO_ROOT / "rag-learning-workspace"
TEST_USERNAME = "rag-learning-edge-test"
TEST_WORKSPACE = WORKSPACE_ROOT / TEST_USERNAME


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args, "--username", TEST_USERNAME],
        check=check,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def run_json(*args: str, check: bool = True) -> dict:
    result = run_cli(*args, check=check)
    return json.loads(result.stdout)


class RagLearningEdgeCaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)

    def test_build_invalid_project_returns_structured_error(self) -> None:
        result = run_cli("build", "--start-project", "--project", "not-a-project", check=False)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload.get("error"))
        self.assertEqual(payload.get("error_type"), "invalid_project")
        self.assertEqual(payload.get("module"), "build")
        self.assertIn("not-a-project", payload.get("message", ""))

    def test_build_invalid_step_returns_structured_error(self) -> None:
        run_cli("build", "--start-project", "--project", "local-minimum-rag")
        result = run_cli(
            "build", "--record-step", "--project", "local-minimum-rag", "--step", "not-a-step",
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload.get("error"))
        self.assertEqual(payload.get("error_type"), "invalid_step")
        self.assertEqual(payload.get("module"), "build")

    def test_lab_invalid_topic_returns_structured_error(self) -> None:
        result = run_cli("lab", "--blueprint", "--topic", "not-a-topic", check=False)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload.get("error"))
        self.assertEqual(payload.get("error_type"), "unknown_topic")
        self.assertEqual(payload.get("module"), "lab")
        self.assertIn("not-a-topic", payload.get("message", ""))

    def test_review_invalid_scenario_returns_structured_error(self) -> None:
        result = run_cli("review", "--template", "--scenario", "not-a-scenario", check=False)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload.get("error"))
        self.assertEqual(payload.get("error_type"), "unknown_scenario")
        self.assertEqual(payload.get("module"), "review")
        self.assertIn("not-a-scenario", payload.get("message", ""))

    def test_learning_invalid_course_returns_structured_error(self) -> None:
        result = run_cli("learning", "--lesson-meta", "--course", "999", check=False)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload.get("error"))
        self.assertEqual(payload.get("error_type"), "invalid_course")
        self.assertEqual(payload.get("module"), "learning")
        self.assertIn("999", payload.get("message", ""))

    def test_lab_empty_history_returns_empty_items(self) -> None:
        fresh_user = "rag-learning-empty-history"
        fresh_ws = WORKSPACE_ROOT / fresh_user
        if fresh_ws.exists():
            shutil.rmtree(fresh_ws)
        subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "workspace", "--bootstrap", "--username", fresh_user],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "lab", "--history", "--username", fresh_user],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["items"], [])
        if fresh_ws.exists():
            shutil.rmtree(fresh_ws)

    def test_review_empty_history_returns_empty_items(self) -> None:
        fresh_user = "rag-learning-empty-history"
        fresh_ws = WORKSPACE_ROOT / fresh_user
        if fresh_ws.exists():
            shutil.rmtree(fresh_ws)
        subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "workspace", "--bootstrap", "--username", fresh_user],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "review", "--history", "--username", fresh_user],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["items"], [])
        if fresh_ws.exists():
            shutil.rmtree(fresh_ws)

    def test_workspace_ownership_mismatch_returns_structured_error(self) -> None:
        mismatch_user = "rag-learning-edge-mismatch"
        mismatch_ws = WORKSPACE_ROOT / mismatch_user
        if mismatch_ws.exists():
            shutil.rmtree(mismatch_ws)
        (mismatch_ws / "profile").mkdir(parents=True, exist_ok=True)
        (mismatch_ws / "progress").mkdir(parents=True, exist_ok=True)
        (mismatch_ws / "profile" / "learner.json").write_text(
            json.dumps({"workspace_user": "other-user"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (mismatch_ws / "progress" / "current-state.json").write_text(
            json.dumps({"current_module": "home"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "workspace", "--bootstrap", "--username", mismatch_user],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload.get("error"))
        self.assertEqual(payload.get("error_type"), "workspace_mismatch")
        self.assertIn("workspace ownership mismatch", payload.get("message", ""))
        if mismatch_ws.exists():
            shutil.rmtree(mismatch_ws)

    def test_corrupted_state_file_returns_io_error(self) -> None:
        corrupt_user = "rag-learning-edge-corrupt"
        corrupt_ws = WORKSPACE_ROOT / corrupt_user
        if corrupt_ws.exists():
            shutil.rmtree(corrupt_ws)
        subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "workspace", "--bootstrap", "--username", corrupt_user],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        (corrupt_ws / "progress" / "current-state.json").write_text("not-json{{", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "profile", "--summary", "--username", corrupt_user],
            check=False,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(payload.get("error"))
        self.assertEqual(payload.get("error_type"), "io_error")
        self.assertEqual(payload.get("module"), "profile")
        if corrupt_ws.exists():
            shutil.rmtree(corrupt_ws)


if __name__ == "__main__":
    unittest.main()
