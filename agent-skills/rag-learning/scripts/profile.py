"""
RAG Learning 学习档案模块。
负责聚合当前进度、实验历史、评审历史、能力摘要和稳定偏好。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    from state import RagLearningStateStore
    from workspace import get_workspace_paths
else:
    from .state import RagLearningStateStore
    from .workspace import get_workspace_paths


class ProfileService:
    def __init__(self, skill_dir: Path, username: str | None = None):
        self.skill_dir = skill_dir
        self.workspace_paths = get_workspace_paths(skill_dir, username=username)
        self.state = RagLearningStateStore(self.workspace_paths)

    def _read_jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def _load_json(self, path: Path, default: dict) -> dict:
        if not path.exists():
            return default.copy()
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def _timestamp(self) -> str:
        return datetime.now().astimezone().isoformat()

    def _extract_lab_preferences(self, experiments: list[dict]) -> list[dict]:
        """从实验历史提取偏好证据。"""
        topic_to_key = {
            "embedding": "embedding",
            "rerank": "rerank",
            "chunking": "chunking",
        }
        prefs: list[dict] = []
        for row in experiments:
            topic = row.get("topic")
            key = topic_to_key.get(topic)
            if key is None:
                continue
            ts = row.get("timestamp", "")
            choice = row.get("recommended_choice")
            if not choice:
                continue
            prefs.append(
                {
                    "key": key,
                    "value": choice,
                    "source": "lab",
                    "timestamp": ts,
                    "topic": topic,
                }
            )
        return prefs

    def _extract_review_preferences(self, reviews: list[dict]) -> list[dict]:
        """从评审历史提取偏好证据。"""
        prefs: list[dict] = []
        for row in reviews:
            stack = row.get("recommended_stack") or {}
            ts = row.get("timestamp", "")
            for key, value in stack.items():
                if not value:
                    continue
                prefs.append(
                    {
                        "key": key,
                        "value": value,
                        "source": "review",
                        "timestamp": ts,
                        "scenario": row.get("scenario"),
                    }
                )
        return prefs

    def _aggregate_preferences(self, evidence: list[dict]) -> dict:
        """按最近证据优先聚合稳定偏好。"""
        by_key: dict[str, list[dict]] = {}
        for item in evidence:
            by_key.setdefault(item["key"], []).append(item)

        stable: dict[str, dict] = {}
        for key, items in by_key.items():
            sorted_items = sorted(items, key=lambda x: x["timestamp"])
            latest = sorted_items[-1]
            stable[key] = {
                "value": latest["value"],
                "source": latest["source"],
                "evidence_count": len(sorted_items),
                "last_evidence_at": latest["timestamp"],
            }
        return stable

    def update_preferences(self) -> dict:
        """从实验与评审历史聚合稳定偏好并回写 preferences.json。"""
        experiments = self._read_jsonl(
            self.workspace_paths["experiment_history_file"]
        )
        reviews = self._read_jsonl(self.workspace_paths["review_history_file"])

        lab_evidence = self._extract_lab_preferences(experiments)
        review_evidence = self._extract_review_preferences(reviews)
        all_evidence = lab_evidence + review_evidence

        stable = self._aggregate_preferences(all_evidence)
        payload = {
            "stable_preferences": stable,
            "evidence_summary": {
                "lab": len(lab_evidence),
                "review": len(review_evidence),
            },
            "updated_at": self._timestamp(),
        }

        self._save_json(self.workspace_paths["preferences_file"], payload)
        return payload

    def get_preferences(self) -> dict:
        """读取 preferences.json，不存在时返回空结构。"""
        return self._load_json(
            self.workspace_paths["preferences_file"],
            {
                "stable_preferences": {},
                "evidence_summary": {"lab": 0, "review": 0},
                "updated_at": None,
            },
        )

    def progress(self) -> dict:
        return {
            "module": "profile",
            "interaction": {"mode": "inform"},
            "current_state": self.state.get_current_state(),
            "course_progress": self.state.get_course_progress(),
            "build_progress": self.state.get_build_progress(),
            "competency": self.state.get_competency(),
        }

    def experiments(self) -> dict:
        rows = self._read_jsonl(self.workspace_paths["experiment_history_file"])
        return {
            "module": "profile",
            "interaction": {"mode": "inform"},
            "count": len(rows),
            "items": list(reversed(rows[-10:])),
        }

    def reviews(self) -> dict:
        rows = self._read_jsonl(self.workspace_paths["review_history_file"])
        return {
            "module": "profile",
            "interaction": {"mode": "inform"},
            "count": len(rows),
            "items": list(reversed(rows[-10:])),
        }

    def summary(self) -> dict:
        current_state = self.state.get_current_state()
        course_progress = self.state.get_course_progress()
        build_progress = self.state.get_build_progress()
        competency = self.state.get_competency()
        experiments = self._read_jsonl(
            self.workspace_paths["experiment_history_file"]
        )
        reviews = self._read_jsonl(self.workspace_paths["review_history_file"])
        preferences = self.get_preferences()

        projects = build_progress.get("projects", {})
        completed_projects = [
            project_id
            for project_id, payload in projects.items()
            if payload.get("status") == "completed"
        ]
        active_projects = [
            project_id
            for project_id, payload in projects.items()
            if payload.get("status") == "in_progress"
        ]

        return {
            "module": "profile",
            "interaction": {"mode": "inform"},
            "current": {
                "module": current_state.get("current_module"),
                "course_id": current_state.get("current_course_id"),
                "project_id": current_state.get("current_project"),
                "lab_topic": current_state.get("current_lab_topic"),
                "review_id": current_state.get("current_review_id"),
            },
            "progress": {
                "completed_courses": len(
                    course_progress.get("completed_courses", [])
                ),
                "active_project_count": len(active_projects),
                "completed_project_count": len(completed_projects),
                "experiment_count": len(experiments),
                "review_count": len(reviews),
            },
            "competency": competency.get("areas", {}),
            "stable_preferences": preferences.get("stable_preferences", {}),
            "preference_evidence": preferences.get(
                "evidence_summary", {"lab": 0, "review": 0}
            ),
            "recent_experiments": list(reversed(experiments[-3:])),
            "recent_reviews": list(reversed(reviews[-3:])),
            "state_recommendation": {
                "action": current_state.get("recommended_next_action"),
                "reason": current_state.get("last_action"),
            },
        }
