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
TEST_USERNAME = "rag-learning-state-test"
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


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class RagLearningStateFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)
        run_cli("workspace", "--bootstrap")

    @classmethod
    def tearDownClass(cls) -> None:
        if TEST_WORKSPACE.exists():
            shutil.rmtree(TEST_WORKSPACE)

    def test_learning_start_updates_current_state_and_course_progress(self) -> None:
        run_cli("learning", "--lesson-meta", "--course", "4")
        home_resume = run_cli("home", "--resume")

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        course_progress = read_json(TEST_WORKSPACE / "progress" / "course-progress.json")

        self.assertEqual(current_state["current_module"], "learning")
        self.assertEqual(current_state["current_course_id"], 4)
        self.assertEqual(current_state["last_action"], "lesson_started")
        self.assertEqual(course_progress["in_progress_course"], 4)
        self.assertEqual(course_progress["course_status"]["4"]["status"], "in_progress")
        self.assertEqual(home_resume["resume_action"], "continue_learning")
        self.assertEqual(home_resume["target_module"], "learning")
        self.assertEqual(home_resume["target_payload"]["course_id"], 4)

    def test_build_flow_updates_project_and_competency_state(self) -> None:
        run_cli("build", "--start-project", "--project", "local-minimum-rag")
        step_record = run_cli(
            "build",
            "--record-step",
            "--project",
            "local-minimum-rag",
            "--step",
            "embedding",
        )
        home_resume = run_cli("home", "--resume")
        build_resume = run_cli("build", "--resume")

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        build_progress = read_json(TEST_WORKSPACE / "progress" / "build-progress.json")
        competency = read_json(TEST_WORKSPACE / "progress" / "competency.json")

        self.assertEqual(current_state["current_module"], "build")
        self.assertEqual(current_state["current_project"], "local-minimum-rag")
        self.assertEqual(current_state["last_action"], "embedding_completed")
        self.assertEqual(step_record["handoff"]["recommended_topic"], "embedding")
        self.assertIn(
            "embedding",
            build_progress["projects"]["local-minimum-rag"]["completed_steps"],
        )
        self.assertGreaterEqual(
            competency["areas"]["embedding_selection"]["evidence_count"], 1
        )
        self.assertEqual(home_resume["resume_action"], "continue_build")
        self.assertEqual(build_resume["target_payload"]["step"], "vector_db")

    def test_lab_flow_updates_state_and_history(self) -> None:
        run_cli("lab", "--blueprint", "--topic", "rerank")
        record = run_cli(
            "lab",
            "--record-result",
            "--topic",
            "rerank",
            "--summary",
            "当前阶段基础召回已足够，暂不引入 rerank。",
            "--recommended-choice",
            "without-rerank",
            "--tradeoff-note",
            "精度提升有限，但延迟与成本会增加。",
        )
        home_resume = run_cli("home", "--resume")
        lab_resume = run_cli("lab", "--resume")

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        history_path = TEST_WORKSPACE / "lab" / "experiment-history.jsonl"
        rows = [
            json.loads(line)
            for line in history_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self.assertEqual(current_state["current_module"], "lab")
        self.assertEqual(current_state["current_lab_topic"], "rerank")
        self.assertEqual(current_state["last_action"], "experiment_completed")
        self.assertEqual(current_state["recommended_next_action"], "return_to_build")
        self.assertEqual(record["result"]["handoff_context"]["project_id"], "local-minimum-rag")
        self.assertTrue(record["result"]["experiment_id"].startswith("rerank-"))
        self.assertEqual(rows[-1]["topic"], "rerank")
        self.assertEqual(home_resume["resume_action"], "continue_lab")
        self.assertEqual(lab_resume["target_payload"]["topic"], "rerank")

    def test_review_flow_updates_state_and_competency(self) -> None:
        template = run_cli("review", "--template", "--scenario", "customer-support-rag")
        run_cli(
            "review",
            "--record-summary",
            "--scenario",
            "customer-support-rag",
            "--constraints-summary",
            "中文客服，多轮对话，预算中等。",
            "--risk-summary",
            "知识更新频率高，缺少标准评估集。",
            "--recommended-stack",
            json.dumps(
                {
                    "embedding": "text-embedding-3-small",
                    "vector_db": "qdrant",
                    "retrieval": "vector-plus-metadata",
                    "rerank": "conditional",
                },
                ensure_ascii=False,
            ),
        )
        home_resume = run_cli("home", "--resume")
        review_entry_points = run_cli("review", "--entry-points")

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        competency = read_json(TEST_WORKSPACE / "progress" / "competency.json")
        history_path = TEST_WORKSPACE / "review" / "review-history.jsonl"
        rows = [
            json.loads(line)
            for line in history_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self.assertEqual(current_state["current_module"], "review")
        self.assertEqual(current_state["current_review_id"], "customer-support-rag")
        self.assertEqual(current_state["last_action"], "review_completed")
        self.assertEqual(current_state["recommended_next_action"], "review_profile")
        self.assertGreaterEqual(
            len(template["evidence_handoff"]["recent_experiments"]), 1
        )
        self.assertGreaterEqual(
            competency["areas"]["architecture_review"]["evidence_count"], 1
        )
        self.assertEqual(rows[-1]["scenario"], "customer-support-rag")
        self.assertEqual(home_resume["resume_action"], "continue_review")
        self.assertEqual(
            review_entry_points["recent_review"]["scenario"], "customer-support-rag"
        )

    def test_preference_rollup_after_lab_and_review(self) -> None:
        run_cli("lab", "--blueprint", "--topic", "embedding")
        run_cli(
            "lab",
            "--record-result",
            "--topic",
            "embedding",
            "--summary",
            "中文语料下 bge-m3 更稳。",
            "--recommended-choice",
            "bge-m3",
            "--tradeoff-note",
            "效果更稳，但成本更高。",
        )
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

        preferences = read_json(TEST_WORKSPACE / "profile" / "preferences.json")
        stable = preferences.get("stable_preferences", {})

        self.assertIn("embedding", stable)
        self.assertIn("vector_db", stable)
        self.assertIn("retrieval", stable)
        self.assertIn("rerank", stable)
        self.assertEqual(stable["embedding"]["value"], "bge-m3")
        self.assertEqual(stable["vector_db"]["value"], "qdrant")
        self.assertEqual(stable["retrieval"]["value"], "hybrid")
        self.assertEqual(stable["rerank"]["value"], "bge-reranker-v2-m3")
        self.assertEqual(stable["embedding"]["evidence_count"], 2)
        self.assertEqual(stable["vector_db"]["evidence_count"], 1)
        self.assertEqual(preferences["evidence_summary"]["lab"], 2)
        self.assertEqual(preferences["evidence_summary"]["review"], 4)
        self.assertIsNotNone(preferences["updated_at"])

    def test_home_recommendation_consumes_neutral_state_as_fallback(self) -> None:
        current_state_file = TEST_WORKSPACE / "progress" / "current-state.json"
        current_state = read_json(current_state_file)
        current_state["recommended_next_action"] = "open_dashboard"
        current_state["current_module"] = "home"
        current_state["last_action"] = "workspace_initialized"
        current_state_file.write_text(
            json.dumps(current_state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        recommendation = run_cli("home", "--recommend")
        profile_summary = run_cli("profile", "--summary")

        self.assertEqual(
            read_json(current_state_file)["recommended_next_action"], "open_dashboard"
        )
        self.assertEqual(recommendation["recommended_action"], "continue_build")
        self.assertNotEqual(recommendation["recommended_action"], "open_dashboard")
        self.assertEqual(
            profile_summary["state_recommendation"]["action"], "open_dashboard"
        )


if __name__ == "__main__":
    unittest.main()
