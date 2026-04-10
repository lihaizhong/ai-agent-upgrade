"""
Prompt Learning workspace 管理
负责用户目录解析、路径管理和最小持久化文件初始化。
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


def resolve_git_username() -> str | None:
    """读取 git config user.name，失败时返回 None。"""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    username = result.stdout.strip()
    return username or None


def normalize_workspace_username(raw_name: str | None) -> str:
    """将用户名规范化为 workspace 目录名。"""
    if raw_name and raw_name.strip():
        return raw_name.strip().replace(" ", "-")
    return "default-zoom"


def resolve_workspace_identity(username: str | None = None) -> dict[str, str | None]:
    """解析当前用户对应的 workspace 身份。"""
    explicit_username = username.strip() if username and username.strip() else None
    source_git_username = resolve_git_username()

    allow_override = (
        os.environ.get("PROMPT_LEARNING_ALLOW_USERNAME_OVERRIDE", "").strip().lower()
        in {"1", "true", "yes"}
    )
    if (
        explicit_username is not None
        and source_git_username
        and normalize_workspace_username(explicit_username)
        != normalize_workspace_username(source_git_username)
        and not allow_override
    ):
        raise ValueError(
            "workspace identity mismatch: "
            f"explicit username '{explicit_username}' does not match current git user "
            f"'{source_git_username}'"
        )

    workspace_seed = explicit_username if explicit_username is not None else source_git_username
    workspace_user = normalize_workspace_username(workspace_seed)
    return {
        "explicit_username": explicit_username,
        "source_git_username": source_git_username,
        "workspace_user": workspace_user,
    }


def get_repo_root(skill_dir: Path) -> Path:
    """返回仓库根目录。"""
    resolved = skill_dir.resolve()
    return resolved.parent.parent


def get_workspace_root(skill_dir: Path) -> Path:
    """返回 prompt-learning-workspace 根目录。"""
    return get_repo_root(skill_dir) / "prompt-learning-workspace"


def get_user_workspace(skill_dir: Path, username: str | None = None) -> Path:
    """返回当前用户的 workspace 目录。"""
    workspace_user = resolve_workspace_identity(username)["workspace_user"]
    return get_workspace_root(skill_dir) / workspace_user


def get_workspace_paths(
    skill_dir: Path, username: str | None = None
) -> dict[str, Path]:
    """返回当前用户 workspace 关键路径。"""
    user_workspace = get_user_workspace(skill_dir, username=username)
    profile_dir = user_workspace / "profile"
    progress_dir = user_workspace / "progress"
    practice_dir = user_workspace / "practice"
    exam_dir = user_workspace / "exam"
    exam_reports_dir = exam_dir / "reports"
    lab_dir = user_workspace / "prompt-lab"
    lab_templates_dir = lab_dir / "templates"

    return {
        "workspace_root": user_workspace,
        "profile_dir": profile_dir,
        "progress_dir": progress_dir,
        "practice_dir": practice_dir,
        "exam_dir": exam_dir,
        "exam_reports_dir": exam_reports_dir,
        "lab_dir": lab_dir,
        "lab_templates_dir": lab_templates_dir,
        "learner_file": profile_dir / "learner.json",
        "preferences_file": profile_dir / "preferences.json",
        "current_state_file": progress_dir / "current-state.json",
        "course_progress_file": progress_dir / "course-progress.json",
        "mastery_file": progress_dir / "mastery.json",
        "practice_history_file": practice_dir / "practice-history.jsonl",
        "mistakes_file": practice_dir / "mistakes.jsonl",
        "exam_history_file": exam_dir / "exam-history.jsonl",
        "exam_session_file": exam_dir / "current-session.json",
        "template_index_file": lab_dir / "template-index.json",
    }


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def _write_json_if_missing(path: Path, payload: dict) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _workspace_has_state(paths: dict[str, Path]) -> bool:
    state_files = [
        paths["preferences_file"],
        paths["current_state_file"],
        paths["course_progress_file"],
        paths["mastery_file"],
        paths["practice_history_file"],
        paths["mistakes_file"],
        paths["exam_history_file"],
        paths["exam_session_file"],
        paths["template_index_file"],
    ]
    return any(path.exists() for path in state_files)


def _default_learner(source_git_username: str | None, workspace_user: str) -> dict:
    now = _timestamp()
    return {
        "workspace_user": workspace_user,
        "source_git_username": source_git_username,
        "created_at": now,
        "updated_at": now,
    }


def _default_preferences() -> dict:
    return {
        "use_question_tool": True,
        "preferred_module": "learning",
        "preferred_difficulty": "auto",
        "language": "zh-CN",
        "updated_at": _timestamp(),
    }


def _default_current_state() -> dict:
    return {
        "current_module": "home",
        "current_course_id": None,
        "current_course_name": None,
        "last_action": "workspace_initialized",
        "recommended_next_action": "open_dashboard",
        "updated_at": _timestamp(),
    }


def _default_course_progress() -> dict:
    return {
        "completed_courses": [],
        "in_progress_course": None,
        "last_completed_course": None,
        "course_status": {},
        "updated_at": _timestamp(),
    }


def _default_mastery() -> dict:
    return {
        "courses": {},
        "updated_at": _timestamp(),
    }


def _default_template_index() -> dict:
    return {
        "templates": [],
        "updated_at": _timestamp(),
    }


def ensure_workspace(skill_dir: Path, username: str | None = None) -> dict:
    """初始化 workspace 目录和最小文件集。"""
    identity = resolve_workspace_identity(username)
    source_git_username = identity["source_git_username"]
    workspace_user = identity["workspace_user"]
    paths = get_workspace_paths(skill_dir, username=username)

    learner_file = paths["learner_file"]
    if not learner_file.exists() and _workspace_has_state(paths):
        raise ValueError(
            "workspace metadata missing: "
            f"target workspace '{workspace_user}' already has state files but no learner.json"
        )
    if learner_file.exists():
        learner = _read_json(learner_file)
        existing_workspace_user = learner.get("workspace_user")
        if (
            isinstance(existing_workspace_user, str)
            and existing_workspace_user
            and existing_workspace_user != workspace_user
        ):
            raise ValueError(
                "workspace ownership mismatch: "
                f"current user resolves to '{workspace_user}', "
                f"but target workspace metadata belongs to '{existing_workspace_user}'"
            )

    created_dirs = []
    created_files = []
    directory_keys = [
        "workspace_root",
        "profile_dir",
        "progress_dir",
        "practice_dir",
        "exam_dir",
        "exam_reports_dir",
        "lab_dir",
        "lab_templates_dir",
    ]
    for key in directory_keys:
        directory = paths[key]
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        if not existed:
            created_dirs.append(str(directory))

    file_definitions = {
        "learner_file": _default_learner(source_git_username, workspace_user),
        "preferences_file": _default_preferences(),
        "current_state_file": _default_current_state(),
        "course_progress_file": _default_course_progress(),
        "mastery_file": _default_mastery(),
        "template_index_file": _default_template_index(),
    }
    for key, payload in file_definitions.items():
        path = paths[key]
        if _write_json_if_missing(path, payload):
            created_files.append(str(path))

    return {
        "source_git_username": source_git_username,
        "workspace_user": workspace_user,
        "workspace_root": str(paths["workspace_root"]),
        "created": bool(created_dirs or created_files),
        "created_dirs": created_dirs,
        "created_files": created_files,
        "paths": {
            key: str(value)
            for key, value in paths.items()
            if key.endswith("_dir") or key == "workspace_root"
        },
    }
