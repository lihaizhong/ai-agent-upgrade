"""
RAG Learning 实验室模块。
提供实验入口、固定蓝图、结果记录和历史聚合。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    from config import load_lab_topics
    from state import RagLearningStateStore
    from workspace import get_workspace_paths
else:
    from .config import load_lab_topics
    from .state import RagLearningStateStore
    from .workspace import get_workspace_paths


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


class LabService:
    def __init__(self, skill_dir: Path, username: str | None = None):
        self.skill_dir = skill_dir
        self.state = RagLearningStateStore.from_skill_dir(skill_dir, username=username)
        self.workspace_paths = get_workspace_paths(skill_dir, username=username)
        self.lab_topics = load_lab_topics(skill_dir)

    def _read_jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def _append_jsonl(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

    def entry_points(self) -> dict:
        return {
            "module": "lab",
            "interaction": {
                "mode": "selector",
                "question": {
                    "header": "RAG Lab",
                    "question": "你想做哪类实验？",
                    "options": [
                        {
                            "label": config["label"],
                            "description": config["goal"],
                            "value": topic,
                        }
                        for topic, config in self.lab_topics.items()
                    ],
                },
            },
            "topics": list(self.lab_topics.keys()),
        }

    def blueprint(self, topic: str) -> dict:
        if topic not in self.lab_topics:
            raise ValueError(f"Unknown lab topic: {topic}")
        config = self.lab_topics[topic]
        current_state = self.state.get_current_state()
        self.state.update_current_state(
            current_module="lab",
            current_project=current_state.get("current_project"),
            current_lab_topic=topic,
            last_action="experiment_started",
            recommended_next_action=config["recommended_next_action"],
        )
        return {
            "module": "lab",
            "topic": topic,
            "goal": config["goal"],
            "variables": config["variables"],
            "fixed_conditions": config["fixed_conditions"],
            "metrics": config["metrics"],
            "output_fields": config["output_fields"],
            "default_variants": config["default_variants"],
            "current_project": current_state.get("current_project"),
        }

    def record_result(
        self,
        *,
        topic: str,
        summary: str,
        recommended_choice: str,
        tradeoff_note: str,
        variants: list[str] | None = None,
        metric_focus: list[str] | None = None,
    ) -> dict:
        if topic not in self.lab_topics:
            raise ValueError(f"Unknown lab topic: {topic}")
        config = self.lab_topics[topic]
        current_state = self.state.get_current_state()
        payload = {
            "timestamp": _timestamp(),
            "topic": topic,
            "scenario": current_state.get("current_project"),
            "variants": variants or config["default_variants"],
            "metric_focus": metric_focus or config["metrics"],
            "summary": summary,
            "recommended_choice": recommended_choice,
            "tradeoff_note": tradeoff_note,
        }
        self._append_jsonl(self.workspace_paths["experiment_history_file"], payload)
        self.state.increment_competency(config["competency_area"])
        self.state.update_current_state(
            current_module="lab",
            current_project=current_state.get("current_project"),
            current_lab_topic=topic,
            last_action="experiment_completed",
            recommended_next_action=config["recommended_next_action"],
        )
        return {"module": "lab", "status": "recorded", "result": payload}

    def history(self) -> dict:
        rows = self._read_jsonl(self.workspace_paths["experiment_history_file"])
        return {
            "module": "lab",
            "count": len(rows),
            "items": list(reversed(rows[-10:])),
        }
