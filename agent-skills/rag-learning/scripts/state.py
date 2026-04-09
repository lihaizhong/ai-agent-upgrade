"""
RAG Learning 平台状态管理。
管理当前产品态、课程进度、项目进度和能力摘要。
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    from workspace import get_workspace_paths
else:
    from .workspace import get_workspace_paths


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def load_json(path: Path, default: dict) -> dict:
    """安全读取 JSON，不存在时返回默认值。"""
    if not path.exists():
        return default.copy()
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: dict) -> None:
    """以原子方式保存 JSON 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def default_current_state() -> dict:
    return {
        "current_module": "home",
        "current_course_id": None,
        "current_project": None,
        "current_lab_topic": None,
        "current_review_id": None,
        "last_action": "workspace_initialized",
        "recommended_next_action": "open_dashboard",
        "updated_at": None,
    }


def default_course_progress() -> dict:
    return {
        "completed_courses": [],
        "in_progress_course": None,
        "last_completed_course": None,
        "course_status": {},
        "updated_at": None,
    }


def default_build_progress() -> dict:
    return {
        "projects": {},
        "updated_at": None,
    }


def default_competency() -> dict:
    return {
        "areas": {
            "rag_foundations": {"level": "new", "evidence_count": 0},
            "embedding_selection": {"level": "new", "evidence_count": 0},
            "vector_db_selection": {"level": "new", "evidence_count": 0},
            "retrieval_design": {"level": "new", "evidence_count": 0},
            "rerank_decision": {"level": "new", "evidence_count": 0},
            "evaluation_design": {"level": "new", "evidence_count": 0},
            "architecture_review": {"level": "new", "evidence_count": 0},
        },
        "updated_at": None,
    }


class RagLearningStateStore:
    """平台态与长期进度态存储。"""

    def __init__(self, workspace_paths: dict[str, Path]):
        self.paths = workspace_paths
        self.current_state_file = workspace_paths["current_state_file"]
        self.course_progress_file = workspace_paths["course_progress_file"]
        self.build_progress_file = workspace_paths["build_progress_file"]
        self.competency_file = workspace_paths["competency_file"]

    @classmethod
    def from_skill_dir(
        cls, skill_dir: Path, username: str | None = None
    ) -> "RagLearningStateStore":
        return cls(get_workspace_paths(skill_dir, username=username))

    def get_current_state(self) -> dict:
        return load_json(self.current_state_file, default_current_state())

    def update_current_state(
        self,
        *,
        current_module: str | None = None,
        current_course_id: int | None = None,
        current_project: str | None = None,
        current_lab_topic: str | None = None,
        current_review_id: str | None = None,
        last_action: str | None = None,
        recommended_next_action: str | None = None,
    ) -> dict:
        state = self.get_current_state()
        updates = {
            "current_module": current_module,
            "current_course_id": current_course_id,
            "current_project": current_project,
            "current_lab_topic": current_lab_topic,
            "current_review_id": current_review_id,
            "last_action": last_action,
            "recommended_next_action": recommended_next_action,
        }
        for key, value in updates.items():
            if value is not None:
                state[key] = value
        state["updated_at"] = _timestamp()
        save_json(self.current_state_file, state)
        return state

    def get_course_progress(self) -> dict:
        return load_json(self.course_progress_file, default_course_progress())

    def start_course(self, course_id: int) -> dict:
        progress = self.get_course_progress()
        course_key = str(course_id)
        course_status = progress["course_status"].setdefault(
            course_key,
            {"status": "in_progress", "started_at": _timestamp(), "completed_at": None},
        )
        course_status["status"] = "in_progress"
        course_status.setdefault("started_at", _timestamp())
        course_status["completed_at"] = None
        progress["in_progress_course"] = course_id
        progress["updated_at"] = _timestamp()
        save_json(self.course_progress_file, progress)
        self.update_current_state(
            current_module="learning",
            current_course_id=course_id,
            last_action="lesson_started",
            recommended_next_action="continue_learning",
        )
        self.increment_competency("rag_foundations")
        return progress

    def complete_course(self, course_id: int) -> dict:
        progress = self.get_course_progress()
        course_key = str(course_id)
        if course_id not in progress["completed_courses"]:
            progress["completed_courses"].append(course_id)
        course_status = progress["course_status"].setdefault(
            course_key,
            {"status": "completed", "started_at": _timestamp(), "completed_at": _timestamp()},
        )
        course_status["status"] = "completed"
        course_status.setdefault("started_at", _timestamp())
        course_status["completed_at"] = _timestamp()
        progress["in_progress_course"] = None
        progress["last_completed_course"] = course_id
        progress["updated_at"] = _timestamp()
        save_json(self.course_progress_file, progress)
        self.update_current_state(
            current_module="learning",
            current_course_id=course_id,
            last_action="course_completed",
            recommended_next_action="start_build",
        )
        self.increment_competency("rag_foundations")
        return progress

    def get_build_progress(self) -> dict:
        return load_json(self.build_progress_file, default_build_progress())

    def start_project(self, project_id: str) -> dict:
        progress = self.get_build_progress()
        project = progress["projects"].setdefault(
            project_id,
            {"status": "in_progress", "current_step": "scenario", "completed_steps": []},
        )
        project["status"] = "in_progress"
        project["current_step"] = project.get("current_step") or "scenario"
        project["last_updated_at"] = _timestamp()
        progress["updated_at"] = _timestamp()
        save_json(self.build_progress_file, progress)
        self.update_current_state(
            current_module="build",
            current_project=project_id,
            last_action="project_started",
            recommended_next_action="continue_build",
        )
        return progress

    def record_build_step(self, project_id: str, step: str, competency_area: str | None = None) -> dict:
        progress = self.get_build_progress()
        project = progress["projects"].setdefault(
            project_id,
            {"status": "in_progress", "current_step": step, "completed_steps": []},
        )
        if step not in project["completed_steps"]:
            project["completed_steps"].append(step)
        project["current_step"] = step
        project["status"] = "in_progress"
        project["last_updated_at"] = _timestamp()
        progress["updated_at"] = _timestamp()
        save_json(self.build_progress_file, progress)
        self.update_current_state(
            current_module="build",
            current_project=project_id,
            last_action=f"{step}_completed",
            recommended_next_action="continue_build",
        )
        if competency_area:
            self.increment_competency(competency_area)
        return progress

    def get_competency(self) -> dict:
        return load_json(self.competency_file, default_competency())

    def increment_competency(self, area: str) -> dict:
        competency = self.get_competency()
        entry = competency["areas"].setdefault(
            area, {"level": "new", "evidence_count": 0}
        )
        entry["evidence_count"] += 1
        if entry["evidence_count"] >= 4:
            entry["level"] = "strong"
        elif entry["evidence_count"] >= 2:
            entry["level"] = "good"
        else:
            entry["level"] = "developing"
        competency["updated_at"] = _timestamp()
        save_json(self.competency_file, competency)
        return competency

    def get_summary(self) -> dict:
        current_state = self.get_current_state()
        course_progress = self.get_course_progress()
        build_progress = self.get_build_progress()
        return {
            "current_module": current_state.get("current_module"),
            "current_course_id": current_state.get("current_course_id"),
            "current_project": current_state.get("current_project"),
            "progress": {
                "completed_courses": len(course_progress.get("completed_courses", [])),
                "in_progress_course": course_progress.get("in_progress_course"),
                "active_projects": len(build_progress.get("projects", {})),
            },
            "recommendation": {
                "action": current_state.get("recommended_next_action"),
                "reason": current_state.get("last_action"),
            },
        }
