"""
提示词工程学习系统 - 核心引擎
状态机、模式路由、流程控制
"""

import random
from pathlib import Path
from typing import Optional

from .course_catalog import CATEGORY_METADATA, CATEGORY_ORDER, COURSE_CATALOG, COURSE_METADATA
from .state import UserState


class PromptLearningEngine:
    """学习系统核心引擎"""

    def __init__(self, skill_dir: Optional[str] = None):
        if skill_dir is None:
            skill_dir = Path(__file__).parent.parent
        self.skill_dir = Path(skill_dir)
        self.state = UserState()
        self.courses = self._load_courses()

    def _load_deps(self) -> dict:
        """加载课程依赖关系"""
        return COURSE_METADATA

    def _load_courses(self) -> list[dict]:
        """加载课程列表"""
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
            errors.append(
                "缺少课程文件: " + ", ".join(sorted(missing_course_files))
            )
        if missing_code_files:
            errors.append(
                "缺少代码文件: " + ", ".join(sorted(missing_code_files))
            )
        if errors:
            raise FileNotFoundError("; ".join(errors))

        return courses

    def _category_map(self) -> dict[str, dict]:
        """课程类别元数据。"""
        return CATEGORY_METADATA

    def _course_to_summary(self, course: dict) -> dict:
        """返回课程摘要信息。"""
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

    def get_course_list_by_category(self) -> dict:
        """按类别获取课程列表和类别说明。"""
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
        category_map = self._category_map()
        for category_name in CATEGORY_ORDER:
            category = category_map[category_name]
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

    def get_courses_by_category(self, category: str) -> dict:
        """获取单个类别的课程列表。"""
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

        category_map = self._category_map()
        category_meta = category_map[category_name]
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

    def get_course_content(self, course_id: int) -> str:
        """获取课程内容"""
        deps = self._load_deps()
        if course_id not in deps:
            raise ValueError(f"课程 {course_id} 不存在")

        course = next((c for c in self.courses if c["id"] == course_id), None)
        if not course:
            raise FileNotFoundError(f"课程文件未找到: {course_id}")

        with open(course["path"], "r", encoding="utf-8") as f:
            return f.read()

    def get_code_implementation(self, course_id: int) -> str:
        """获取代码实现"""
        deps = self._load_deps()
        if course_id not in deps:
            raise ValueError(f"课程 {course_id} 不存在")

        code_file = deps[course_id]["code_file"]
        code_path = self.skill_dir / "code" / code_file

        if not code_path.exists():
            raise FileNotFoundError(f"代码文件未找到: {code_file}")

        with open(code_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_prerequisites(self, course_id: int) -> list[int]:
        """获取前置课程"""
        deps = self._load_deps()
        return deps.get(course_id, {}).get("prereqs", [])

    def select_question_type(self, course_id: int) -> str:
        """根据课程选择练习题类型"""
        if course_id <= 3:
            return "诊断型"
        elif course_id <= 11:
            return "设计型"
        elif course_id <= 14:
            return "对比型"
        else:
            return "组合型"

    def build_practice_blueprint(self, course_id: int) -> dict:
        """返回稳定的练习题生成蓝图，由 LLM 负责填充内容。"""
        deps = self._load_deps()
        if course_id not in deps:
            raise ValueError(f"课程 {course_id} 不存在")

        course = deps[course_id]
        question_type = self.select_question_type(course_id)
        prerequisites = [
            deps[prereq]["name"] for prereq in course["prereqs"] if prereq in deps
        ]

        format_rules = {
            "识别型": ["给定 1 个短场景", "要求识别技术或关键概念", "答案可直接判定对错"],
            "诊断型": ["给定 1 个错误提示词或失败案例", "要求指出核心问题", "反馈聚焦 1 个关键改法"],
            "设计型": ["给定 1 个任务场景", "要求设计提示词或技术组合", "评分看结构完整性与适配性"],
            "选择型": ["提供 4 个选项", "仅 1 个正确答案", "必须通过脚本随机化正确答案位置"],
            "对比型": ["要求比较 2 种相关技术", "至少包含适用场景差异", "反馈指出关键边界"],
            "组合型": ["要求组合 2 种及以上技术", "必须说明各技术职责", "反馈聚焦协作链路是否完整"],
        }

        response_schema = {
            "type": question_type,
            "stem": "题干",
            "expected_elements": ["评分要点1", "评分要点2"],
            "answer_format": "用户应该如何作答",
            "feedback_focus": "批改时优先看的一个关键点",
        }

        if question_type == "选择型":
            response_schema["options"] = [
                {"text": "选项内容", "is_correct": True},
                {"text": "选项内容", "is_correct": False},
                {"text": "选项内容", "is_correct": False},
                {"text": "选项内容", "is_correct": False},
            ]

        return {
            "course_id": course_id,
            "course_name": course["name"],
            "question_type": question_type,
            "prerequisites": prerequisites,
            "workflow": [
                "脚本先确定题型、答题格式和评分关注点",
                "LLM 只生成题干、选项或参考答案，不改结构",
                "如果是选择题，再由脚本随机化正确答案位置",
                "批改时优先按脚本给出的 expected_elements 检查",
            ],
            "constraints": format_rules[question_type],
            "response_schema": response_schema,
        }

    def build_learning_panel(self, course_id: int, include_code: bool = False) -> dict:
        """返回课程学习完成后的固定下一步面板。"""
        deps = self._load_deps()
        if course_id not in deps:
            raise ValueError(f"课程 {course_id} 不存在")

        course = deps[course_id]
        options = [
            {
                "label": "启发式提问",
                "description": "从概念、场景、边界和迁移四个角度追问",
                "value": "ask",
            },
            {
                "label": "可选练习",
                "description": "基于脚本蓝图做一题巩固理解",
                "value": "practice",
            },
            {
                "label": "学习导航",
                "description": "切换课程、返回分类或继续下一课",
                "value": "navigate",
            },
        ]
        if include_code:
            options.append(
                {
                    "label": "查看代码实现",
                    "description": "按分段讲解课程配套代码",
                    "value": "code",
                }
            )

        return {
            "course_id": course_id,
            "course_name": course["name"],
            "question": {
                "header": "课程学习完成",
                "question": f"「{course['name']}」学习完成，下一步做什么？",
                "options": options,
                "multiple": False,
            },
            "heuristic_prompts": [
                "这个技术的核心作用是什么？",
                "它最适合解决哪类问题？",
                "它和相邻技术的边界差异是什么？",
                "如果迁移到你的任务里，最先该改哪一段？",
            ],
            "navigation_actions": [
                "继续下一课",
                "返回分类列表",
                "切换到指定课程",
            ],
        }

    def build_code_explanation_outline(self, course_id: int) -> dict:
        """返回代码讲解的固定结构，避免整段贴代码。"""
        deps = self._load_deps()
        if course_id not in deps:
            raise ValueError(f"课程 {course_id} 不存在")

        course = deps[course_id]
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
                {"key": "prompt", "title": "提示词或样例构造", "focus": "模板、示例、上下文"},
                {"key": "execution", "title": "核心调用流程", "focus": "模型调用、推理、控制流"},
                {"key": "parsing", "title": "结果解析", "focus": "输出结构、校验、后处理"},
                {"key": "entry", "title": "运行入口", "focus": "如何触发、如何替换成你的任务"},
            ],
        }

    def randomize_options(
        self, correct_answer: str, distractors: list[str]
    ) -> list[tuple[str, str]]:
        """随机化选项位置"""
        options = [(correct_answer, True)] + [(d, False) for d in distractors]
        random.shuffle(options)
        labels = ["A", "B", "C", "D"]
        return [
            (labels[i], text, is_correct)
            for i, (text, is_correct) in enumerate(options)
        ]

    def get_next_course_recommendation(self) -> dict:
        """获取下一课推荐"""
        return self.state.get_recommended_path()
