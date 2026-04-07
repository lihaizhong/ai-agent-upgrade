"""
提示词工程学习系统 - 核心引擎
状态机、模式路由、流程控制
"""

import random
from pathlib import Path
from typing import Optional

from .state import UserState


class PromptLearningEngine:
    """学习系统核心引擎"""

    CATEGORY_ORDER = [
        "基础课程",
        "推理课程",
        "知识课程",
        "工具课程",
        "优化课程",
        "前沿课程",
    ]

    def __init__(self, skill_dir: Optional[str] = None):
        if skill_dir is None:
            skill_dir = Path(__file__).parent.parent
        self.skill_dir = Path(skill_dir)
        self.state = UserState()
        self.courses = self._load_courses()

    def _load_deps(self) -> dict:
        """加载课程依赖关系"""
        return {
            1: {"name": "零样本提示", "prereqs": [], "code_file": "01_zero_shot.py"},
            2: {"name": "少样本提示", "prereqs": [1], "code_file": "02_few_shot.py"},
            3: {"name": "思维链提示", "prereqs": [2], "code_file": "03_cot.py"},
            4: {
                "name": "自我一致性",
                "prereqs": [3],
                "code_file": "04_self_consistency.py",
            },
            5: {"name": "思维树", "prereqs": [3, 4], "code_file": "05_tot.py"},
            6: {
                "name": "生成知识提示",
                "prereqs": [3],
                "code_file": "06_generated_knowledge.py",
            },
            7: {"name": "检索增强生成", "prereqs": [6], "code_file": "07_rag.py"},
            8: {
                "name": "链式提示",
                "prereqs": [3],
                "code_file": "08_prompt_chaining.py",
            },
            9: {"name": "ReAct框架", "prereqs": [3, 8], "code_file": "09_react.py"},
            10: {"name": "程序辅助语言模型", "prereqs": [3], "code_file": "10_pal.py"},
            11: {
                "name": "自动推理和工具使用",
                "prereqs": [9],
                "code_file": "11_art.py",
            },
            12: {"name": "自动提示工程师", "prereqs": [1], "code_file": "12_ape.py"},
            13: {
                "name": "主动提示",
                "prereqs": [2],
                "code_file": "13_active_prompt.py",
            },
            14: {"name": "方向性刺激提示", "prereqs": [3], "code_file": "14_dsp.py"},
            15: {"name": "自我反思", "prereqs": [3, 9], "code_file": "15_reflexion.py"},
            16: {
                "name": "多模态思维链",
                "prereqs": [3],
                "code_file": "16_multimodal_cot.py",
            },
            17: {"name": "图提示", "prereqs": [5], "code_file": "17_graph_prompt.py"},
        }

    def _load_courses(self) -> list[dict]:
        """加载课程列表"""
        courses = []
        courses_dir = self.skill_dir / "courses"
        deps = self._load_deps()
        course_summaries = {
            1: "入门必学，学会直接给模型下清晰指令",
            2: "通过示例约束输出格式和风格",
            3: "让模型显式展开推理步骤",
            4: "多次采样后投票，降低单次推理偏差",
            5: "把复杂问题扩展成树状探索过程",
            6: "先激活相关知识，再组织回答",
            7: "结合外部知识库，降低知识过期和幻觉",
            8: "把任务拆成多个串联步骤执行",
            9: "让模型在推理和行动之间循环",
            10: "把推理转成代码执行，提升计算可靠性",
            11: "自动选择工具与推理步骤完成任务",
            12: "自动生成和搜索更优提示词",
            13: "动态挑选最有帮助的示例",
            14: "通过刺激信号引导模型朝目标输出",
            15: "基于失败反馈持续自我修正",
            16: "把视觉信息纳入链式推理",
            17: "用图结构组织提示与关系推理",
        }
        for i in range(1, 18):
            matches = list(courses_dir.glob(f"{i:02d}-*.md"))
            if matches:
                courses.append(
                    {
                        "id": i,
                        "name": deps[i]["name"],
                        "file": matches[0].name,
                        "path": str(matches[0]),
                        "summary": course_summaries[i],
                        "prereqs": deps[i]["prereqs"],
                    }
                )
        return courses

    def _category_map(self) -> dict[str, dict]:
        """课程类别元数据。"""
        return {
            "基础课程": {
                "description": "建立提示词最基本的指令表达和示例意识。",
                "courses": [1, 2],
            },
            "推理课程": {
                "description": "学习如何让模型分步推理、投票和探索多条解法。",
                "courses": [3, 4, 5],
            },
            "知识课程": {
                "description": "处理知识注入、外部检索和多步骤任务编排。",
                "courses": [6, 7, 8],
            },
            "工具课程": {
                "description": "让模型调用工具、执行代码并与环境交互。",
                "courses": [9, 10, 11],
            },
            "优化课程": {
                "description": "关注提示词自动优化、示例选择与引导策略。",
                "courses": [12, 13, 14],
            },
            "前沿课程": {
                "description": "覆盖反馈学习、多模态推理和图结构提示等进阶主题。",
                "courses": [15, 16, 17],
            },
        }

    def _course_to_summary(self, course: dict) -> dict:
        """返回课程摘要信息。"""
        return {
            "id": course["id"],
            "name": course["name"],
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
        }
        category_map = self._category_map()
        for category_name in self.CATEGORY_ORDER:
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
                    "courses": courses,
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
