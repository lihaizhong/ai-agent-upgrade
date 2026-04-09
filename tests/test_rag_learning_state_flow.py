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

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        course_progress = read_json(TEST_WORKSPACE / "progress" / "course-progress.json")

        self.assertEqual(current_state["current_module"], "learning")
        self.assertEqual(current_state["current_course_id"], 4)
        self.assertEqual(current_state["last_action"], "lesson_started")
        self.assertEqual(course_progress["in_progress_course"], 4)
        self.assertEqual(course_progress["course_status"]["4"]["status"], "in_progress")

    def test_build_flow_updates_project_and_competency_state(self) -> None:
        run_cli("build", "--start-project", "--project", "local-minimum-rag")
        run_cli(
            "build",
            "--record-step",
            "--project",
            "local-minimum-rag",
            "--step",
            "embedding",
        )

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        build_progress = read_json(TEST_WORKSPACE / "progress" / "build-progress.json")
        competency = read_json(TEST_WORKSPACE / "progress" / "competency.json")

        self.assertEqual(current_state["current_module"], "build")
        self.assertEqual(current_state["current_project"], "local-minimum-rag")
        self.assertEqual(current_state["last_action"], "embedding_completed")
        self.assertIn(
            "embedding",
            build_progress["projects"]["local-minimum-rag"]["completed_steps"],
        )
        self.assertGreaterEqual(
            competency["areas"]["embedding_selection"]["evidence_count"], 1
        )

    def test_lab_flow_updates_state_and_history(self) -> None:
        run_cli("lab", "--blueprint", "--topic", "rerank")
        run_cli(
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

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        history_path = TEST_WORKSPACE / "lab" / "experiment-history.jsonl"
        rows = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(current_state["current_module"], "lab")
        self.assertEqual(current_state["current_lab_topic"], "rerank")
        self.assertEqual(current_state["last_action"], "experiment_completed")
        self.assertEqual(current_state["recommended_next_action"], "return_to_build")
        self.assertEqual(rows[-1]["topic"], "rerank")

    def test_review_flow_updates_state_and_competency(self) -> None:
        run_cli("review", "--template", "--scenario", "customer-support-rag")
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

        current_state = read_json(TEST_WORKSPACE / "progress" / "current-state.json")
        competency = read_json(TEST_WORKSPACE / "progress" / "competency.json")
        history_path = TEST_WORKSPACE / "review" / "review-history.jsonl"
        rows = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(current_state["current_module"], "review")
        self.assertEqual(current_state["current_review_id"], "customer-support-rag")
        self.assertEqual(current_state["last_action"], "review_completed")
        self.assertEqual(current_state["recommended_next_action"], "review_profile")
        self.assertGreaterEqual(
            competency["areas"]["architecture_review"]["evidence_count"], 1
        )
        self.assertEqual(rows[-1]["scenario"], "customer-support-rag")


if __name__ == "__main__":
    unittest.main()
