"""
RAG Learning 平台配置加载。
从 reference/platform-config.json 读取实验与评审配置。
"""

from __future__ import annotations

import json
from pathlib import Path


def load_platform_config(skill_dir: Path) -> dict:
    config_path = skill_dir / "reference" / "platform-config.json"
    return json.loads(config_path.read_text(encoding="utf-8"))


def load_lab_topics(skill_dir: Path) -> dict:
    return load_platform_config(skill_dir).get("lab_topics", {})


def load_review_scenarios(skill_dir: Path) -> dict:
    return load_platform_config(skill_dir).get("review_scenarios", {})


def load_review_fields(skill_dir: Path) -> list[str]:
    return load_platform_config(skill_dir).get("review_fields", [])

