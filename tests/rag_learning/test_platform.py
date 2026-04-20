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
TEST_USERNAME = "rag-learning-test"
TEST_WORKSPACE = WORKSPACE_ROOT / TEST_USERNAME


def run_cli_for(
    username: str, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args, "--username", username],
        check=check,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def run_cli(*args: str) -> dict:
    result = run_cli_for(TEST_USERNAME, *args)
    return json.loads(result.stdout)


class RagLearningPlatformSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        for username in [
            TEST_USERNAME,
            "rag-learning-new-user",
            "rag-learning-fresh-user",
            "rag-learning-ownership-mismatch",
            "existing-rag-user",
        ]:
            workspace = WORKSPACE_ROOT / username
            if workspace.exists():
                shutil.rmtree(workspace)

    def test_workspace_bootstrap_creates_expected_files(self) -> None:
        learner_file = TEST_WORKSPACE / "profile" / "learner.json"
        current_state_file = TEST_WORKSPACE / "progress" / "current-state.json"
        build_progress_file = TEST_WORKSPACE / "progress" / "build-progress.json"

        self.assertTrue(learner_file.exists())
        self.assertTrue(current_state_file.exists())
        self.assertTrue(build_progress_file.exists())

        learner = json.loads(learner_file.read_text(encoding="utf-8"))
        self.assertEqual(learner["workspace_user"], TEST_USERNAME)

    def test_new_user_entry_bootstraps_own_workspace(self) -> None:
        existing_workspace = WORKSPACE_ROOT / "existing-rag-user"
        existing_workspace.mkdir(parents=True, exist_ok=True)
        new_username = "rag-learning-new-user"
        new_workspace = WORKSPACE_ROOT / new_username
        if new_workspace.exists():
            shutil.rmtree(new_workspace)

        dashboard = json.loads(run_cli_for(new_username, "home", "--dashboard").stdout)

        self.assertEqual(dashboard["module"], "home")
        self.assertTrue(new_workspace.exists())
        self.assertTrue((new_workspace / "profile" / "learner.json").exists())
        self.assertFalse((existing_workspace / "profile" / "learner.json").exists())

    def test_home_recommendation_falls_back_for_fresh_workspace(self) -> None:
        fresh_username = "rag-learning-fresh-user"
        fresh_workspace = WORKSPACE_ROOT / fresh_username
        if fresh_workspace.exists():
            shutil.rmtree(fresh_workspace)

        recommendation = json.loads(
            run_cli_for(fresh_username, "home", "--recommend").stdout
        )
        current_state = json.loads(
            (fresh_workspace / "progress" / "current-state.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(current_state["recommended_next_action"], "open_dashboard")
        self.assertEqual(recommendation["recommended_action"], "continue_learning")
        self.assertNotEqual(recommendation["recommended_action"], "open_dashboard")

    def test_home_resume_falls_back_for_fresh_workspace(self) -> None:
        fresh_username = "rag-learning-fresh-user"
        resume = json.loads(run_cli_for(fresh_username, "home", "--resume").stdout)

        self.assertEqual(resume["resume_action"], "open_dashboard")
        self.assertEqual(resume["target_module"], "home")
        self.assertTrue(resume["is_fallback"])

    def test_workspace_bootstrap_rejects_ownership_mismatch(self) -> None:
        username = "rag-learning-ownership-mismatch"
        workspace = WORKSPACE_ROOT / username
        if workspace.exists():
            shutil.rmtree(workspace)
        (workspace / "profile").mkdir(parents=True, exist_ok=True)
        (workspace / "progress").mkdir(parents=True, exist_ok=True)
        (workspace / "profile" / "learner.json").write_text(
            json.dumps({"workspace_user": "other-user"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (workspace / "progress" / "current-state.json").write_text(
            json.dumps({"current_module": "home"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        result = run_cli_for(username, "workspace", "--bootstrap", check=False)

        self.assertNotEqual(result.returncode, 0)
        error_payload = json.loads(result.stdout)
        self.assertTrue(error_payload.get("error"))
        self.assertEqual(error_payload.get("error_type"), "workspace_mismatch")
        self.assertIn("workspace ownership mismatch", error_payload.get("message", ""))

    def test_home_dashboard_and_learning_catalog(self) -> None:
        dashboard = run_cli("home", "--dashboard")
        self.assertEqual(dashboard["module"], "home")
        self.assertEqual(dashboard["interaction"]["mode"], "selector")
        self.assertIn("question", dashboard)
        self.assertNotIn("question", dashboard["interaction"])
        self.assertEqual(len(dashboard["cards"]), 4)

        catalog = run_cli("learning", "--catalog")
        self.assertEqual(catalog["module"], "learning")
        self.assertEqual(catalog["interaction"]["mode"], "inform")
        self.assertIn("selection", catalog["tracks"])
        self.assertGreaterEqual(len(catalog["courses"]), 12)

        novice_path = run_cli("learning", "--path", "--level", "novice")
        enterprise_path = run_cli("learning", "--path", "--level", "enterprise")
        self.assertEqual(novice_path["interaction"]["mode"], "inform")
        self.assertEqual(enterprise_path["interaction"]["mode"], "inform")
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
        self.assertEqual(panel["interaction"]["mode"], "inform")
        self.assertEqual(panel["step"], "embedding")
        self.assertEqual(panel["next_step"], "vector_db")
        self.assertEqual(panel["handoff"]["recommended_module"], "lab")
        self.assertEqual(panel["handoff"]["recommended_topic"], "embedding")

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
        build_resume = run_cli("build", "--resume")
        self.assertIn(
            "embedding",
            build_progress["projects"]["local-minimum-rag"]["completed_steps"],
        )
        self.assertEqual(build_resume["resume_action"], "continue_build")
        self.assertEqual(build_resume["target_payload"]["project_id"], "local-minimum-rag")
        self.assertEqual(build_resume["target_payload"]["step"], "vector_db")

    def test_build_flow_rejects_unknown_project_id(self) -> None:
        with self.assertRaises(subprocess.CalledProcessError):
            run_cli("build", "--start-project", "--project", "not-a-real-project")

    def test_lab_and_review_flows_record_history(self) -> None:
        lab_entry_points = run_cli("lab", "--entry-points")
        self.assertEqual(lab_entry_points["interaction"]["mode"], "selector")
        self.assertIn("question", lab_entry_points)

        lab_blueprint = run_cli("lab", "--blueprint", "--topic", "embedding")
        self.assertEqual(lab_blueprint["interaction"]["mode"], "inform")
        self.assertEqual(lab_blueprint["topic"], "embedding")
        self.assertIn("handoff_context", lab_blueprint)

        lab_record = run_cli(
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
        self.assertIn("experiment_id", lab_record["result"])
        lab_resume = run_cli("lab", "--resume")
        self.assertEqual(lab_resume["resume_action"], "continue_lab")
        self.assertEqual(lab_resume["target_payload"]["topic"], "embedding")
        lab_history = run_cli("lab", "--history")
        self.assertEqual(lab_history["interaction"]["mode"], "inform")
        self.assertGreaterEqual(lab_history["count"], 1)

        review_entry_points = run_cli("review", "--entry-points")
        self.assertEqual(review_entry_points["interaction"]["mode"], "selector")
        self.assertIn("question", review_entry_points)
        self.assertEqual(
            [option["value"] for option in review_entry_points["question"]["options"]],
            ["start_new_review", "continue_recent_review", "view_review_history"],
        )

        review_template = run_cli(
            "review", "--template", "--scenario", "enterprise-knowledge-search"
        )
        self.assertEqual(review_template["interaction"]["mode"], "inform")
        self.assertEqual(review_template["scenario"], "enterprise-knowledge-search")
        self.assertIn("evidence_handoff", review_template)

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
        self.assertEqual(review_history["interaction"]["mode"], "inform")
        self.assertGreaterEqual(review_history["count"], 1)

        review_entry_points_after = run_cli("review", "--entry-points")
        self.assertEqual(
            review_entry_points_after["recent_review"]["scenario"],
            "enterprise-knowledge-search",
        )

    def test_profile_summary_reflects_recorded_state(self) -> None:
        summary = run_cli("profile", "--summary")
        self.assertEqual(summary["module"], "profile")
        self.assertEqual(summary["interaction"]["mode"], "inform")
        self.assertIn("state_recommendation", summary)
        self.assertIn("stable_preferences", summary)
        self.assertIn("preference_evidence", summary)
        self.assertGreaterEqual(summary["progress"]["active_project_count"], 1)
        self.assertGreaterEqual(summary["progress"]["experiment_count"], 1)
        self.assertGreaterEqual(summary["progress"]["review_count"], 1)

        # active project count 应只统计 in_progress 项目
        build_progress = json.loads(
            (TEST_WORKSPACE / "progress" / "build-progress.json").read_text(
                encoding="utf-8"
            )
        )
        active_projects = [
            pid
            for pid, p in build_progress.get("projects", {}).items()
            if p.get("status") == "in_progress"
        ]
        self.assertEqual(
            summary["progress"]["active_project_count"], len(active_projects)
        )

        # 稳定偏好应来自评审推荐栈（review 在 lab 之后记录，覆盖 embedding）
        prefs = summary["stable_preferences"]
        self.assertIn("embedding", prefs)
        self.assertIn("vector_db", prefs)
        self.assertIn("retrieval", prefs)
        self.assertIn("rerank", prefs)
        self.assertEqual(prefs["embedding"]["value"], "bge-m3")
        self.assertEqual(prefs["vector_db"]["value"], "qdrant")
        self.assertEqual(prefs["retrieval"]["value"], "hybrid")
        self.assertEqual(prefs["rerank"]["value"], "bge-reranker-v2-m3")

        # evidence_count 应反映合并后的证据数
        self.assertEqual(prefs["embedding"]["evidence_count"], 2)
        self.assertEqual(prefs["vector_db"]["evidence_count"], 1)

        # 偏好证据摘要
        evidence = summary["preference_evidence"]
        self.assertGreaterEqual(evidence["lab"], 1)
        self.assertGreaterEqual(evidence["review"], 1)


if __name__ == "__main__":
    unittest.main()
