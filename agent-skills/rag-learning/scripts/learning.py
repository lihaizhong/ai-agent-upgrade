"""
RAG Learning 学习中心。
围绕课程目录、推荐课程和课程元数据提供结构化输出。
"""

from __future__ import annotations

from pathlib import Path

if __package__ in {None, ""}:
    from catalog import load_course_catalog, load_recommended_paths
    from state import RagLearningStateStore
else:
    from .catalog import load_course_catalog, load_recommended_paths
    from .state import RagLearningStateStore

def get_course_metadata(skill_dir: Path, course_id: int) -> dict | None:
    for item in load_course_catalog(skill_dir):
        if item["id"] == course_id:
            return item
    return None


class LearningService:
    def __init__(self, skill_dir: Path, username: str | None = None):
        self.skill_dir = skill_dir
        self.state = RagLearningStateStore.from_skill_dir(skill_dir, username=username)
        self.course_catalog = load_course_catalog(skill_dir)
        self.recommended_paths = load_recommended_paths(skill_dir)

    def catalog(self) -> dict:
        return {
            "module": "learning",
            "interaction": {"mode": "inform"},
            "tracks": sorted({item["track"] for item in self.course_catalog}),
            "courses": self.course_catalog,
        }

    def path(self, level: str) -> dict:
        course_ids = self.recommended_paths.get(level, [])
        return {
            "module": "learning",
            "interaction": {"mode": "inform"},
            "level": level,
            "courses": [
                get_course_metadata(self.skill_dir, course_id) for course_id in course_ids
            ],
        }

    def recommend_course(self) -> dict:
        progress = self.state.get_course_progress()
        in_progress = progress.get("in_progress_course")
        if in_progress:
            course = get_course_metadata(self.skill_dir, in_progress)
            reason = "已有进行中的课程，优先保持学习连续性。"
        else:
            completed = set(progress.get("completed_courses", []))
            course = next(
                (item for item in self.course_catalog if item["id"] not in completed),
                self.course_catalog[0],
            )
            reason = "推荐第一门未完成课程，优先保持决策顺序。"
        return {
            "module": "learning",
            "interaction": {
                "mode": "open_ended",
                "prompt_hint": "根据推荐课程和原因，用自然语言组织下一步建议。",
            },
            "recommended_course": course,
            "reason": reason,
        }

    def lesson_meta(self, course_id: int) -> dict:
        course = get_course_metadata(self.skill_dir, course_id)
        if course is None:
            raise ValueError(f"Unknown course id: {course_id}")
        self.state.start_course(course_id)
        return {
            "module": "learning",
            "interaction": {"mode": "inform"},
            "course": course,
            "path": str(self.skill_dir / "courses" / course["slug"]),
            "teaching_structure": [
                "一句话理解",
                "这个决策解决什么问题",
                "判断时看哪些约束",
                "常见选项与边界",
                "最小场景例子",
                "企业场景例子",
                "常见误区",
            ],
        }

    def complete_course(self, course_id: int) -> dict:
        course = get_course_metadata(self.skill_dir, course_id)
        if course is None:
            raise ValueError(f"Unknown course id: {course_id}")
        progress = self.state.complete_course(course_id)
        return {
            "module": "learning",
            "interaction": {"mode": "inform"},
            "course": course,
            "status": "completed",
            "progress": progress,
        }
