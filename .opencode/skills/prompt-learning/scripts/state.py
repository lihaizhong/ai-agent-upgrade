"""
提示词工程学习系统 - 核心状态管理
管理用户学习进度、考试状态、会话配置
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


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
        """获取下一门课程的索引"""
        completed = self.state["completed_courses"]
        if not completed:
            return 0
        last_idx = max(int(c.split("-")[0]) - 1 for c in completed)
        if last_idx < 16:
            return last_idx + 1
        return None

    def get_recommended_path(self) -> dict:
        """获取推荐学习路径"""
        completed = self.state["completed_courses"]
        if not completed:
            return {
                "recommendation": "建议从 01-零样本提示 开始",
                "next_course": 0,
                "category": "基础",
            }

        last_completed = max(int(c.split("-")[0]) for c in completed)

        courses_by_category = {
            "基础": [1, 2],
            "推理": [3, 4, 5],
            "知识": [6, 7, 8],
            "工具": [9, 10, 11],
            "优化": [12, 13, 14],
            "前沿": [15, 16, 17],
        }

        current_category = None
        for cat, courses in courses_by_category.items():
            if last_completed in courses:
                current_category = cat
                break

        next_course = last_completed + 1 if last_completed < 17 else None

        return {
            "completed_count": len(completed),
            "last_completed": last_completed,
            "current_category": current_category,
            "next_course": next_course,
            "next_category": self._get_category_for_course(next_course)
            if next_course
            else None,
        }

    @staticmethod
    def _get_category_for_course(course_num: int) -> Optional[str]:
        """获取课程所属类别"""
        categories = {
            "基础": [1, 2],
            "推理": [3, 4, 5],
            "知识": [6, 7, 8],
            "工具": [9, 10, 11],
            "优化": [12, 13, 14],
            "前沿": [15, 16, 17],
        }
        for cat, courses in categories.items():
            if course_num in courses:
                return cat
        return None
