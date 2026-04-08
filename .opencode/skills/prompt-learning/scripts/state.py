"""
提示词工程学习系统 - 核心状态管理
管理用户学习进度、考试状态、会话配置
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .course_catalog import CATEGORY_ORDER, COURSE_METADATA
from .workspace import get_workspace_paths


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def load_json(path: Path, default: dict) -> dict:
    """安全读取 JSON，不存在时返回默认值。"""
    if not path.exists():
        return default.copy()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, payload: dict) -> None:
    """保存 JSON 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def default_current_state() -> dict:
    return {
        "current_module": "home",
        "current_course_id": None,
        "current_course_name": None,
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


def default_mastery() -> dict:
    return {
        "courses": {},
        "updated_at": None,
    }


def derive_mastery_level(practice_attempts: int, mistake_count: int) -> str:
    """根据练习次数和错误数推导课程掌握度。"""
    if practice_attempts <= 0:
        return "new"
    if practice_attempts >= 4 and mistake_count <= 1:
        return "strong"
    if practice_attempts >= 2 and mistake_count <= 2:
        return "good"
    return "developing"


class LearningStateStore:
    """平台态与长期进度态存储。"""

    def __init__(self, workspace_paths: dict[str, Path]):
        self.paths = workspace_paths
        self.current_state_file = workspace_paths["current_state_file"]
        self.course_progress_file = workspace_paths["course_progress_file"]
        self.mastery_file = workspace_paths["mastery_file"]

    @classmethod
    def from_skill_dir(
        cls, skill_dir: Path, username: str | None = None
    ) -> "LearningStateStore":
        return cls(get_workspace_paths(skill_dir, username=username))

    def get_current_state(self) -> dict:
        return load_json(self.current_state_file, default_current_state())

    def update_current_state(
        self,
        *,
        current_module: str | None = None,
        current_course_id: int | None = None,
        current_course_name: str | None = None,
        last_action: str | None = None,
        recommended_next_action: str | None = None,
    ) -> dict:
        state = self.get_current_state()
        updates = {
            "current_module": current_module,
            "current_course_id": current_course_id,
            "current_course_name": current_course_name,
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

    def start_course(self, course_id: int, course_name: str) -> dict:
        progress = self.get_course_progress()
        course_key = str(course_id)
        existing_status = progress["course_status"].get(course_key, {})
        is_completed_course = (
            course_id in progress["completed_courses"]
            or existing_status.get("status") == "completed"
        )

        if is_completed_course:
            self.update_current_state(
                current_module="learning",
                current_course_id=course_id,
                current_course_name=course_name,
                last_action="lesson_opened",
                recommended_next_action="continue_learning",
            )
            return progress

        course_status = progress["course_status"].setdefault(
            course_key,
            {
                "status": "in_progress",
                "started_at": _timestamp(),
                "completed_at": None,
            },
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
            current_course_name=course_name,
            last_action="lesson_started",
            recommended_next_action="continue_learning",
        )
        return progress

    def complete_course(self, course_id: int, course_name: str) -> dict:
        progress = self.get_course_progress()
        course_key = str(course_id)
        if course_id not in progress["completed_courses"]:
            progress["completed_courses"].append(course_id)

        course_status = progress["course_status"].setdefault(
            course_key,
            {
                "status": "completed",
                "started_at": _timestamp(),
                "completed_at": _timestamp(),
            },
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
            current_course_name=course_name,
            last_action="course_completed",
            recommended_next_action="continue_learning",
        )
        return progress

    def get_mastery(self) -> dict:
        return load_json(self.mastery_file, default_mastery())

    def record_practice_outcome(
        self,
        *,
        course_id: int,
        result: str,
        mistake_count: int = 0,
    ) -> dict:
        mastery = self.get_mastery()
        course_key = str(course_id)
        course_entry = mastery["courses"].setdefault(
            course_key,
            {
                "level": "new",
                "practice_attempts": 0,
                "mistake_count": 0,
                "last_practiced_at": None,
            },
        )
        course_entry["practice_attempts"] += 1
        course_entry["mistake_count"] += max(mistake_count, 0)
        course_entry["last_practiced_at"] = _timestamp()
        course_entry["level"] = derive_mastery_level(
            course_entry["practice_attempts"],
            course_entry["mistake_count"],
        )
        mastery["updated_at"] = _timestamp()
        save_json(self.mastery_file, mastery)

        recommended_next_action = "start_practice"
        if result == "good":
            recommended_next_action = "continue_learning"
        elif mistake_count > 0 or result == "weak":
            recommended_next_action = "review_mistakes"

        self.update_current_state(
            current_module="practice",
            last_action="practice_completed",
            recommended_next_action=recommended_next_action,
        )
        return mastery

    def get_summary(self) -> dict:
        current_state = self.get_current_state()
        progress = self.get_course_progress()
        return {
            "current_module": current_state.get("current_module"),
            "current_course": {
                "id": current_state.get("current_course_id"),
                "name": current_state.get("current_course_name"),
            },
            "progress": {
                "completed_count": len(progress.get("completed_courses", [])),
                "in_progress_course": progress.get("in_progress_course"),
                "last_completed_course": progress.get("last_completed_course"),
            },
            "recommendation": {
                "action": current_state.get("recommended_next_action"),
                "reason": current_state.get("last_action"),
            },
        }


class UserState:
    """用户状态管理器"""

    def __init__(self, state_dir: Optional[str] = None):
        if state_dir is None:
            state_dir = os.environ.get(
                "PROMPT_LEARNING_STATE_DIR",
                os.path.join(os.path.expanduser("~"), ".prompt_learning_state"),
            )
        self.state_dir = self._ensure_state_dir(Path(state_dir))
        self.state_file = self.state_dir / "user_state.json"
        self.state = self._load()

    def _ensure_state_dir(self, preferred: Path) -> Path:
        """优先使用用户指定目录，失败时回退到临时目录。"""
        candidates = [
            preferred,
            Path.cwd() / ".prompt_learning_state",
            Path("/tmp/prompt_learning_state"),
        ]
        for candidate in candidates:
            try:
                candidate.mkdir(parents=True, exist_ok=True)
                return candidate
            except OSError:
                continue
        raise PermissionError("无法创建 prompt-learning 状态目录")

    def _load(self) -> dict:
        """加载用户状态"""
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._default_state()

    def _default_state(self) -> dict:
        """默认状态"""
        return {
            "completed_courses": [],
            "current_course": None,
            "practice_count": 0,
            "exam_history": [],
            "last_mode": None,
            "session": {
                "active": False,
                "mode": None,
                "course_index": None,
                "exam_questions": [],
                "exam_answers": [],
                "exam_scores": [],
                "current_question": 0,
            },
            "preferences": {
                "use_question_tool": True,
            },
            "updated_at": None,
        }

    def save(self):
        """保存状态到文件"""
        self.state["updated_at"] = datetime.now().isoformat()
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def complete_course(self, course_id: str):
        """标记课程完成"""
        if course_id not in self.state["completed_courses"]:
            self.state["completed_courses"].append(course_id)
        self.state["current_course"] = course_id
        self.save()

    def start_session(self, mode: str, **kwargs):
        """开始新会话"""
        self.state["last_mode"] = mode
        self.state["session"] = {
            "active": True,
            "mode": mode,
            "course_index": kwargs.get("course_index"),
            "exam_questions": kwargs.get("exam_questions", []),
            "exam_answers": [],
            "exam_scores": [],
            "current_question": 0,
            **kwargs,
        }
        self.save()

    def end_session(self):
        """结束当前会话"""
        self.state["session"]["active"] = False
        self.save()

    def record_exam_result(self, score: int, total: int, report_path: str):
        """记录考试成绩"""
        self.state["exam_history"].append(
            {
                "date": datetime.now().isoformat(),
                "score": score,
                "total": total,
                "report_path": report_path,
            }
        )
        self.save()

    def increment_practice(self):
        """增加练习计数"""
        self.state["practice_count"] += 1
        self.save()

    def get_next_course(self) -> Optional[int]:
        """获取下一门建议课程编号。"""
        recommendation = self.get_recommended_path()
        return recommendation.get("next_course")

    def get_recommended_path(self) -> dict:
        """获取推荐学习路径。

        规则：
        - 允许自由选课，不强制线性推进。
        - 如果当前课程存在未完成前置课，优先建议补前置。
        - 否则优先推荐同类别中尚未学习的课程。
        - 再否则推荐全局第一门未完成课程。
        """
        completed = self.state["completed_courses"]
        completed_ids = {
            int(course.split("-")[0])
            for course in completed
            if course and "-" in course and course.split("-")[0].isdigit()
        }

        current_course_id = None
        current_course = self.state.get("current_course")
        if (
            isinstance(current_course, str)
            and "-" in current_course
            and current_course.split("-")[0].isdigit()
        ):
            current_course_id = int(current_course.split("-")[0])

        if not completed_ids and not current_course_id:
            return {
                "recommendation": "建议先从基础课程开始；如果你已有经验，也可以直接指定想学的课程。",
                "next_course": 1,
                "category": "基础课程",
                "reason": "建立最基本的指令表达和示例意识。",
            }

        if current_course_id:
            prereqs = COURSE_METADATA.get(current_course_id, {}).get("prereqs", [])
            missing_prereqs = [course_id for course_id in prereqs if course_id not in completed_ids]
            if missing_prereqs:
                next_course = missing_prereqs[0]
                return {
                    "recommendation": (
                        f"当前课程可以继续学；如果你觉得某些概念跳跃，优先补第 {next_course:02d} 课会更稳。"
                    ),
                    "current_course": current_course_id,
                    "next_course": next_course,
                    "category": self._get_category_for_course(next_course),
                    "reason": f"这是当前课程的前置知识：{COURSE_METADATA[next_course]['name']}。",
                }

        current_category = (
            self._get_category_for_course(current_course_id) if current_course_id else None
        )
        if current_category:
            for course_id in self._category_course_ids(current_category):
                if course_id == current_course_id and course_id not in completed_ids:
                    continue
                if course_id not in completed_ids:
                    return {
                        "recommendation": f"建议继续本类别学习，第 {course_id:02d} 课与当前主题衔接最自然。",
                        "current_course": current_course_id,
                        "next_course": course_id,
                        "category": current_category,
                        "reason": f"保持在“{current_category}”内继续推进，知识跳跃最小。",
                    }

        for course_id in sorted(COURSE_METADATA):
            if course_id not in completed_ids:
                return {
                    "recommendation": f"建议下一步学习第 {course_id:02d} 课，也可以直接改学你当前最关心的主题。",
                    "current_course": current_course_id,
                    "next_course": course_id,
                    "category": self._get_category_for_course(course_id),
                    "reason": "这是当前尚未完成的课程之一。",
                }

        return {
            "recommendation": "17 门课程都已完成，可以转入综合练习、考试或针对具体任务做提示词生成训练。",
            "current_course": current_course_id,
            "next_course": None,
            "category": None,
            "reason": "当前没有未完成课程。",
        }

    @staticmethod
    def _get_category_for_course(course_num: int) -> Optional[str]:
        """获取课程所属类别"""
        categories = {
            "基础课程": [1, 2],
            "推理课程": [3, 4, 5],
            "知识课程": [6, 7, 8],
            "工具课程": [9, 10, 11],
            "优化课程": [12, 13, 14],
            "前沿课程": [15, 16, 17],
        }
        for cat, courses in categories.items():
            if course_num in courses:
                return cat
        return None

    @staticmethod
    def _category_course_ids(category_name: str) -> list[int]:
        category_map = {
            "基础课程": [1, 2],
            "推理课程": [3, 4, 5],
            "知识课程": [6, 7, 8],
            "工具课程": [9, 10, 11],
            "优化课程": [12, 13, 14],
            "前沿课程": [15, 16, 17],
        }
        if category_name in category_map:
            return category_map[category_name]

        for category in CATEGORY_ORDER:
            if category == category_name:
                return category_map.get(category, [])
        return []
