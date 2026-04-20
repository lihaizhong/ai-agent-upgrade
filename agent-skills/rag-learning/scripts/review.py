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
    from profile import ProfileService
    from state import RagLearningStateStore
    from workspace import get_workspace_paths
else:
    from .config import load_review_fields, load_review_scenarios
    from .profile import ProfileService
    from .state import RagLearningStateStore
    from .workspace import get_workspace_paths


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


class ReviewService:
    def __init__(self, skill_dir: Path, username: str | None = None):
        self.skill_dir = skill_dir
        self.username = username
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

    def _recent_experiment_handoff(self, current_project: str | None) -> list[dict]:
        rows = self._read_jsonl(self.workspace_paths["experiment_history_file"])
        if current_project:
            rows = [row for row in rows if row.get("scenario") == current_project]
        return [
            {
                "experiment_id": row.get("experiment_id"),
                "topic": row.get("topic"),
                "summary": row.get("summary"),
                "recommended_choice": row.get("recommended_choice"),
            }
            for row in rows[-3:]
        ]

    def entry_points(self) -> dict:
        current_state = self.state.get_current_state()
        recent_review = self._recent_review(current_state.get("current_review_id"))
        return {
            "module": "review",
            "interaction": {"mode": "selector"},
            "question": {
                "header": "Review",
                "question": "你想如何进入架构评审？",
                "options": [
                    {
                        "label": "新建评审",
                        "description": "从场景模板开始发起新的 RAG 架构评审。",
                        "value": "start_new_review",
                    },
                    {
                        "label": "继续最近评审",
                        "description": self._continue_description(recent_review),
                        "value": "continue_recent_review",
                    },
                    {
                        "label": "查看历史摘要",
                        "description": "查看最近保存的架构评审摘要，快速回顾已有方案。",
                        "value": "view_review_history",
                    },
                ],
            },
            "available_scenarios": [
                {
                    "label": item["label"],
                    "description": item["description"],
                    "value": scenario,
                }
                for scenario, item in self.review_scenarios.items()
            ],
            "scenarios": list(self.review_scenarios.keys()),
            "recent_review": recent_review,
            "history_preview": self.history()["items"][:3],
        }

    def _recent_review(self, current_review_id: str | None) -> dict | None:
        if current_review_id and current_review_id in self.review_scenarios:
            config = self.review_scenarios[current_review_id]
            return {
                "scenario": current_review_id,
                "label": config["label"],
                "source": "current_state",
            }

        rows = self._read_jsonl(self.workspace_paths["review_history_file"])
        if not rows:
            return None
        latest = rows[-1]
        scenario = latest.get("scenario")
        config = self.review_scenarios.get(scenario, {})
        return {
            "scenario": scenario,
            "label": config.get("label", scenario),
            "source": "history",
        }

    def _continue_description(self, recent_review: dict | None) -> str:
        if recent_review is None:
            return "当前暂无最近评审上下文，可先新建一份架构评审。"
        return f"回到最近一次“{recent_review['label']}”评审，继续补充或整理结论。"

    def template(self, scenario: str) -> dict:
        if scenario not in self.review_scenarios:
            raise ValueError(f"Unknown review scenario: {scenario}")
        current_state = self.state.get_current_state()
        current_project = current_state.get("current_project")
        self.state.update_current_state(
            current_module="review",
            current_review_id=scenario,
            last_action="review_started",
            recommended_next_action="complete_constraints",
        )
        config = self.review_scenarios[scenario]
        return {
            "module": "review",
            "interaction": {"mode": "inform"},
            "scenario": scenario,
            "label": config["label"],
            "fields": self.review_fields,
            "recommended_stack": config["recommended_stack"],
            "evidence_handoff": {
                "current_project": current_project,
                "recent_experiments": self._recent_experiment_handoff(current_project),
            },
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
        ProfileService(self.skill_dir, username=self.username).update_preferences()
        return {
            "module": "review",
            "interaction": {"mode": "inform"},
            "status": "recorded",
            "result": payload,
        }

    def history(self) -> dict:
        rows = self._read_jsonl(self.workspace_paths["review_history_file"])
        return {
            "module": "review",
            "interaction": {"mode": "inform"},
            "count": len(rows),
            "items": list(reversed(rows[-10:])),
        }
