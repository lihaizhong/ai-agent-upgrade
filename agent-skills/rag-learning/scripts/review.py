"""
RAG Learning 架构评审模块。
提供评审入口、结构化模板、结果记录和历史聚合。
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    from config import load_review_fields, load_review_scenarios
    from state import RagLearningStateStore
    from workspace import get_workspace_paths
else:
    from .config import load_review_fields, load_review_scenarios
    from .state import RagLearningStateStore
    from .workspace import get_workspace_paths


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


class ReviewService:
    def __init__(self, skill_dir: Path, username: str | None = None):
        self.skill_dir = skill_dir
        self.state = RagLearningStateStore.from_skill_dir(skill_dir, username=username)
        self.workspace_paths = get_workspace_paths(skill_dir, username=username)
        self.review_scenarios = load_review_scenarios(skill_dir)
        self.review_fields = load_review_fields(skill_dir)

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
            "module": "review",
            "interaction": {
                "mode": "selector",
                "question": {
                    "header": "Review",
                    "question": "你想发起哪类架构评审？",
                    "options": [
                        {
                            "label": item["label"],
                            "description": item["description"],
                            "value": scenario,
                        }
                        for scenario, item in self.review_scenarios.items()
                    ],
                },
            },
            "scenarios": list(self.review_scenarios.keys()),
        }

    def template(self, scenario: str) -> dict:
        if scenario not in self.review_scenarios:
            raise ValueError(f"Unknown review scenario: {scenario}")
        self.state.update_current_state(
            current_module="review",
            current_review_id=scenario,
            last_action="review_started",
            recommended_next_action="complete_constraints",
        )
        config = self.review_scenarios[scenario]
        return {
            "module": "review",
            "scenario": scenario,
            "label": config["label"],
            "fields": self.review_fields,
            "recommended_stack": config["recommended_stack"],
        }

    def record_summary(
        self,
        *,
        scenario: str,
        constraints_summary: str,
        recommended_stack: dict,
        risk_summary: str,
    ) -> dict:
        if scenario not in self.review_scenarios:
            raise ValueError(f"Unknown review scenario: {scenario}")
        payload = {
            "timestamp": _timestamp(),
            "scenario": scenario,
            "constraints_summary": constraints_summary,
            "recommended_stack": recommended_stack,
            "risk_summary": risk_summary,
        }
        self._append_jsonl(self.workspace_paths["review_history_file"], payload)
        self.state.increment_competency("architecture_review")
        self.state.update_current_state(
            current_module="review",
            current_review_id=scenario,
            last_action="review_completed",
            recommended_next_action="review_profile",
        )
        return {"module": "review", "status": "recorded", "result": payload}

    def history(self) -> dict:
        rows = self._read_jsonl(self.workspace_paths["review_history_file"])
        return {
            "module": "review",
            "count": len(rows),
            "items": list(reversed(rows[-10:])),
        }
