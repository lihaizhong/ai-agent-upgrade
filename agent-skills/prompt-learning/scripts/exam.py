"""
提示词工程学习系统 - 考试引擎
题目生成、评分、报告生成
"""

from __future__ import annotations

import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .state import LearningStateStore
from .workspace import get_workspace_paths


class ExamEngine:
    """考试引擎"""

    def __init__(
        self,
        skill_dir: Optional[str | Path] = None,
        username: str | None = None,
    ):
        if skill_dir is None:
            skill_dir = Path(__file__).parent.parent
        self.skill_dir = Path(skill_dir)
        workspace_paths = get_workspace_paths(self.skill_dir, username=username)
        self.exam_dir = workspace_paths["exam_reports_dir"]
        self.exam_dir.mkdir(parents=True, exist_ok=True)
        self.questions = []
        self.answers = []
        self.scores = []

    def get_entry_points(self) -> dict:
        """返回考试中心入口。"""
        return {
            "interaction": {
                "mode": "selector",
            },
            "question": {
                "id": "exam-entry-selection",
                "header": "考试中心",
                "question": "你想进行哪种考试？",
                "options": [
                    {
                        "label": "诊断考试",
                        "description": "快速识别知识缺口和薄弱课程",
                        "value": "diagnostic",
                    },
                    {
                        "label": "综合考试",
                        "description": "系统检查跨课程理解和技术组合能力",
                        "value": "final",
                    },
                ],
                "multiple": False,
            }
        }

    def build_exam_blueprint(self, exam_type: str = "diagnostic") -> dict:
        """固定考试流程和槽位，题目内容由 LLM 生成。"""
        type_meta = {
            "diagnostic": {
                "label": "诊断考试",
                "goal": "快速识别知识缺口并输出补强建议",
            },
            "final": {
                "label": "综合考试",
                "goal": "系统检查综合掌握情况与跨技术组合能力",
            },
        }
        meta = type_meta.get(exam_type, type_meta["diagnostic"])
        return {
            "interaction": {
                "mode": "inform",
            },
            "exam_type": exam_type,
            "exam_label": meta["label"],
            "goal": meta["goal"],
            "total_questions": 11,
            "total_score": 100,
            "workflow": [
                "脚本先生成固定结构和题位",
                "LLM 按题位生成内容",
                "脚本校验题型、分值、难度和字段完整性",
                "校验通过后再展示给用户",
            ],
            "slots": [
                {
                    "num": 1,
                    "type": "mc",
                    "difficulty": "初级",
                    "score": 5,
                    "goal": "基础概念识别",
                },
                {
                    "num": 2,
                    "type": "mc",
                    "difficulty": "初级",
                    "score": 5,
                    "goal": "简单场景判断",
                },
                {
                    "num": 3,
                    "type": "mc",
                    "difficulty": "中级",
                    "score": 5,
                    "goal": "技术选择",
                },
                {
                    "num": 4,
                    "type": "mc",
                    "difficulty": "中级",
                    "score": 5,
                    "goal": "方案对比",
                },
                {
                    "num": 5,
                    "type": "mc",
                    "difficulty": "高级/专家",
                    "score": 5,
                    "goal": "复杂权衡",
                },
                {
                    "num": 6,
                    "type": "fill",
                    "difficulty": "中级",
                    "score": 10,
                    "goal": "关键参数",
                },
                {
                    "num": 7,
                    "type": "fill",
                    "difficulty": "中级",
                    "score": 10,
                    "goal": "步骤或机制",
                },
                {
                    "num": 8,
                    "type": "fill",
                    "difficulty": "高级",
                    "score": 10,
                    "goal": "场景匹配",
                },
                {
                    "num": 9,
                    "type": "essay",
                    "difficulty": "中级",
                    "score": 15,
                    "goal": "提示词设计",
                },
                {
                    "num": 10,
                    "type": "essay",
                    "difficulty": "高级",
                    "score": 15,
                    "goal": "多技术融合",
                },
                {
                    "num": 11,
                    "type": "essay",
                    "difficulty": "专家",
                    "score": 15,
                    "goal": "系统性权衡",
                },
            ],
        }

    def generate_exam_structure(self, exam_type: str = "diagnostic") -> dict:
        """生成考试结构说明"""
        type_meta = {
            "diagnostic": {
                "label": "诊断考试",
                "goal": "快速识别知识缺口和薄弱点",
            },
            "final": {
                "label": "综合考试",
                "goal": "系统检查综合掌握情况与技术组合能力",
            },
        }
        meta = type_meta.get(exam_type, type_meta["diagnostic"])
        return {
            "interaction": {
                "mode": "inform",
            },
            "exam_type": exam_type,
            "exam_label": meta["label"],
            "goal": meta["goal"],
            "total_questions": 11,
            "total_score": 100,
            "sections": [
                {
                    "name": "选择题",
                    "count": 5,
                    "score_per_question": 5,
                    "total_score": 25,
                    "difficulty": "初级到专家",
                },
                {
                    "name": "填空题",
                    "count": 3,
                    "score_per_question": 10,
                    "total_score": 30,
                    "difficulty": "中级及以上",
                },
                {
                    "name": "大题",
                    "count": 3,
                    "score_per_question": 15,
                    "total_score": 45,
                    "difficulty": "中级及以上",
                },
            ],
        }

    def generate_mc_question(
        self,
        question_num: int,
        difficulty: str,
        question: str,
        options: list[dict],
        correct_index: int,
    ) -> dict:
        """生成选择题"""
        shuffled = list(enumerate(options))
        random.shuffle(shuffled)

        new_correct_idx = next(
            i for i, (orig_idx, _) in enumerate(shuffled) if orig_idx == correct_index
        )

        return {
            "type": "mc",
            "num": question_num,
            "difficulty": difficulty,
            "question": question,
            "options": [
                {
                    "label": chr(65 + i),
                    "text": opt["text"],
                    "description": opt.get("description", ""),
                }
                for i, (_, opt) in enumerate(shuffled)
            ],
            "correct_answer": chr(65 + new_correct_idx),
            "score": 5,
        }

    def generate_fill_question(
        self,
        question_num: int,
        difficulty: str,
        question: str,
        answer: str,
        acceptable_variants: list[str] = None,
    ) -> dict:
        """生成填空题"""
        return {
            "type": "fill",
            "num": question_num,
            "difficulty": difficulty,
            "question": question,
            "answer": answer,
            "acceptable_variants": acceptable_variants or [],
            "score": 10,
        }

    def generate_essay_question(
        self,
        question_num: int,
        difficulty: str,
        scenario: str,
        requirements: list[str],
        scoring_rubric: dict,
    ) -> dict:
        """生成大题"""
        return {
            "type": "essay",
            "num": question_num,
            "difficulty": difficulty,
            "scenario": scenario,
            "requirements": requirements,
            "scoring_rubric": scoring_rubric,
            "score": 15,
        }

    def validate_mc_question(self, question: dict) -> dict:
        """校验选择题结构，避免 LLM 自行漂移。"""
        errors = []

        if question.get("type") != "mc":
            errors.append("type 必须为 mc")
        if question.get("score") != 5:
            errors.append("score 必须为 5")
        if not question.get("question"):
            errors.append("question 不能为空")

        options = question.get("options", [])
        if len(options) != 4:
            errors.append("options 必须恰好为 4 个")

        labels = [option.get("label") for option in options]
        if labels != ["A", "B", "C", "D"]:
            errors.append("options.label 必须依次为 A/B/C/D")

        correct_answer = question.get("correct_answer")
        if correct_answer not in {"A", "B", "C", "D"}:
            errors.append("correct_answer 必须为 A/B/C/D")

        return {"valid": not errors, "errors": errors}

    def validate_fill_question(self, question: dict) -> dict:
        """校验填空题结构。"""
        errors = []

        if question.get("type") != "fill":
            errors.append("type 必须为 fill")
        if question.get("score") != 10:
            errors.append("score 必须为 10")
        if not question.get("question"):
            errors.append("question 不能为空")
        if not question.get("answer"):
            errors.append("answer 不能为空")

        return {"valid": not errors, "errors": errors}

    def validate_essay_question(self, question: dict) -> dict:
        """校验大题结构。"""
        errors = []
        rubric = question.get("scoring_rubric", {})

        if question.get("type") != "essay":
            errors.append("type 必须为 essay")
        if question.get("score") != 15:
            errors.append("score 必须为 15")
        if not question.get("scenario"):
            errors.append("scenario 不能为空")
        if not isinstance(question.get("requirements"), list) or not question.get(
            "requirements"
        ):
            errors.append("requirements 必须是非空列表")
        if not isinstance(rubric, dict) or not rubric:
            errors.append("scoring_rubric 必须是非空对象")

        rubric_total = sum(rubric.values()) if isinstance(rubric, dict) else 0
        if rubric and abs(rubric_total - 1.0) > 0.001:
            errors.append("scoring_rubric 权重总和必须为 1.0")

        return {"valid": not errors, "errors": errors}

    def validate_exam_paper(self, questions: list[dict]) -> dict:
        """校验整张试卷是否符合固定流程。"""
        blueprint = self.build_exam_blueprint()
        errors = []

        if len(questions) != len(blueprint["slots"]):
            errors.append("题目总数必须为 11")
            return {"valid": False, "errors": errors}

        score_total = 0
        for slot, question in zip(blueprint["slots"], questions):
            if question.get("num") != slot["num"]:
                errors.append(f"第 {slot['num']} 题题号不匹配")
            if question.get("type") != slot["type"]:
                errors.append(f"第 {slot['num']} 题题型应为 {slot['type']}")
            if question.get("difficulty") != slot["difficulty"]:
                errors.append(f"第 {slot['num']} 题难度应为 {slot['difficulty']}")
            if question.get("score") != slot["score"]:
                errors.append(f"第 {slot['num']} 题分值应为 {slot['score']}")

            if slot["type"] == "mc":
                errors.extend(
                    f"第 {slot['num']} 题: {item}"
                    for item in self.validate_mc_question(question)["errors"]
                )
            elif slot["type"] == "fill":
                errors.extend(
                    f"第 {slot['num']} 题: {item}"
                    for item in self.validate_fill_question(question)["errors"]
                )
            else:
                errors.extend(
                    f"第 {slot['num']} 题: {item}"
                    for item in self.validate_essay_question(question)["errors"]
                )

            score_total += question.get("score", 0)

        if score_total != 100:
            errors.append("整张试卷总分必须为 100")

        return {"valid": not errors, "errors": errors}

    def grade_mc(self, question: dict, user_answer: str) -> tuple[bool, int]:
        """评分选择题"""
        is_correct = user_answer.strip().upper() == question["correct_answer"]
        return is_correct, question["score"] if is_correct else 0

    def grade_fill(self, question: dict, user_answer: str) -> tuple[float, int]:
        """评分填空题"""
        answer = user_answer.strip().lower()
        correct = question["answer"].lower()
        variants = [v.lower() for v in question.get("acceptable_variants", [])]

        if answer == correct or answer in variants:
            return True, question["score"]

        similarity = self._calculate_similarity(answer, correct)
        if similarity > 0.8:
            return True, question["score"]
        elif similarity > 0.5:
            return False, int(question["score"] * 0.5)

        return False, 0

    def grade_essay(
        self, question: dict, user_answer: str, rubric_scores: dict
    ) -> tuple[int, str]:
        """评分大题"""
        rubric = question["scoring_rubric"]
        total_score = 0
        feedback_parts = []

        for criterion, weight in rubric.items():
            user_score = rubric_scores.get(criterion, 0)
            max_score = weight * 15
            total_score += min(user_score, max_score)

            if user_score < max_score * 0.6:
                feedback_parts.append(f"{criterion}: 需要改进")

        return int(total_score), "; ".join(feedback_parts) if feedback_parts else "优秀"

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """计算字符串相似度"""
        if not s1 or not s2:
            return 0.0

        range_match = re.fullmatch(r"(\d+)\s*[-~到]\s*(\d+)", s2)
        if range_match:
            user_numbers = [part for part in re.split(r"\D+", s1) if part]
            if len(user_numbers) >= 2 and user_numbers[:2] == list(range_match.groups()):
                return 1.0

        set1 = set(s1.split())
        set2 = set(s2.split())

        if not set1 or not set2:
            return 0.0

        intersection = set1 & set2
        union = set1 | set2

        return len(intersection) / len(union) if union else 0.0

    def generate_report(
        self,
        questions: list[dict],
        answers: list[dict],
        scores: list[int],
        username: str,
    ) -> str:
        """生成考试报告"""
        total_score = sum(scores)
        max_score = 100
        percentage = (total_score / max_score) * 100

        mc_scores = sum(s for q, s in zip(questions, scores) if q["type"] == "mc")
        fill_scores = sum(s for q, s in zip(questions, scores) if q["type"] == "fill")
        essay_scores = sum(s for q, s in zip(questions, scores) if q["type"] == "essay")

        report = f"""# 提示词工程考试报告

**考试日期**：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**考生**：{username}
**题目总数**：11题
**总得分**：{total_score}/{max_score}分
**得分率**：{percentage:.1f}%

---

## 综合评价

{self._get_evaluation(total_score)}

---

## 各题得分明细

### 第一部分：选择题（5题，共25分）
"""

        for i, (q, a, s) in enumerate(zip(questions, answers, scores)):
            if q["type"] == "mc":
                report += f"| {q['num']} | {q['difficulty']} | {a.get('answer', 'N/A')} | {q['correct_answer']} | {s}/{q['score']} |\n"

        report += f"\n**选择题得分**：{mc_scores}/25分\n\n"
        report += "### 第二部分：填空题（3题，共30分）\n"

        for i, (q, a, s) in enumerate(zip(questions, answers, scores)):
            if q["type"] == "fill":
                report += f"| {q['num']} | {q['difficulty']} | {a.get('answer', 'N/A')} | {q['answer']} | {s}/{q['score']} |\n"

        report += f"\n**填空题得分**：{fill_scores}/30分\n\n"
        report += "### 第三部分：大题（3题，共45分）\n"

        for i, (q, a, s) in enumerate(zip(questions, answers, scores)):
            if q["type"] == "essay":
                report += f"| {q['num']} | {q['difficulty']} | {s}/{q['score']} | {a.get('feedback', '')} |\n"

        report += f"\n**大题得分**：{essay_scores}/45分\n"

        report_path = (
            self.exam_dir
            / f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{username}-prompt-learning-exam.md"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        return str(report_path)

    def _get_evaluation(self, score: int) -> str:
        """获取严格但尊重学生的评价。"""
        if score >= 90:
            return "这次考试表现扎实，核心技术已经掌握得比较完整。接下来不要停在会做题这一层，建议继续加强复杂场景下的技术组合、自我反思机制和真实任务迁移能力。"
        elif score >= 70:
            return "整体达到合格线，但基础概念和技术组合还不够稳。建议先回看错题对应课程，把“为什么选这个技术、为什么不用别的技术”讲清楚，再继续做中高级题。"
        elif score >= 50:
            return "当前暴露出的主要问题是概念区分不清、应用链路不完整。建议回到基础和中级课程，先把每门课的核心作用、适用场景和边界条件重新梳理一遍，再做针对性练习。"
        else:
            return "当前基础还不够，先不要急着做综合题。建议从前几课重新建立概念框架，每学完一课做一题小练习，重点确认自己能说清“它解决什么问题、何时该用、何时不该用”。"


class ExamService:
    """考试中心持久化与摘要服务。"""

    def __init__(self, workspace_paths: dict[str, Path], state_store: LearningStateStore):
        self.workspace_paths = workspace_paths
        self.state_store = state_store
        self.exam_history_file = workspace_paths["exam_history_file"]
        self.exam_session_file = workspace_paths["exam_session_file"]

    @classmethod
    def from_skill_dir(
        cls, skill_dir: Path, username: str | None = None
    ) -> "ExamService":
        workspace_paths = get_workspace_paths(skill_dir, username=username)
        return cls(
            workspace_paths=workspace_paths,
            state_store=LearningStateStore(workspace_paths),
        )

    def _timestamp(self) -> str:
        return datetime.now().astimezone().isoformat()

    def _append_jsonl(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _read_session(self) -> dict | None:
        if not self.exam_session_file.exists():
            return None
        with open(self.exam_session_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_session(self, payload: dict) -> dict:
        self.exam_session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.exam_session_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return payload

    def _build_question_summary(self, blueprint: dict) -> list[dict]:
        return [
            {
                "num": slot["num"],
                "type": slot["type"],
                "difficulty": slot["difficulty"],
                "goal": slot["goal"],
                "score": slot["score"],
            }
            for slot in blueprint["slots"]
        ]

    def _session_to_context(self, session: dict) -> dict:
        current_num = session["current_question_num"]
        current_slot = session["question_summaries"][current_num - 1]
        total_questions = session["total_questions"]
        return {
            "interaction": {
                "mode": "inform",
            },
            "session_id": session["session_id"],
            "exam_type": session["exam_type"],
            "exam_label": session["exam_label"],
            "status": session["status"],
            "current_question_num": current_num,
            "total_questions": total_questions,
            "remaining_questions": total_questions - current_num + 1,
            "current_slot": current_slot,
        }

    def get_in_progress_session(self) -> dict | None:
        session = self._read_session()
        if not session or session.get("status") != "in_progress":
            return None
        return session

    def get_resume_prompt(self) -> dict:
        session = self.get_in_progress_session()
        if not session:
            return {
                "interaction": {
                    "mode": "inform",
                },
                "has_in_progress": False,
                "session": None,
            }

        return {
            "interaction": {
                "mode": "selector",
            },
            "has_in_progress": True,
            "session": {
                "session_id": session["session_id"],
                "exam_type": session["exam_type"],
                "exam_label": session["exam_label"],
                "current_question_num": session["current_question_num"],
                "total_questions": session["total_questions"],
                "started_at": session["started_at"],
                "updated_at": session["updated_at"],
            },
            "question": {
                "id": "exam-session-resume-selection",
                "header": "未完成考试",
                "question": "检测到未完成的考试，你想怎么处理？",
                "options": [
                    {
                        "label": "恢复考试",
                        "description": "回到当前未完成题，继续逐题作答",
                        "value": "resume",
                    },
                    {
                        "label": "放弃考试",
                        "description": "放弃当前考试会话，不写入正式成绩",
                        "value": "abandon",
                    },
                ],
                "multiple": False,
            },
        }

    def start_session(self, exam_type: str) -> dict:
        existing = self.get_in_progress_session()
        if existing:
            return self.get_resume_prompt()

        engine = ExamEngine()
        blueprint = engine.build_exam_blueprint(exam_type)
        session = {
            "session_id": f"exam-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}",
            "exam_type": exam_type,
            "exam_label": blueprint["exam_label"],
            "status": "in_progress",
            "current_question_num": 1,
            "total_questions": blueprint["total_questions"],
            "started_at": self._timestamp(),
            "updated_at": self._timestamp(),
            "completed_at": None,
            "answers": [],
            "scores": [],
            "question_summaries": self._build_question_summary(blueprint),
        }
        self._write_session(session)
        self.state_store.update_current_state(
            current_module="exam",
            last_action="exam_started",
            recommended_next_action="continue_exam",
        )
        return self._session_to_context(session)

    def get_current_question_context(self, session_id: str | None = None) -> dict:
        session = self.get_in_progress_session()
        if not session:
            raise ValueError("没有进行中的考试会话")
        if session_id and session["session_id"] != session_id:
            raise ValueError("session_id 不匹配")
        return self._session_to_context(session)

    def abandon_session(self, session_id: str | None = None) -> dict:
        session = self.get_in_progress_session()
        if not session:
            raise ValueError("没有进行中的考试会话")
        if session_id and session["session_id"] != session_id:
            raise ValueError("session_id 不匹配")

        session["status"] = "abandoned"
        session["completed_at"] = self._timestamp()
        session["updated_at"] = session["completed_at"]
        self._write_session(session)
        self.state_store.update_current_state(
            current_module="exam",
            last_action="exam_abandoned",
            recommended_next_action="exam_entry",
        )
        return {
            "interaction": {
                "mode": "inform",
            },
            "abandoned": True,
            "session_id": session["session_id"],
            "exam_type": session["exam_type"],
            "status": session["status"],
        }

    def record_history(self, payload: dict) -> dict:
        exam_type = payload.get("exam_type", "diagnostic")
        score = payload.get("score")
        total_score = payload.get("total_score", 100)
        weak_courses = payload.get("weak_courses", [])
        weak_topics = payload.get("weak_topics", [])
        report_path = payload.get("report_path")

        if exam_type not in {"diagnostic", "final"}:
            raise ValueError("exam_type 必须是 diagnostic 或 final")
        if not isinstance(score, int):
            raise ValueError("score 必须是整数")
        if not isinstance(total_score, int):
            raise ValueError("total_score 必须是整数")

        entry = {
            "timestamp": self._timestamp(),
            "exam_type": exam_type,
            "score": score,
            "total_score": total_score,
            "weak_courses": weak_courses,
            "weak_topics": weak_topics,
            "report_path": report_path,
        }
        self._append_jsonl(self.exam_history_file, entry)
        self.state_store.update_current_state(
            current_module="exam",
            last_action="exam_completed",
            recommended_next_action="review_weak_topics",
        )
        return {
            "interaction": {
                "mode": "inform",
            },
            "recorded": True,
            "entry": entry,
        }

    def get_history_summary(self) -> dict:
        if not self.exam_history_file.exists():
            return {
                "interaction": {
                    "mode": "inform",
                },
                "count": 0,
                "latest": None,
                "latest_weak_topics": [],
            }

        with open(self.exam_history_file, "r", encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]

        latest = rows[-1] if rows else None
        return {
            "interaction": {
                "mode": "inform",
            },
            "count": len(rows),
            "latest": latest,
            "latest_weak_topics": latest.get("weak_topics", []) if latest else [],
        }
