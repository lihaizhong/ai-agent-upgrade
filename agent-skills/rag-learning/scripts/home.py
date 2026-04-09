"""
RAG Learning 平台首页。
负责 dashboard、resume 和 recommendation 输出。
"""

from __future__ import annotations

from pathlib import Path

if __package__ in {None, ""}:
    from learning import get_course_metadata
    from state import RagLearningStateStore
else:
    from .learning import get_course_metadata
    from .state import RagLearningStateStore


HOME_CARDS = [
    {
        "label": "继续学习",
        "description": "回到当前课程或推荐课程，继续建立 RAG 选型框架。",
        "value": "continue_learning",
    },
    {
        "label": "搭建最小 RAG",
        "description": "进入最小 RAG 项目，按决策顺序推进实现。",
        "value": "start_build",
    },
    {
        "label": "进入 RAG Lab",
        "description": "对比 embedding、rerank 和 chunking 等关键变量。",
        "value": "open_lab",
    },
    {
        "label": "发起架构评审",
        "description": "围绕业务约束输出结构化 RAG 方案。",
        "value": "start_review",
    },
]


class HomeService:
    def __init__(self, skill_dir: Path, username: str | None = None):
        self.skill_dir = skill_dir
        self.state = RagLearningStateStore.from_skill_dir(skill_dir, username=username)

    def dashboard(self) -> dict:
        summary = self.state.get_summary()
        return {
            "module": "home",
            "interaction": {
                "mode": "selector",
                "question": {
                    "header": "RAG Home",
                    "question": "你现在想推进哪一步？",
                    "options": HOME_CARDS,
                },
            },
            "summary": summary,
            "cards": HOME_CARDS,
        }

    def resume(self) -> dict:
        current_state = self.state.get_current_state()
        course = None
        if current_state.get("current_course_id") is not None:
            course = get_course_metadata(
                self.skill_dir, current_state["current_course_id"]
            )
        return {
            "module": "home",
            "resume_target": {
                "module": current_state.get("current_module"),
                "course": course,
                "project_id": current_state.get("current_project"),
                "lab_topic": current_state.get("current_lab_topic"),
            },
            "reason": current_state.get("last_action"),
        }

    def recommend(self) -> dict:
        summary = self.state.get_summary()
        return {
            "module": "home",
            "recommended_action": summary["recommendation"]["action"],
            "reason": summary["recommendation"]["reason"],
            "current_context": {
                "module": summary["current_module"],
                "course_id": summary["current_course_id"],
                "project_id": summary["current_project"],
            },
        }
