"""
RAG Learning 平台配置加载。
从 reference/platform-config.json 读取 build、实验与评审配置。
"""

from __future__ import annotations

import json
from pathlib import Path


def load_platform_config(skill_dir: Path) -> dict:
    config_path = skill_dir / "reference" / "platform-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    _validate_platform_config(config)
    return config


def _validate_platform_config(config: dict) -> None:
    build_projects = config.get("build_projects", {})
    build_step_panels = config.get("build_step_panels", {})
    lab_topics = config.get("lab_topics", {})
    review_scenarios = config.get("review_scenarios", {})
    review_fields = config.get("review_fields", [])

    if not isinstance(build_projects, dict) or not build_projects:
        raise ValueError("platform-config missing build_projects")
    if not isinstance(build_step_panels, dict) or not build_step_panels:
        raise ValueError("platform-config missing build_step_panels")
    if not isinstance(lab_topics, dict) or not lab_topics:
        raise ValueError("platform-config missing lab_topics")
    if not isinstance(review_scenarios, dict) or not review_scenarios:
        raise ValueError("platform-config missing review_scenarios")
    if not isinstance(review_fields, list) or not review_fields:
        raise ValueError("platform-config missing review_fields")

    step_names = set(build_step_panels.keys())
    valid_competency_areas = {
        "rag_foundations",
        "embedding_selection",
        "vector_db_selection",
        "retrieval_design",
        "rerank_decision",
        "evaluation_design",
        "architecture_review",
    }

    for project_id, project in build_projects.items():
        if "name" not in project or "description" not in project:
            raise ValueError(f"build project '{project_id}' missing required fields")

    for step_name, panel in build_step_panels.items():
        if panel.get("next_step") not in step_names | {"lab"}:
            raise ValueError(
                f"build step '{step_name}' points to unknown next_step '{panel.get('next_step')}'"
            )
        competency_area = panel.get("competency_area")
        if competency_area not in valid_competency_areas:
            raise ValueError(
                f"build step '{step_name}' uses unknown competency_area '{competency_area}'"
            )
        handoff = panel.get("handoff", {})
        topic = handoff.get("recommended_topic")
        if topic is not None and topic not in lab_topics:
            raise ValueError(
                f"build step '{step_name}' references unknown lab topic '{topic}'"
            )
        scenario = handoff.get("recommended_scenario")
        if scenario is not None and scenario not in review_scenarios:
            raise ValueError(
                f"build step '{step_name}' references unknown review scenario '{scenario}'"
            )


def load_build_projects(skill_dir: Path) -> dict:
    return load_platform_config(skill_dir).get("build_projects", {})


def load_build_step_panels(skill_dir: Path) -> dict:
    return load_platform_config(skill_dir).get("build_step_panels", {})


def load_lab_topics(skill_dir: Path) -> dict:
    return load_platform_config(skill_dir).get("lab_topics", {})


def load_review_scenarios(skill_dir: Path) -> dict:
    return load_platform_config(skill_dir).get("review_scenarios", {})


def load_review_fields(skill_dir: Path) -> list[str]:
    return load_platform_config(skill_dir).get("review_fields", [])
