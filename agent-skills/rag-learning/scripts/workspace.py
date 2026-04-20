"""
RAG Learning workspace 管理。
负责用户目录解析、路径管理和最小持久化文件初始化。
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


DEFAULT_WORKSPACE_USERNAME = "default-zoom"


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
    if not raw_name or not raw_name.strip():
        return DEFAULT_WORKSPACE_USERNAME

    candidate = raw_name.strip().replace(" ", "-")
    candidate = re.sub(r"[^\w.-]", "-", candidate, flags=re.UNICODE)
    candidate = re.sub(r"-{2,}", "-", candidate)
    candidate = candidate.strip("._-")
    if candidate in {"", ".", ".."}:
        return DEFAULT_WORKSPACE_USERNAME
    return candidate


def resolve_workspace_identity(username: str | None = None) -> dict[str, str | bool | None]:
    """解析当前用户对应的 workspace 身份。"""
    explicit_username = username.strip() if username and username.strip() else None
    source_git_username = resolve_git_username()
    workspace_seed = (
        explicit_username if explicit_username is not None else source_git_username
    )
    workspace_user = normalize_workspace_username(workspace_seed)
    return {
        "explicit_username": explicit_username,
        "source_git_username": source_git_username,
        "workspace_user": workspace_user,
        "using_fallback": workspace_seed is None,
    }


def get_repo_root(skill_dir: Path) -> Path:
    """返回仓库根目录。"""
    candidates = [skill_dir.resolve(), Path(__file__).resolve()]
    for candidate in candidates:
        for parent in [candidate, *candidate.parents]:
            if (parent / "AGENTS.md").exists() and (parent / "agent-skills").exists():
                return parent
    raise ValueError(f"Cannot resolve repo root from skill directory: {skill_dir}")


def get_workspace_root(skill_dir: Path) -> Path:
    """返回 rag-learning-workspace 根目录。"""
    return get_repo_root(skill_dir) / "rag-learning-workspace"


def get_user_workspace(skill_dir: Path, username: str | None = None) -> Path:
    """返回当前用户的 workspace 目录。"""
    workspace_root = get_workspace_root(skill_dir).resolve()
    workspace_user = resolve_workspace_identity(username)["workspace_user"]
    if not isinstance(workspace_user, str):
        raise ValueError("workspace identity did not resolve to a valid user")
    candidate = (workspace_root / workspace_user).resolve()
    try:
        candidate.relative_to(workspace_root)
    except ValueError as exc:
        raise ValueError(
            f"workspace path escapes root: user '{workspace_user}' resolved outside workspace root"
        ) from exc
    return candidate


def get_workspace_paths(skill_dir: Path, username: str | None = None) -> dict[str, Path]:
    """返回当前用户 workspace 关键路径。"""
    user_workspace = get_user_workspace(skill_dir, username=username)
    profile_dir = user_workspace / "profile"
    progress_dir = user_workspace / "progress"
    lab_dir = user_workspace / "lab"
    review_dir = user_workspace / "review"
    review_drafts_dir = review_dir / "drafts"

    return {
        "workspace_root": user_workspace,
        "profile_dir": profile_dir,
        "progress_dir": progress_dir,
        "lab_dir": lab_dir,
        "review_dir": review_dir,
        "review_drafts_dir": review_drafts_dir,
        "learner_file": profile_dir / "learner.json",
        "preferences_file": profile_dir / "preferences.json",
        "current_state_file": progress_dir / "current-state.json",
        "course_progress_file": progress_dir / "course-progress.json",
        "build_progress_file": progress_dir / "build-progress.json",
        "competency_file": progress_dir / "competency.json",
        "experiment_history_file": lab_dir / "experiment-history.jsonl",
        "review_history_file": review_dir / "review-history.jsonl",
    }


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def _write_json_if_missing(path: Path, payload: dict) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def _touch_if_missing(path: Path) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return True


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _workspace_has_state(paths: dict[str, Path]) -> bool:
    state_paths = [
        paths["profile_dir"],
        paths["progress_dir"],
        paths["lab_dir"],
        paths["review_dir"],
    ]
    for path in state_paths:
        if not path.exists():
            continue
        if path.is_file():
            return True
        if any(path.iterdir()):
            return True
    return False


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
        "stable_preferences": {},
        "evidence_summary": {"lab": 0, "review": 0},
        "updated_at": _timestamp(),
    }


def _default_current_state() -> dict:
    return {
        "current_module": "home",
        "current_course_id": None,
        "current_project": None,
        "current_lab_topic": None,
        "current_review_id": None,
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


def _default_build_progress() -> dict:
    return {
        "projects": {},
        "updated_at": _timestamp(),
    }


def _default_competency() -> dict:
    return {
        "areas": {
            "rag_foundations": {"level": "new", "evidence_count": 0},
            "embedding_selection": {"level": "new", "evidence_count": 0},
            "vector_db_selection": {"level": "new", "evidence_count": 0},
            "retrieval_design": {"level": "new", "evidence_count": 0},
            "rerank_decision": {"level": "new", "evidence_count": 0},
            "evaluation_design": {"level": "new", "evidence_count": 0},
            "architecture_review": {"level": "new", "evidence_count": 0},
        },
        "updated_at": _timestamp(),
    }


def ensure_workspace(skill_dir: Path, username: str | None = None) -> dict:
    """初始化 workspace 目录和最小文件集。"""
    identity = resolve_workspace_identity(username)
    source_git_username = identity["source_git_username"]
    workspace_user = identity["workspace_user"]
    if not isinstance(workspace_user, str):
        raise ValueError("workspace identity did not resolve to a valid user")
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
        "lab_dir",
        "review_dir",
        "review_drafts_dir",
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
        "build_progress_file": _default_build_progress(),
        "competency_file": _default_competency(),
    }
    for key, payload in file_definitions.items():
        path = paths[key]
        if _write_json_if_missing(path, payload):
            created_files.append(str(path))

    for key in ["experiment_history_file", "review_history_file"]:
        if _touch_if_missing(paths[key]):
            created_files.append(str(paths[key]))

    return {
        "explicit_username": identity["explicit_username"],
        "source_git_username": source_git_username,
        "workspace_user": workspace_user,
        "using_fallback": identity["using_fallback"],
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
