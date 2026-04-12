"""
练习中心模块
负责练习入口和动态练习蓝图。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .course_catalog import COURSE_METADATA
from .state import LearningStateStore
from .workspace import get_workspace_paths


class PracticeService:
    """练习中心服务。"""

    def __init__(self, state_store: LearningStateStore, workspace_paths: dict[str, Path]):
        self.state_store = state_store
        self.workspace_paths = workspace_paths
        self.practice_history_file = workspace_paths["practice_history_file"]
        self.mistakes_file = workspace_paths["mistakes_file"]

    @classmethod
    def from_skill_dir(
        cls, skill_dir: Path, username: str | None = None
    ) -> "PracticeService":
        workspace_paths = get_workspace_paths(skill_dir, username=username)
        return cls(
            state_store=LearningStateStore(workspace_paths),
            workspace_paths=workspace_paths,
        )

    def _timestamp(self) -> str:
        return datetime.now().astimezone().isoformat()

    def _append_jsonl(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _rewrite_jsonl(self, path: Path, rows: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _resolve_mistakes(self, course_id: int, mistake_tags: list[str]) -> int:
        if not mistake_tags or not self.mistakes_file.exists():
            return 0

        with open(self.mistakes_file, "r", encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]

        remaining_tags = set(mistake_tags)
        resolved_count = 0
        for row in reversed(rows):
            if not remaining_tags:
                break
            if row.get("course_id") != course_id:
                continue
            if row.get("status") != "open":
                continue
            mistake_tag = row.get("mistake_tag")
            if mistake_tag not in remaining_tags:
                continue
            row["status"] = "resolved"
            row["review_count"] = int(row.get("review_count", 0)) + 1
            row["last_reviewed_at"] = self._timestamp()
            remaining_tags.remove(mistake_tag)
            resolved_count += 1

        self._rewrite_jsonl(self.mistakes_file, rows)
        return resolved_count

    def get_entry_points(self) -> dict:
        return {
            "interaction": {
                "mode": "selector",
            },
            "question": {
                "id": "practice-entry-selection",
                "header": "练习中心",
                "question": "你想如何继续练习？",
                "options": [
                    {
                        "label": "当前课程继续练",
                        "description": "围绕当前正在学习的课程继续巩固",
                        "value": "current",
                    },
                    {
                        "label": "专项练习",
                        "description": "指定某门课程或某类能力集中练习",
                        "value": "targeted",
                    },
                    {
                        "label": "错题回练",
                        "description": "针对已记录的薄弱点生成相似题",
                        "value": "mistake",
                    },
                ],
                "multiple": False,
            }
        }

    def get_resume_target(self) -> dict:
        current_state = self.state_store.get_current_state()
        current_course_id = current_state.get("current_course_id")
        current_course_name = current_state.get("current_course_name")
        if current_course_id:
            return {
                "interaction": {
                    "mode": "open_ended",
                    "prompt_hint": "根据返回的路由信息，用自然语言引导用户继续当前练习。",
                },
                "entry_type": "current",
                "course_id": current_course_id,
                "course_name": current_course_name,
                "reason": "当前已有课程上下文，优先继续围绕该课程练习。",
            }
        return {
            "interaction": {
                "mode": "open_ended",
                "prompt_hint": "根据返回的路由信息，用自然语言引导用户选择练习方向。",
            },
            "entry_type": "targeted",
            "course_id": None,
            "course_name": None,
            "reason": "当前没有课程上下文，建议先选择专项练习。",
        }

    def _question_type_for_course(self, course_id: int) -> str:
        if course_id <= 3:
            return "diagnose"
        if course_id <= 11:
            return "design"
        if course_id <= 14:
            return "compare"
        return "compose"

    def build_blueprint(
        self,
        *,
        course_id: int | None = None,
        mode: str = "current",
        focus_tag: str | None = None,
    ) -> dict:
        if mode not in {"current", "targeted", "mistake"}:
            raise ValueError(f"不支持的练习模式: {mode}")

        if course_id is None:
            course_id = self.state_store.get_current_state().get("current_course_id")

        if course_id is None and mode != "mistake":
            raise ValueError("current 或 targeted 模式下必须提供课程编号")

        if course_id is not None and course_id not in COURSE_METADATA:
            raise ValueError(f"课程 {course_id} 不存在")

        if mode == "mistake":
            question_type = "diagnose"
            course_name = COURSE_METADATA[course_id]["name"] if course_id else None
            return {
                "interaction": {
                    "mode": "open_ended",
                    "prompt_hint": "根据蓝图自然组织题目，不要把蓝图本身改写成选择器。",
                },
                "mode": "mistake",
                "course_id": course_id,
                "course_name": course_name,
                "question_type": question_type,
                "goal": "围绕历史错误模式生成相似但不重复的练习题。",
                "focus_tag": focus_tag,
                "constraints": [
                    "题目应贴近已记录的错误模式",
                    "不要复述原题，应生成相似但不重复的新场景",
                    "反馈优先指出该错误模式是否被修正",
                ],
                "workflow": [
                    "脚本确定错题回练模式与反馈目标",
                    "LLM 生成新的相似场景和题干",
                    "批改时优先检查错误模式是否得到修正",
                ],
                "response_schema": {
                    "type": question_type,
                    "expected_elements": ["指出错误模式", "给出修正思路"],
                    "answer_format": "用户用自然语言说明问题与修正方式",
                    "feedback_focus": "优先判断用户是否真正修正了历史错误模式",
                },
            }

        course = COURSE_METADATA[course_id]
        question_type = self._question_type_for_course(course_id)
        constraints_map = {
            "diagnose": [
                "给定 1 个错误提示词或失败案例",
                "要求指出核心问题",
                "反馈聚焦 1 个关键改法",
            ],
            "design": [
                "给定 1 个任务场景",
                "要求设计提示词或技术组合",
                "评分看结构完整性与适配性",
            ],
            "compare": [
                "要求比较 2 种相关技术",
                "至少包含适用场景差异",
                "反馈指出关键边界",
            ],
            "compose": [
                "要求组合 2 种及以上技术",
                "必须说明各技术职责",
                "反馈聚焦协作链路是否完整",
            ],
        }
        response_schema_map = {
            "diagnose": {
                "type": "diagnose",
                "expected_elements": ["指出核心问题", "给出关键改法"],
                "answer_format": "用户用自然语言分析错误并提出修正方案",
                "feedback_focus": "优先指出诊断是否抓住真正的失败原因",
            },
            "design": {
                "type": "design",
                "expected_elements": ["步骤明确", "目标清楚", "边界合理"],
                "answer_format": "用户用自然语言或 prompt 草稿作答",
                "feedback_focus": "优先指出结构上最关键的缺口",
            },
            "compare": {
                "type": "compare",
                "expected_elements": ["适用场景差异", "边界差异"],
                "answer_format": "用户对比两种技术并说明何时用哪个",
                "feedback_focus": "优先检查是否真正说清边界而非只讲定义",
            },
            "compose": {
                "type": "compose",
                "expected_elements": ["各技术职责", "协作链路"],
                "answer_format": "用户说明组合方案及各部分职责",
                "feedback_focus": "优先检查组合链路是否完整、职责是否清楚",
            },
        }

        goals = {
            "current": "围绕当前课程做一题巩固练习，检验核心概念是否能迁移到场景中。",
            "targeted": "围绕指定课程做专项训练，集中检查该主题的关键能力。",
        }

        return {
            "interaction": {
                "mode": "open_ended",
                "prompt_hint": "根据蓝图自然组织题目，不要把蓝图本身改写成选择器。",
            },
            "mode": mode,
            "course_id": course_id,
            "course_name": course["name"],
            "question_type": question_type,
            "goal": goals[mode],
            "prerequisites": [
                COURSE_METADATA[prereq]["name"]
                for prereq in course["prereqs"]
                if prereq in COURSE_METADATA
            ],
            "constraints": constraints_map[question_type],
            "workflow": [
                "脚本先确定练习模式、题型和评分关注点",
                "LLM 只生成题干、参考答案和反馈，不改蓝图结构",
                "批改时优先按脚本给出的 expected_elements 检查",
            ],
            "response_schema": response_schema_map[question_type],
        }

    def record_result(self, payload: dict) -> dict:
        course_id = payload.get("course_id")
        course_name = payload.get("course_name")
        entry_type = payload.get("entry_type")
        question_type = payload.get("question_type")
        result = payload.get("result")

        if course_id not in COURSE_METADATA:
            raise ValueError(f"课程 {course_id} 不存在")
        if not course_name:
            course_name = COURSE_METADATA[course_id]["name"]
        if result not in {"good", "partial", "weak"}:
            raise ValueError("result 必须是 good / partial / weak")

        mistake_tags = payload.get("mistake_tags", [])
        strength_tags = payload.get("strength_tags", [])
        prompt_summary = payload.get("prompt_summary", "")
        feedback_summary = payload.get("feedback_summary", "")
        focus_tag = payload.get("focus_tag")
        resolved_mistake_tags = payload.get("resolved_mistake_tags", [])

        if not isinstance(resolved_mistake_tags, list):
            raise ValueError("resolved_mistake_tags 必须是列表")

        event = {
            "timestamp": self._timestamp(),
            "course_id": course_id,
            "course_name": course_name,
            "entry_type": entry_type,
            "question_type": question_type,
            "result": result,
            "mistake_tags": mistake_tags,
            "strength_tags": strength_tags,
            "prompt_summary": prompt_summary,
            "feedback_summary": feedback_summary,
        }
        self._append_jsonl(self.practice_history_file, event)

        tags_to_resolve = []
        if result == "good" and entry_type == "mistake":
            tags_to_resolve = [
                tag
                for tag in (resolved_mistake_tags or mistake_tags or [focus_tag])
                if tag
            ]
        resolved_mistakes = self._resolve_mistakes(course_id, tags_to_resolve)

        written_mistakes = 0
        for mistake_tag in mistake_tags:
            if result == "good":
                continue
            mistake_event = {
                "timestamp": self._timestamp(),
                "course_id": course_id,
                "course_name": course_name,
                "mistake_tag": mistake_tag,
                "mistake_summary": payload.get("mistake_summary", feedback_summary),
                "source": "practice",
                "status": "open",
                "review_count": 0,
                "last_reviewed_at": None,
            }
            self._append_jsonl(self.mistakes_file, mistake_event)
            written_mistakes += 1

        mastery = self.state_store.record_practice_outcome(
            course_id=course_id,
            result=result,
            mistake_delta=written_mistakes - resolved_mistakes,
        )

        return {
            "interaction": {
                "mode": "inform",
            },
            "recorded": True,
            "event": event,
            "written_mistakes": written_mistakes,
            "resolved_mistakes": resolved_mistakes,
            "mastery": mastery["courses"].get(str(course_id)),
        }

    def list_open_mistakes(self, *, course_id: int | None = None) -> dict:
        if not self.mistakes_file.exists():
            return {
                "interaction": {
                    "mode": "inform",
                },
                "count": 0,
                "items": [],
            }

        items = []
        with open(self.mistakes_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                item = json.loads(line)
                if item.get("status") != "open":
                    continue
                if course_id is not None and item.get("course_id") != course_id:
                    continue
                items.append(item)
        return {
            "interaction": {
                "mode": "inform",
            },
            "count": len(items),
            "items": items,
        }

    def get_practice_summary(self) -> dict:
        recent_practice_count = 0
        latest_result = None
        if self.practice_history_file.exists():
            with open(self.practice_history_file, "r", encoding="utf-8") as f:
                rows = [json.loads(line) for line in f if line.strip()]
            recent_practice_count = len(rows)
            if rows:
                latest_result = rows[-1].get("result")

        open_mistakes = self.list_open_mistakes()
        recommended_entry = "targeted"
        reason = "当前没有练习记录，建议先做专项练习。"
        if open_mistakes["count"] > 0:
            recommended_entry = "mistake"
            reason = "你目前有未解决错题，优先回练更有效。"
        elif recent_practice_count > 0:
            recommended_entry = "current"
            reason = "已有练习记录，可以继续沿当前课程巩固。"

        return {
            "interaction": {
                "mode": "inform",
            },
            "recent_practice_count": recent_practice_count,
            "open_mistake_count": open_mistakes["count"],
            "latest_result": latest_result,
            "recommended_entry": recommended_entry,
            "reason": reason,
        }
