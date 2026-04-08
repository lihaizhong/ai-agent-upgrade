"""
Prompt Learning 首页服务
负责 dashboard、resume 和 recommendation 结构输出。
"""

from __future__ import annotations

import json
from pathlib import Path

from .state import LearningStateStore
from .workspace import get_workspace_paths


def _read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default.copy()
    return json.loads(path.read_text(encoding="utf-8"))


class HomeService:
    """学习平台首页服务。"""

    def __init__(self, workspace_paths: dict[str, Path], state_store: LearningStateStore):
        self.workspace_paths = workspace_paths
        self.state_store = state_store

    @classmethod
    def from_skill_dir(
        cls, skill_dir: Path, username: str | None = None
    ) -> "HomeService":
        workspace_paths = get_workspace_paths(skill_dir, username=username)
        return cls(
            workspace_paths=workspace_paths,
            state_store=LearningStateStore(workspace_paths),
        )

    def get_navigation_cards(self) -> list[dict]:
        return [
            {
                "key": "continue_learning",
                "label": "继续学习",
                "description": "回到当前课程并继续推进",
            },
            {
                "key": "start_practice",
                "label": "开始练习",
                "description": "围绕当前课程、专项主题或错题继续训练",
            },
            {
                "key": "take_exam",
                "label": "参加考试",
                "description": "进行诊断考试或综合考试",
            },
            {
                "key": "open_lab",
                "label": "进入 Prompt Lab",
                "description": "把真实任务带进来做 prompt 实战",
            },
        ]

    def get_resume_target(self) -> dict:
        current_state = self.state_store.get_current_state()
        course_progress = self.state_store.get_course_progress()
        current_course_id = current_state.get("current_course_id")
        current_course_name = current_state.get("current_course_name")
        in_progress_course = course_progress.get("in_progress_course")

        if current_course_id or in_progress_course:
            target_course_id = current_course_id or in_progress_course
            return {
                "action": "continue_learning",
                "label": "继续学习",
                "target_module": "learning",
                "target_course_id": target_course_id,
                "target_course_name": current_course_name,
                "reason": "当前存在进行中的课程，可以直接继续推进。",
            }

        return {
            "action": "open_catalog",
            "label": "开始学习",
            "target_module": "learning",
            "target_course_id": None,
            "target_course_name": None,
            "reason": "当前没有进行中的课程，建议先从课程目录开始。",
        }

    def get_recommendation(self) -> dict:
        current_state = self.state_store.get_current_state()
        course_progress = self.state_store.get_course_progress()
        mastery = self.state_store.get_mastery()
        current_action = current_state.get("recommended_next_action")

        if current_action == "start_practice":
            return {
                "action": "start_practice",
                "label": "开始练习",
                "reason": "当前课程已讲完，先做一道动态练习更合适。",
            }

        if course_progress.get("in_progress_course"):
            return {
                "action": "continue_learning",
                "label": "继续学习",
                "reason": "存在进行中的课程，优先保持当前学习连续性。",
            }

        has_developing_course = any(
            item.get("level") == "developing"
            for item in mastery.get("courses", {}).values()
        )
        if has_developing_course:
            return {
                "action": "start_practice",
                "label": "开始练习",
                "reason": "已有课程掌握度仍在 developing，优先巩固更合适。",
            }

        if len(course_progress.get("completed_courses", [])) >= 3:
            return {
                "action": "take_exam",
                "label": "参加考试",
                "reason": "已积累多门课程，适合用一次诊断考试检查薄弱点。",
            }

        return {
            "action": "continue_learning",
            "label": "继续学习",
            "reason": "当前最合理的下一步是继续进入课程学习。",
        }

    def get_dashboard(self) -> dict:
        learner = _read_json(
            self.workspace_paths["learner_file"],
            {
                "workspace_user": self.workspace_paths["workspace_root"].name,
            },
        )
        current_state = self.state_store.get_current_state()
        cards = self.get_navigation_cards()
        recommendation = self.get_recommendation()
        resume = self.get_resume_target()

        return {
            "user": {
                "workspace_user": learner.get("workspace_user"),
                "source_git_username": learner.get("source_git_username"),
            },
            "current": {
                "module": current_state.get("current_module"),
                "course_id": current_state.get("current_course_id"),
                "course_name": current_state.get("current_course_name"),
            },
            "resume": resume,
            "recommendation": recommendation,
            "cards": cards,
            "question": {
                "id": "home-dashboard-navigation",
                "header": "学习平台",
                "question": "你接下来想做什么？",
                "options": [
                    {
                        "label": item["label"],
                        "description": item["description"],
                        "value": item["key"],
                    }
                    for item in cards
                ],
                "multiple": False,
            },
        }
