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
            "interaction": {"mode": "selector"},
            "question": {
                "header": "RAG Home",
                "question": "你现在想推进哪一步？",
                "options": HOME_CARDS,
            },
            "summary": summary,
            "cards": HOME_CARDS,
        }

    def resume(self) -> dict:
        current_state = self.state.get_current_state()
        course_progress = self.state.get_course_progress()
        build_progress = self.state.get_build_progress()
        resume_action, target_module, target_payload, reason, is_fallback = (
            self._resolve_resume_contract(
                current_state=current_state,
                course_progress=course_progress,
                build_progress=build_progress,
            )
        )
        return {
            "module": "home",
            "interaction": {
                "mode": "open_ended",
                "prompt_hint": "根据 continuation contract，用自然语言引导用户恢复当前上下文。",
            },
            "resume_action": resume_action,
            "target_module": target_module,
            "target_payload": target_payload,
            "resume_target": target_payload,
            "reason": reason,
            "is_fallback": is_fallback,
        }

    def recommend(self) -> dict:
        current_state = self.state.get_current_state()
        course_progress = self.state.get_course_progress()
        build_progress = self.state.get_build_progress()
        current_action = current_state.get("recommended_next_action")

        interaction = {
            "mode": "open_ended",
            "prompt_hint": "根据返回的推荐信息，用自然语言建议用户下一步。",
        }
        explicit_action = self._recommendation_from_state(current_action, interaction)
        if explicit_action is not None:
            explicit_action["current_context"] = {
                "module": current_state.get("current_module"),
                "course_id": current_state.get("current_course_id"),
                "project_id": current_state.get("current_project"),
            }
            return explicit_action

        fallback = self._fallback_recommendation(
            current_state=current_state,
            course_progress=course_progress,
            build_progress=build_progress,
            interaction=interaction,
        )
        return {
            "module": "home",
            "interaction": interaction,
            "recommended_action": fallback["recommended_action"],
            "reason": fallback["reason"],
            "current_context": {
                "module": current_state.get("current_module"),
                "course_id": current_state.get("current_course_id"),
                "project_id": current_state.get("current_project"),
            },
        }

    def _resolve_resume_contract(
        self,
        *,
        current_state: dict,
        course_progress: dict,
        build_progress: dict,
    ) -> tuple[str, str, dict, str, bool]:
        current_module = current_state.get("current_module")
        current_course_id = current_state.get("current_course_id")
        current_project = current_state.get("current_project")
        current_lab_topic = current_state.get("current_lab_topic")
        current_review_id = current_state.get("current_review_id")

        if current_module == "learning" and current_course_id is not None:
            course = get_course_metadata(self.skill_dir, current_course_id)
            return (
                "continue_learning",
                "learning",
                {
                    "course_id": current_course_id,
                    "course": course,
                },
                "当前存在课程上下文，可直接回到学习中心继续当前课程。",
                False,
            )

        if current_module == "build" and current_project:
            return (
                "continue_build",
                "build",
                {
                    "project_id": current_project,
                },
                "当前存在实战项目上下文，可直接回到实战中心继续推进。",
                False,
            )

        if current_module == "lab" and current_lab_topic:
            return (
                "continue_lab",
                "lab",
                {
                    "topic": current_lab_topic,
                    "project_id": current_project,
                },
                "当前存在实验上下文，可直接回到 RAG Lab 继续当前主题。",
                False,
            )

        if current_module == "review" and current_review_id:
            return (
                "continue_review",
                "review",
                {
                    "scenario": current_review_id,
                    "project_id": current_project,
                },
                "当前存在架构评审上下文，可直接回到评审模块继续整理。",
                False,
            )

        in_progress_course = course_progress.get("in_progress_course")
        if in_progress_course is not None:
            course = get_course_metadata(self.skill_dir, in_progress_course)
            return (
                "continue_learning",
                "learning",
                {
                    "course_id": in_progress_course,
                    "course": course,
                },
                "当前存在进行中的课程，可恢复到学习主线继续推进。",
                False,
            )

        active_project_id = self._active_build_project(build_progress, current_project)
        if active_project_id is not None:
            return (
                "continue_build",
                "build",
                {
                    "project_id": active_project_id,
                },
                "当前存在进行中的 RAG 项目，可恢复到实战中心继续推进。",
                False,
            )

        return (
            "open_dashboard",
            "home",
            {},
            "当前没有可恢复的进行中上下文，回到平台首页重新选择下一步。",
            True,
        )

    def _active_build_project(
        self, build_progress: dict, preferred_project: str | None
    ) -> str | None:
        projects = build_progress.get("projects", {})
        if preferred_project and projects.get(preferred_project, {}).get("status") == "in_progress":
            return preferred_project
        for project_id, payload in projects.items():
            if payload.get("status") == "in_progress":
                return project_id
        return None

    def _recommendation_from_state(
        self, action: str | None, interaction: dict
    ) -> dict | None:
        if action in {None, "open_dashboard"}:
            return None

        recommendation_map = {
            "continue_learning": {
                "recommended_action": "continue_learning",
                "reason": "当前已有明确课程上下文，优先保持学习连续性。",
            },
            "start_build": {
                "recommended_action": "start_build",
                "reason": "当前课程主线已完成，下一步适合进入最小 RAG 实战。",
            },
            "continue_build": {
                "recommended_action": "continue_build",
                "reason": "当前已有进行中的 RAG 项目，优先继续推进。",
            },
            "return_to_build": {
                "recommended_action": "return_to_build",
                "reason": "实验已完成，下一步应回到实战上下文吸收结论。",
            },
            "complete_constraints": {
                "recommended_action": "complete_constraints",
                "reason": "架构评审已启动，先补齐业务约束再继续。",
            },
            "review_profile": {
                "recommended_action": "review_profile",
                "reason": "当前评审已完成，适合回到学习档案查看沉淀结果。",
            },
        }
        payload = recommendation_map.get(action)
        if payload is None:
            return None
        return {
            "module": "home",
            "interaction": interaction,
            **payload,
            "current_context": {},
        }

    def _fallback_recommendation(
        self,
        *,
        current_state: dict,
        course_progress: dict,
        build_progress: dict,
        interaction: dict,
    ) -> dict:
        if course_progress.get("in_progress_course") is not None:
            return {
                "module": "home",
                "interaction": interaction,
                "recommended_action": "continue_learning",
                "reason": "当前存在进行中的课程，优先继续学习。",
            }

        current_project = current_state.get("current_project")
        if current_project or build_progress.get("projects"):
            return {
                "module": "home",
                "interaction": interaction,
                "recommended_action": "continue_build",
                "reason": "当前已有项目上下文，优先继续推进实战。",
            }

        return {
            "module": "home",
            "interaction": interaction,
            "recommended_action": "continue_learning",
            "reason": "当前没有更强的显式动作，默认回到学习主线。",
        }
