"""
学习档案模块
负责聚合读取当前进度、练习、考试和模板摘要。
"""

from __future__ import annotations

import json
from pathlib import Path

from .state import LearningStateStore
from .workspace import get_workspace_paths


class ProfileService:
    """学习档案服务。"""

    def __init__(self, workspace_paths: dict[str, Path], state_store: LearningStateStore):
        self.workspace_paths = workspace_paths
        self.state_store = state_store

    @classmethod
    def from_skill_dir(
        cls, skill_dir: Path, username: str | None = None
    ) -> "ProfileService":
        workspace_paths = get_workspace_paths(skill_dir, username=username)
        return cls(
            workspace_paths=workspace_paths,
            state_store=LearningStateStore(workspace_paths),
        )

    def _read_json(self, path: Path, default: dict) -> dict:
        if not path.exists():
            return default.copy()
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def get_progress(self) -> dict:
        return {
            "current_state": self.state_store.get_current_state(),
            "course_progress": self.state_store.get_course_progress(),
            "mastery": self.state_store.get_mastery(),
        }

    def get_mistakes(self) -> dict:
        rows = self._read_jsonl(self.workspace_paths["mistakes_file"])
        open_items = [row for row in rows if row.get("status") == "open"]
        return {
            "count": len(rows),
            "open_count": len(open_items),
            "items": rows,
        }

    def get_exam_history(self) -> dict:
        rows = self._read_jsonl(self.workspace_paths["exam_history_file"])
        return {
            "count": len(rows),
            "items": rows,
        }

    def get_templates(self) -> dict:
        payload = self._read_json(
            self.workspace_paths["template_index_file"],
            {"templates": [], "updated_at": None},
        )
        return {
            "count": len(payload.get("templates", [])),
            "items": payload.get("templates", []),
            "updated_at": payload.get("updated_at"),
        }

    def get_summary(self) -> dict:
        current_state = self.state_store.get_current_state()
        course_progress = self.state_store.get_course_progress()
        mastery = self.state_store.get_mastery()
        mistakes = self.get_mistakes()
        exams = self.get_exam_history()
        templates = self.get_templates()

        return {
            "current": {
                "module": current_state.get("current_module"),
                "course_id": current_state.get("current_course_id"),
                "course_name": current_state.get("current_course_name"),
            },
            "progress": {
                "completed_count": len(course_progress.get("completed_courses", [])),
                "in_progress_course": course_progress.get("in_progress_course"),
                "last_completed_course": course_progress.get("last_completed_course"),
            },
            "mastery": {
                "course_count": len(mastery.get("courses", {})),
                "courses": mastery.get("courses", {}),
            },
            "mistakes": {
                "count": mistakes["count"],
                "open_count": mistakes["open_count"],
            },
            "exams": {
                "count": exams["count"],
                "latest": exams["items"][-1] if exams["items"] else None,
            },
            "templates": {
                "count": templates["count"],
                "latest": templates["items"][-1] if templates["items"] else None,
            },
        }
