"""
学习中心模块
负责课程目录、课程元数据、推荐课程和课程完成状态更新。
"""

from __future__ import annotations

from pathlib import Path

from .course_catalog import (
    CATEGORY_METADATA,
    CATEGORY_ORDER,
    COURSE_CATALOG,
    COURSE_METADATA,
)
from .state import LearningStateStore
from .workspace import get_workspace_paths


class LearningService:
    """学习中心服务。"""

    def __init__(self, skill_dir: Path, state_store: LearningStateStore):
        self.skill_dir = skill_dir
        self.state_store = state_store
        self.courses = self._load_courses()

    @classmethod
    def from_skill_dir(
        cls, skill_dir: Path, username: str | None = None
    ) -> "LearningService":
        workspace_paths = get_workspace_paths(skill_dir, username=username)
        return cls(skill_dir=skill_dir, state_store=LearningStateStore(workspace_paths))

    def _load_courses(self) -> list[dict]:
        courses = []
        missing_course_files = []
        missing_code_files = []

        for course in COURSE_CATALOG:
            course_path = self.skill_dir / "courses" / course["course_file"]
            code_path = self.skill_dir / "code" / course["code_file"]
            if course_path.exists():
                courses.append(
                    {
                        "id": course["id"],
                        "name": course["name"],
                        "file": course["course_file"],
                        "path": str(course_path),
                        "summary": course["summary"],
                        "prereqs": course["prereqs"],
                        "code_file": course["code_file"],
                    }
                )
            else:
                missing_course_files.append(course["course_file"])

            if not code_path.exists():
                missing_code_files.append(course["code_file"])

        errors = []
        if missing_course_files:
            errors.append("缺少课程文件: " + ", ".join(sorted(missing_course_files)))
        if missing_code_files:
            errors.append("缺少代码文件: " + ", ".join(sorted(missing_code_files)))
        if errors:
            raise FileNotFoundError("; ".join(errors))

        return courses

    def _course_to_summary(self, course: dict) -> dict:
        return {
            "id": course["id"],
            "value": str(course["id"]),
            "name": course["name"],
            "label": course["name"],
            "summary": course["summary"],
            "prerequisites": course["prereqs"],
            "selection_hint": (
                "可直接选学；如果没学过前置课程，学习时一并补充相关背景。"
                if course["prereqs"]
                else "可直接开始，无前置要求。"
            ),
        }

    def get_catalog(self) -> dict:
        result = {
            "learning_rule": "课程可以自由选择，不要求严格按顺序完成；前置课程仅用于辅助理解。",
            "categories": [],
            "question": {
                "header": "选择课程类别",
                "question": "请选择你要学习的课程类别：",
                "options": [],
                "multiple": False,
            },
        }

        for category_name in CATEGORY_ORDER:
            category = CATEGORY_METADATA[category_name]
            courses = [
                self._course_to_summary(course)
                for course in self.courses
                if course["id"] in category["courses"]
            ]
            result["categories"].append(
                {
                    "name": category_name,
                    "description": category["description"],
                    "course_ids": category["courses"],
                    "range_label": f"{category['courses'][0]:02d}-{category['courses'][-1]:02d}",
                    "courses": courses,
                    "question": {
                        "header": "选择课程",
                        "question": f"请选择 {category_name} 中要学习的课程：",
                        "options": [
                            {
                                "label": item["name"],
                                "description": f"{item['id']:02d} · {item['summary']}",
                                "value": str(item["id"]),
                            }
                            for item in courses
                        ],
                        "multiple": False,
                    },
                }
            )
            result["question"]["options"].append(
                {
                    "label": category_name,
                    "description": (
                        f"{category['courses'][0]:02d}-{category['courses'][-1]:02d} · "
                        f"{category['description']}"
                    ),
                    "value": category_name,
                }
            )

        return result

    def get_category(self, category: str) -> dict:
        normalized = category.strip().lower()
        aliases = {
            "基础课程": "基础课程",
            "基础": "基础课程",
            "推理课程": "推理课程",
            "推理": "推理课程",
            "知识课程": "知识课程",
            "知识": "知识课程",
            "工具课程": "工具课程",
            "工具": "工具课程",
            "优化课程": "优化课程",
            "优化": "优化课程",
            "前沿课程": "前沿课程",
            "前沿": "前沿课程",
        }
        category_name = aliases.get(normalized)
        if not category_name:
            raise ValueError(f"未知课程类别: {category}")

        category_meta = CATEGORY_METADATA[category_name]
        courses = [
            self._course_to_summary(course)
            for course in self.courses
            if course["id"] in category_meta["courses"]
        ]
        return {
            "name": category_name,
            "description": category_meta["description"],
            "learning_rule": "可从本类别任意一课开始；如遇陌生概念，再回看前置课。",
            "courses": courses,
            "question": {
                "header": "选择课程",
                "question": f"请选择 {category_name} 中要学习的课程：",
                "options": [
                    {
                        "label": item["name"],
                        "description": f"{item['id']:02d} · {item['summary']}",
                        "value": str(item["id"]),
                    }
                    for item in courses
                ],
                "multiple": False,
            },
        }

    def get_lesson_meta(self, course_id: int) -> dict:
        if course_id not in COURSE_METADATA:
            raise ValueError(f"课程 {course_id} 不存在")

        course = next((c for c in self.courses if c["id"] == course_id), None)
        if not course:
            raise FileNotFoundError(f"课程文件未找到: {course_id}")

        self.state_store.start_course(course_id, COURSE_METADATA[course_id]["name"])

        return {
            "course_id": course_id,
            "course_name": COURSE_METADATA[course_id]["name"],
            "file_path": course["path"],
            "instruction": "请读取上述文件内容并自行组织输出",
        }

    def get_code_meta(self, course_id: int) -> dict:
        if course_id not in COURSE_METADATA:
            raise ValueError(f"课程 {course_id} 不存在")

        course = COURSE_METADATA[course_id]
        code_path = self.skill_dir / "code" / course["code_file"]
        if not code_path.exists():
            raise FileNotFoundError(f"代码文件未找到: {course['code_file']}")

        return {
            "course_id": course_id,
            "course_name": course["name"],
            "file_path": str(code_path),
            "instruction": "请读取上述文件内容并自行组织输出",
        }

    def get_lesson_panel(self, course_id: int) -> dict:
        if course_id not in COURSE_METADATA:
            raise ValueError(f"课程 {course_id} 不存在")

        course = COURSE_METADATA[course_id]
        self.state_store.update_current_state(
            current_module="learning",
            current_course_id=course_id,
            current_course_name=course["name"],
            last_action="lesson_completed_waiting_practice",
            recommended_next_action="start_practice",
        )
        options = [
            {
                "label": "启发式提问",
                "description": "从概念、场景、边界和迁移四个角度追问",
                "value": "ask",
            },
            {
                "label": "继续做练习题",
                "description": "再来一题，继续巩固当前课程",
                "value": "practice_more",
            },
            {
                "label": "查看代码实现",
                "description": "按分段讲解课程配套代码",
                "value": "code",
            },
        ]
        return {
            "course_id": course_id,
            "course_name": course["name"],
            "question": {
                "header": "练习完成",
                "question": f"「{course['name']}」这道练习做完了，下一步做什么？",
                "options": options,
                "multiple": False,
            },
            "heuristic_prompts": [
                "这个技术的核心作用是什么？",
                "它最适合解决哪类问题？",
                "它和相邻技术的边界差异是什么？",
                "如果迁移到你的任务里，最先该改哪一段？",
            ],
            "followup_actions": [
                "启发式提问",
                "继续做练习题",
                "查看代码实现",
            ],
        }

    def get_code_outline(self, course_id: int) -> dict:
        if course_id not in COURSE_METADATA:
            raise ValueError(f"课程 {course_id} 不存在")

        course = COURSE_METADATA[course_id]
        return {
            "course_id": course_id,
            "course_name": course["name"],
            "code_file": course["code_file"],
            "workflow": [
                "先用 1 到 2 句话说明示例代码解决什么问题",
                "将代码拆成 3 到 5 个片段，按执行顺序或理解顺序讲解",
                "每个片段解释它在做什么、为什么这样写、你可以怎么改",
                "仅在用户明确要求时展示完整代码",
            ],
            "sections": [
                {"key": "setup", "title": "初始化", "focus": "依赖、配置、输入约束"},
                {
                    "key": "prompt",
                    "title": "提示词或样例构造",
                    "focus": "模板、示例、上下文",
                },
                {
                    "key": "execution",
                    "title": "核心调用流程",
                    "focus": "模型调用、推理、控制流",
                },
                {
                    "key": "parsing",
                    "title": "结果解析",
                    "focus": "输出结构、校验、后处理",
                },
                {
                    "key": "entry",
                    "title": "运行入口",
                    "focus": "如何触发、如何替换成你的任务",
                },
            ],
        }

    def recommend_course(self) -> dict:
        current_state = self.state_store.get_current_state()
        progress = self.state_store.get_course_progress()

        current_course_id = current_state.get("current_course_id")
        if current_course_id:
            course = COURSE_METADATA[current_course_id]
            return {
                "recommendation": "存在进行中的课程，建议优先继续当前课程。",
                "course_id": current_course_id,
                "course_name": course["name"],
                "reason": "保持当前学习连续性，切换成本最低。",
            }

        in_progress_course = progress.get("in_progress_course")
        if in_progress_course:
            course = COURSE_METADATA[in_progress_course]
            return {
                "recommendation": "存在进行中的课程，建议优先继续当前课程。",
                "course_id": in_progress_course,
                "course_name": course["name"],
                "reason": "状态记录显示该课程尚未完成。",
            }

        completed = set(progress.get("completed_courses", []))
        for course in COURSE_CATALOG:
            if course["id"] not in completed:
                return {
                    "recommendation": f"建议从第 {course['id']:02d} 课开始，也可以改学你当前最关心的主题。",
                    "course_id": course["id"],
                    "course_name": course["name"],
                    "reason": "这是当前尚未完成课程中的最前一课。",
                }

        return {
            "recommendation": "17 门课程都已完成，可以转入综合练习、考试或 Prompt Lab。",
            "course_id": None,
            "course_name": None,
            "reason": "当前没有待学课程。",
        }

    def complete_course(self, course_id: int) -> dict:
        if course_id not in COURSE_METADATA:
            raise ValueError(f"课程 {course_id} 不存在")
        course_name = COURSE_METADATA[course_id]["name"]
        progress = self.state_store.complete_course(course_id, course_name)
        return {
            "status": "completed",
            "course": course_id,
            "course_name": course_name,
            "progress": progress,
        }
