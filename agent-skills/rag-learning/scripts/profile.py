"""
RAG Learning 学习档案模块。
负责聚合当前进度、实验历史、评审历史和能力摘要。
"""

from __future__ import annotations

import json
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
        experiments = self._read_jsonl(self.workspace_paths["experiment_history_file"])
        reviews = self._read_jsonl(self.workspace_paths["review_history_file"])
        completed_projects = [
            project_id
            for project_id, payload in build_progress.get("projects", {}).items()
            if payload.get("status") == "completed"
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
                "completed_courses": len(course_progress.get("completed_courses", [])),
                "active_project_count": len(build_progress.get("projects", {})),
                "completed_project_count": len(completed_projects),
                "experiment_count": len(experiments),
                "review_count": len(reviews),
            },
            "competency": competency.get("areas", {}),
            "recent_experiments": list(reversed(experiments[-3:])),
            "recent_reviews": list(reversed(reviews[-3:])),
            "recommendation": {
                "action": current_state.get("recommended_next_action"),
                "reason": current_state.get("last_action"),
            },
        }

