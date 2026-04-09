from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "agent-skills" / "rag-learning" / "scripts" / "__main__.py"
WORKSPACE_ROOT = REPO_ROOT / "rag-learning-workspace"
TEST_USERNAME = "rag-learning-test"
TEST_WORKSPACE = WORKSPACE_ROOT / TEST_USERNAME


def run_cli(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args, "--username", TEST_USERNAME],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return json.loads(result.stdout)


class RagLearningPlatformSmokeTest(unittest.TestCase):
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
        build_progress_file = TEST_WORKSPACE / "progress" / "build-progress.json"

        self.assertTrue(learner_file.exists())
        self.assertTrue(current_state_file.exists())
        self.assertTrue(build_progress_file.exists())

        learner = json.loads(learner_file.read_text(encoding="utf-8"))
        self.assertEqual(learner["workspace_user"], TEST_USERNAME)

    def test_home_dashboard_and_learning_catalog(self) -> None:
        dashboard = run_cli("home", "--dashboard")
        self.assertEqual(dashboard["module"], "home")
        self.assertEqual(len(dashboard["cards"]), 4)

        catalog = run_cli("learning", "--catalog")
        self.assertEqual(catalog["module"], "learning")
        self.assertIn("selection", catalog["tracks"])
        self.assertGreaterEqual(len(catalog["courses"]), 12)

        novice_path = run_cli("learning", "--path", "--level", "novice")
        enterprise_path = run_cli("learning", "--path", "--level", "enterprise")
        self.assertEqual([item["id"] for item in novice_path["courses"]], [1, 2, 3, 7])
        self.assertEqual(
            [item["id"] for item in enterprise_path["courses"]], [10, 11, 12]
        )

    def test_build_flow_updates_progress(self) -> None:
        run_cli("build", "--start-project", "--project", "local-minimum-rag")
        panel = run_cli(
            "build",
            "--step-panel",
            "--project",
            "local-minimum-rag",
            "--step",
            "embedding",
        )
        self.assertEqual(panel["step"], "embedding")
        self.assertEqual(panel["next_step"], "vector_db")

        run_cli(
            "build",
            "--record-step",
            "--project",
            "local-minimum-rag",
            "--step",
            "embedding",
        )
        build_progress = json.loads(
            (TEST_WORKSPACE / "progress" / "build-progress.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("embedding", build_progress["projects"]["local-minimum-rag"]["completed_steps"])

    def test_build_flow_rejects_unknown_project_id(self) -> None:
        with self.assertRaises(subprocess.CalledProcessError):
            run_cli("build", "--start-project", "--project", "not-a-real-project")

    def test_lab_and_review_flows_record_history(self) -> None:
        lab_blueprint = run_cli("lab", "--blueprint", "--topic", "embedding")
        self.assertEqual(lab_blueprint["topic"], "embedding")

        run_cli(
            "lab",
            "--record-result",
            "--topic",
            "embedding",
            "--summary",
            "测试语料下 embedding A 更稳。",
            "--recommended-choice",
            "embedding-a",
            "--tradeoff-note",
            "效果更稳，但成本更高。",
        )
        lab_history = run_cli("lab", "--history")
        self.assertGreaterEqual(lab_history["count"], 1)

        review_template = run_cli(
            "review", "--template", "--scenario", "enterprise-knowledge-search"
        )
        self.assertEqual(review_template["scenario"], "enterprise-knowledge-search")

        run_cli(
            "review",
            "--record-summary",
            "--scenario",
            "enterprise-knowledge-search",
            "--constraints-summary",
            "中文为主，10 万级文档，要求私有部署。",
            "--risk-summary",
            "缺少评估标注集。",
            "--recommended-stack",
            json.dumps(
                {
                    "embedding": "bge-m3",
                    "vector_db": "qdrant",
                    "retrieval": "hybrid",
                    "rerank": "bge-reranker-v2-m3",
                },
                ensure_ascii=False,
            ),
        )
        review_history = run_cli("review", "--history")
        self.assertGreaterEqual(review_history["count"], 1)

    def test_profile_summary_reflects_recorded_state(self) -> None:
        summary = run_cli("profile", "--summary")
        self.assertEqual(summary["module"], "profile")
        self.assertGreaterEqual(summary["progress"]["active_project_count"], 1)
        self.assertGreaterEqual(summary["progress"]["experiment_count"], 1)
        self.assertGreaterEqual(summary["progress"]["review_count"], 1)


if __name__ == "__main__":
    unittest.main()
