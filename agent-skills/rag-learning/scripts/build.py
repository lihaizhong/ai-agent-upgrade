"""
RAG Learning 实战中心。
围绕最小 RAG 项目提供结构化步骤面板。
"""

from __future__ import annotations

from pathlib import Path

if __package__ in {None, ""}:
    from catalog import load_scenarios
    from config import load_build_projects, load_build_step_panels
    from state import RagLearningStateStore
else:
    from .catalog import load_scenarios
    from .config import load_build_projects, load_build_step_panels
    from .state import RagLearningStateStore


class BuildService:
    def __init__(self, skill_dir: Path, username: str | None = None):
        self.skill_dir = skill_dir
        self.state = RagLearningStateStore.from_skill_dir(skill_dir, username=username)
        self.project_config = load_build_projects(skill_dir)
        self.step_panels = load_build_step_panels(skill_dir)
        self.projects = self._load_projects()

    def _load_projects(self) -> list[dict]:
        projects: list[dict] = []
        scenarios_by_project = {
            scenario.get("project_id"): scenario for scenario in load_scenarios(self.skill_dir)
        }
        for project_id, config in self.project_config.items():
            scenario = scenarios_by_project.get(project_id)
            if scenario is None:
                continue
            projects.append(
                {
                    "id": project_id,
                    "name": config["name"],
                    "status": config["status"],
                    "description": config["description"],
                    "scenario_name": scenario["name"],
                    "estimated_time": scenario["estimated_time"],
                    "recommended_start": scenario["recommended_start"],
                }
            )
        return projects

    def _validate_project_id(self, project_id: str) -> None:
        if project_id not in {project["id"] for project in self.projects}:
            raise ValueError(f"Unknown build project: {project_id}")

    def entry_points(self) -> dict:
        return {
            "module": "build",
            "interaction": {"mode": "selector"},
            "question": {
                "header": "Build",
                "question": "你想推进哪一个 RAG 项目？",
                "options": [
                    {
                        "label": project["name"],
                        "description": project["description"],
                        "value": project["id"],
                    }
                    for project in self.projects
                ],
            },
            "projects": self.projects,
        }

    def resume(self) -> dict:
        current_state = self.state.get_current_state()
        build_progress = self.state.get_build_progress()
        project_id = self._active_project_id(
            current_state.get("current_project"), build_progress
        )
        if project_id is None:
            return {
                "module": "build",
                "interaction": {"mode": "inform"},
                "resume_action": "open_build_entry_points",
                "target_module": "build",
                "target_payload": {},
                "reason": "当前没有进行中的 RAG 项目，回到实战入口选择项目。",
                "is_fallback": True,
                "available_projects": self.projects,
            }

        project_progress = build_progress["projects"].get(project_id, {})
        resume_step = self._resume_step(project_progress)
        return {
            "module": "build",
            "interaction": {"mode": "inform"},
            "resume_action": "continue_build",
            "target_module": "build",
            "target_payload": {
                "project_id": project_id,
                "step": resume_step,
                "status": project_progress.get("status"),
                "completed_steps": project_progress.get("completed_steps", []),
            },
            "reason": "当前存在进行中的 RAG 项目，可直接回到当前步骤继续推进。",
            "is_fallback": False,
            "handoff": self.step_panels.get(resume_step, {}).get("handoff", {}),
        }

    def start_project(self, project_id: str) -> dict:
        self._validate_project_id(project_id)
        progress = self.state.start_project(project_id)
        return {
            "module": "build",
            "interaction": {"mode": "inform"},
            "project_id": project_id,
            "progress": progress,
        }

    def step_panel(self, project_id: str, step: str) -> dict:
        self._validate_project_id(project_id)
        if step not in self.step_panels:
            raise ValueError(f"Unknown build step: {step}")
        self.state.start_project(project_id)
        panel = self.step_panels[step]
        return {
            "module": "build",
            "interaction": {"mode": "inform"},
            "project_id": project_id,
            "step": step,
            "current_decision": panel["current_decision"],
            "recommended_solution": panel["recommendation"],
            "tradeoff_reason": panel["tradeoff"],
            "minimum_task": panel["task"],
            "next_step": panel["next_step"],
            "handoff": panel.get("handoff", {}),
        }

    def record_step(self, project_id: str, step: str) -> dict:
        self._validate_project_id(project_id)
        if step not in self.step_panels:
            raise ValueError(f"Unknown build step: {step}")
        panel = self.step_panels[step]
        progress = self.state.record_build_step(
            project_id, step, competency_area=panel["competency_area"]
        )
        return {
            "module": "build",
            "interaction": {"mode": "inform"},
            "project_id": project_id,
            "step": step,
            "status": "recorded",
            "progress": progress,
            "handoff": panel.get("handoff", {}),
        }

    def _active_project_id(
        self, preferred_project: str | None, build_progress: dict
    ) -> str | None:
        projects = build_progress.get("projects", {})
        if preferred_project and projects.get(preferred_project, {}).get("status") == "in_progress":
            return preferred_project
        for project_id, payload in projects.items():
            if payload.get("status") == "in_progress":
                return project_id
        return None

    def _resume_step(self, project_progress: dict) -> str:
        current_step = project_progress.get("current_step") or "scenario"
        completed_steps = set(project_progress.get("completed_steps", []))
        if current_step in completed_steps:
            next_step = self.step_panels.get(current_step, {}).get("next_step")
            if next_step in self.step_panels:
                return next_step
        return current_step
