"""
RAG Learning 统一目录解析。
从 reference/catalog.md 提取课程、路径和场景元数据。
"""

from __future__ import annotations

import re
from pathlib import Path


COURSE_TABLE_HEADER = "| 编号 | 课程 | 难度 | 预计时长 | 适用人群 |"
SCENARIO_TABLE_HEADER = "| 编号 | 场景 | 难度 | 预计时间 | 推荐起点 |"

COURSE_TRACK_NAMES = {
    "基础理解": "foundations",
    "组件选型": "selection",
    "第一个项目": "practice",
    "场景扩展": "practice",
    "企业与线上": "advanced",
}

PROJECT_ID_MAP = {
    "文档问答系统": "local-minimum-rag",
    "客服机器人": "customer-support-rag",
    "企业知识库搜索": "enterprise-knowledge-search",
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _lines(path: Path) -> list[str]:
    return _read_text(path).splitlines()


def _extract_table(lines: list[str], header: str) -> list[list[str]]:
    try:
        start = lines.index(header)
    except ValueError:
        return []

    rows: list[list[str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


def _extract_learning_tracks(lines: list[str]) -> dict[int, str]:
    tracks: dict[int, str] = {}
    in_section = False
    current_track = None

    for raw_line in lines:
        line = raw_line.strip()
        if line == "## 学习中心主线":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        match = re.match(r"\d+\.\s+`([^`]+)`", line)
        if match:
            current_track = COURSE_TRACK_NAMES.get(match.group(1))
            continue
        if current_track:
            tokens = re.findall(r"\b\d{2}\b|\b\d\b", line)
            for token in tokens:
                tracks[int(token)] = current_track
    return tracks


def _extract_recommended_paths(lines: list[str]) -> dict[str, list[int]]:
    in_section = False
    paths: dict[str, list[int]] = {}
    current_key = None

    label_map = {
        "零基础": "novice",
        "已了解基本概念，准备做项目": "intermediate",
        "已做过简单 RAG，准备进阶": "advanced",
        "需要企业级设计": "enterprise",
    }

    for raw_line in lines:
        line = raw_line.strip()
        if line == "## 推荐学习起点":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        if line.startswith("- ") and line.endswith("："):
            label = line[2:-1]
            current_key = label_map.get(label)
            if current_key:
                paths[current_key] = []
            continue
        if current_key and line:
            ids = [int(token) for token in re.findall(r"\b\d{2}\b|\b\d\b", line)]
            paths[current_key].extend(ids)
            paths[current_key] = list(dict.fromkeys(paths[current_key]))
    return paths


def _duration_to_minutes(raw: str) -> int:
    match = re.search(r"(\d+)", raw)
    return int(match.group(1)) if match else 0


def _difficulty_to_code(raw: str) -> str:
    count = raw.count("⭐")
    return f"star-{count}" if count else "unknown"


def _slug_map(skill_dir: Path) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for path in (skill_dir / "courses").glob("*.md"):
        match = re.match(r"(\d+)-", path.name)
        if match:
            mapping[int(match.group(1))] = path.name
    return mapping


def load_course_catalog(skill_dir: Path) -> list[dict]:
    lines = _lines(skill_dir / "reference" / "catalog.md")
    rows = _extract_table(lines, COURSE_TABLE_HEADER)
    tracks = _extract_learning_tracks(lines)
    slug_mapping = _slug_map(skill_dir)
    courses: list[dict] = []
    for row in rows:
        if len(row) < 5:
            continue
        course_id = int(row[0])
        courses.append(
            {
                "id": course_id,
                "name": row[1],
                "slug": slug_mapping.get(course_id, ""),
                "difficulty": _difficulty_to_code(row[2]),
                "duration_minutes": _duration_to_minutes(row[3]),
                "audience": row[4],
                "track": tracks.get(course_id, "unassigned"),
            }
        )
    return courses


def load_recommended_paths(skill_dir: Path) -> dict[str, list[int]]:
    return _extract_recommended_paths(_lines(skill_dir / "reference" / "catalog.md"))


def load_scenarios(skill_dir: Path) -> list[dict]:
    lines = _lines(skill_dir / "reference" / "catalog.md")
    rows = _extract_table(lines, SCENARIO_TABLE_HEADER)
    scenarios: list[dict] = []
    for row in rows:
        if len(row) < 5:
            continue
        scenario_name = row[1]
        scenarios.append(
            {
                "id": int(row[0]),
                "name": scenario_name,
                "project_id": PROJECT_ID_MAP.get(scenario_name),
                "difficulty": row[2],
                "estimated_time": row[3],
                "recommended_start": row[4],
            }
        )
    return scenarios
